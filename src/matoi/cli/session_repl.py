"""Interactive REPL session for Matoi.

Flow:
1. Pick PM (or use saved)
2. Describe your goal
3. PM recommends team
4. REPL: user types tasks, agents respond (streaming + markdown)
5. /commit -> debate on changes -> commit -> update graph -> show cost
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from matoi.agents.registry import AgentRegistry
from matoi.cli.common import get_package_root, get_registry, load_avatar
from matoi.cli.tui import MatoiPrompt
from matoi.core.agent import AgentDefinition
from matoi.core.config import (
    GlobalConfig,
    ProjectConfig,
    ensure_project_structure,
    get_project_dir,
    load_global_config,
    load_project_config,
    require_api_key,
    save_global_config,
    save_project_config,
)
from matoi.core.cost import Budget
from matoi.core.team import TeamConfig
from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import MODEL_MAP, ModelRouter
from matoi.storage.costs import CostTracker
from matoi.storage.memory import MemoryStore

console = Console()

COMMANDS = {
    "/help": "Show available commands",
    "/team": "Show current team",
    "/agents": "Show all available agents",
    "/cost": "Show session cost so far",
    "/history": "Show tasks run in this session",
    "/standup": "Generate session summary",
    "/execute": "PM breaks task into subtasks, agents execute",
    "/commit": "Review changes, debate, commit",
    "/key": "Change API key",
    "/quit": "End session (Ctrl+D)",
}


class Session:
    """An interactive Matoi session."""

    def __init__(self) -> None:
        self.registry = get_registry()
        self.provider: AnthropicProvider | None = None
        self.router = ModelRouter()
        self.cost_tracker = CostTracker(Budget(max_total_usd=10.0))
        self.pm: AgentDefinition | None = None
        self.agents: list[AgentDefinition] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history: list[dict] = []
        self.memory: MemoryStore | None = None
        self.prompt: MatoiPrompt | None = None

    def start(self) -> None:
        """Main entry point for interactive session."""
        console.print()
        try:
            import pyfiglet
            banner = pyfiglet.figlet_format("MATOI", font="block")
            console.print(f"[bold cyan]{banner}[/bold cyan]", highlight=False)
        except ImportError:
            console.print("[bold cyan]MATOI[/bold cyan]")
        console.print("  [dim]Your startup team in the terminal.[/dim]")
        console.print("  [dim]/help for commands, /commit before committing, /quit to exit.[/dim]")
        console.print()

        # ── Ensure API key ──
        self._ensure_api_key()
        self.provider = AnthropicProvider()

        # ── Ensure project initialized ──
        project_dir = get_project_dir()
        if not (project_dir / "config.json").exists():
            ensure_project_structure()

        # ── Setup memory ──
        self.memory = MemoryStore(project_dir)

        # ── Pick PM ──
        project_config = load_project_config()
        if project_config and project_config.pm:
            self.pm = self.registry.get(project_config.pm)
            if self.pm:
                self._show_pm_avatar()
            else:
                self._pick_pm()
        else:
            self._pick_pm()

        # ── Initialize TUI prompt ──
        agent_slugs = [a.slug for a in self.registry.list_all()]
        self.prompt = MatoiPrompt(
            project_name=Path.cwd().name,
            pm_name=self.pm.name if self.pm else "",
            agent_slugs=agent_slugs,
        )

        # ── Describe goal -> assemble team ──
        console.print()
        goal = self.prompt.ask_initial("What are you working on today?")
        console.print()

        if goal.strip():
            import questionary
            choice = questionary.select(
                "Assemble team:",
                choices=[
                    questionary.Choice("Auto -- PM recommends team", value="auto"),
                    questionary.Choice("Manual -- pick agents yourself", value="manual"),
                ],
            ).ask()
            if choice == "manual":
                self._manual_team_selection()
            else:
                self._recommend_team(goal)

        if self.prompt:
            self.prompt.update_status(
                team_size=len(self.agents),
                pm_name=self.pm.name if self.pm else "",
            )

        # ── REPL loop ──
        self._repl(goal)

    def _ensure_api_key(self) -> None:
        """Check API key, prompt if missing or invalid."""
        key = require_api_key()

        if key:
            # Validate the key with a cheap test call
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=key)
                client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1,
                    messages=[{"role": "user", "content": "hi"}],
                )
                console.print("  [dim]API key: ok[/dim]")
                return
            except anthropic.AuthenticationError:
                console.print("  [yellow]API key is invalid or expired.[/yellow]\n")
                key = ""
            except Exception:
                # Network error etc -- assume key is ok, will fail later if not
                console.print("  [dim]API key: found (not verified)[/dim]")
                return

        # Ask for key
        console.print("  Get your key at: https://console.anthropic.com/settings/keys\n")
        key = Prompt.ask("  API Key", password=True)
        if not key.strip():
            console.print("[red]API key is required.[/red]")
            raise SystemExit(1)
        config = load_global_config()
        config.anthropic_api_key = key.strip()
        save_global_config(config)
        os.environ["ANTHROPIC_API_KEY"] = key.strip()
        console.print("  [green]Saved.[/green]\n")

    def _pick_pm(self) -> None:
        """Interactive PM selection with arrow-key menu."""
        import questionary

        coordinators = self.registry.list_by_type("coordinator")
        if not coordinators:
            console.print("[red]No PM agents found.[/red]")
            raise SystemExit(1)

        choices = [
            questionary.Choice(
                title=f'{pm.name} -- "{pm.motto}"',
                value=pm.slug,
            )
            for pm in coordinators
        ]

        slug = questionary.select(
            "Select your PM:",
            choices=choices,
            style=questionary.Style([
                ("highlighted", "bold"),
                ("selected", "bold fg:cyan"),
                ("pointer", "bold fg:cyan"),
            ]),
        ).ask()

        if slug is None:
            raise SystemExit(0)

        self.pm = self.registry.get(slug)
        self._show_pm_avatar()

    def _show_pm_avatar(self) -> None:
        """Show selected PM with inline image or text fallback."""
        if not self.pm:
            return
        from matoi.cli.common import display_avatar
        console.print()
        display_avatar(self.pm.slug, width=8)
        console.print(f"  [bold]{self.pm.name}[/bold] -- \"{self.pm.motto}\"")

    def _manual_team_selection(self) -> None:
        """Let user pick agents with checkbox menu."""
        import questionary

        all_agents = [a for a in self.registry.list_all() if a.agent_type.value != "coordinator"]

        TYPE_LABELS = {"executor": "EXE", "thinker": "THK", "critic": "CRT"}

        choices = [
            questionary.Choice(
                title=f'[{TYPE_LABELS.get(a.agent_type.value, "?")}] {a.name} ({a.category.value})',
                value=a.slug,
            )
            for a in all_agents
        ]

        selected = questionary.checkbox(
            "Select agents (space to toggle, enter to confirm, max 4):",
            choices=choices,
            validate=lambda x: len(x) <= 4 or "Maximum 4 agents",
        ).ask()

        if not selected:
            console.print("  [dim]No agents selected, using defaults.[/dim]")
            self.agents = list(all_agents[:3])
            return

        self.agents = []
        for slug in selected[:4]:
            agent = self.registry.get(slug)
            if agent:
                self.agents.append(agent)

        names = ", ".join(f"[bold]{a.name}[/bold]" for a in self.agents)
        console.print(f"\n  Team: {names}")

        pc = load_project_config() or ProjectConfig()
        pc.pm = self.pm.slug if self.pm else ""
        pc.agents = [a.slug for a in self.agents]
        pc.project_name = pc.project_name or Path.cwd().name
        save_project_config(pc)

    def _recommend_team(self, goal: str) -> None:
        """PM recommends team composition based on the goal."""
        if not self.pm or not self.provider:
            return

        all_agents = [a for a in self.registry.list_all() if a.agent_type.value != "coordinator"]

        agents_desc = ""
        for i, a in enumerate(all_agents):
            agents_desc += f"{i + 1}. {a.slug}: {a.name} ({a.role}) -- {a.motto}\n"

        system = (
            f"You are {self.pm.name}. {self.pm.motto}\n"
            "The user described their goal. Recommend 2-4 agents from the list.\n"
            "Return ONLY a JSON array of agent slugs.\n"
            f"Example: [\"backend-engineer\", \"market-researcher\"]\n\n"
            f"Available agents:\n{agents_desc}"
        )

        model_id = MODEL_MAP[self.pm.model_policy.brief]

        try:
            from alive_progress import alive_bar
            with alive_bar(title=f"  {self.pm.name} assembling team", bar=False, spinner="dots_waves"):
                text, cost = self.provider.call(model_id, system, goal, max_tokens=200)
            cost.agent_slug = self.pm.slug
            cost.stage = "team_recommend"
            self.cost_tracker.record(cost)

            # Parse response
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            slugs = json.loads(text)

            self.agents = []
            for slug in slugs:
                agent = self.registry.get(slug)
                if agent:
                    self.agents.append(agent)

            if self.agents:
                names = ", ".join(f"[bold]{a.name}[/bold]" for a in self.agents)
                console.print(f"\n  Team: {names}")

                # Save to project config
                pc = load_project_config() or ProjectConfig()
                pc.pm = self.pm.slug
                pc.agents = [a.slug for a in self.agents]
                pc.project_name = pc.project_name or Path.cwd().name
                save_project_config(pc)
            else:
                console.print("  [dim]Could not parse team recommendation, using all agents.[/dim]")
                self.agents = all_agents[:4]

        except Exception:
            console.print("  [dim]Team recommendation failed, using defaults.[/dim]")
            self.agents = all_agents[:3]

    def _repl(self, initial_goal: str = "") -> None:
        """Main REPL loop with prompt_toolkit."""
        console.print()
        console.rule("[dim]Session started[/dim]")
        console.print()

        while True:
            user_input = self.prompt.ask()

            if user_input is None:  # Ctrl+D
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            # ── Exit without slash ──
            if user_input.lower() in ("exit", "quit", "q"):
                break

            # ── Commands ──
            if user_input.startswith("/"):
                cmd = user_input.split()[0].lower()
                if cmd in ("/quit", "/exit"):
                    break
                elif cmd == "/help":
                    self._show_help()
                elif cmd == "/team":
                    self._show_team()
                elif cmd == "/cost":
                    self._show_cost()
                elif cmd == "/commit":
                    self._commit_flow()
                elif cmd == "/agents":
                    self._show_agents()
                elif cmd == "/history":
                    self._show_history()
                elif cmd == "/standup":
                    self._generate_standup()
                elif cmd == "/execute":
                    rest = user_input[len("/execute"):].strip()
                    if rest:
                        self._execute_task(rest)
                    else:
                        console.print("  [dim]Usage: /execute <task description>[/dim]")
                elif cmd == "/key":
                    self._change_key()
                else:
                    console.print(f"  [dim]Unknown: {cmd}. Type /help[/dim]")
                continue

            # ── Run task ──
            self.prompt.set_working(True)
            try:
                self._run_task(user_input)
            except Exception as e:
                error_name = type(e).__name__
                console.print(f"\n  [red]{error_name}: {e}[/red]\n")
            finally:
                self.prompt.set_working(False)

            # Update status bar
            if self.prompt:
                summary = self.cost_tracker.summary()
                self.prompt.update_status(
                    cost_usd=summary["total_cost_usd"],
                    total_tokens=summary.get("total_tokens", 0),
                )

        # ── Session end ──
        console.print()
        if self.history and self.pm and self.provider:
            self._generate_standup()
        self._show_cost()
        console.print("[dim]Session ended.[/dim]\n")

    def _run_task(self, task: str) -> None:
        """Run a task through the pipeline (brief → expert → synthesis)."""
        if not self.pm or not self.provider:
            return

        console.print()

        # Memory context
        memory_context = ""
        if self.memory:
            memory_context = self.memory.get_context(task)

        # Brief
        console.rule(f"[bold cyan]{self.pm.name} -- brief[/bold cyan]")
        brief = self._call_agent(self.pm, "brief",
            f"Create a brief for this task:\n{task}"
            + (f"\n\n{memory_context}" if memory_context else ""),
        )

        # Expert pass
        opinions: dict[str, str] = {}
        for agent in self.agents:
            if self.cost_tracker.is_over_budget():
                console.print("[yellow]Budget limit reached.[/yellow]")
                break
            console.rule(f"[dim]{agent.name}[/dim]")
            opinion = self._call_agent(agent, "expert_pass",
                f"## Task\n{task}\n\n## Brief\n{brief}",
            )
            opinions[agent.slug] = opinion

        # Synthesis
        opinions_text = ""
        for slug, opinion in opinions.items():
            a = self.registry.get(slug)
            name = a.name if a else slug
            opinions_text += f"\n### {name}\n{opinion}\n"

        console.rule(f"[bold green]{self.pm.name} -- synthesis[/bold green]")
        decision = self._call_agent(self.pm, "synthesis",
            f"## Task\n{task}\n\n## Brief\n{brief}\n\n## Opinions\n{opinions_text}\n\n"
            "Synthesize a decision: what to do, why, risks, next steps.",
        )

        # Save to history
        self.history.append({
            "task": task,
            "brief": brief,
            "opinions": opinions,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
        })

        console.print()

    def _call_agent(self, agent: AgentDefinition, stage: str, user_msg: str) -> str:
        """Call an agent with live markdown rendering."""
        from rich.live import Live

        model_id = self.router.resolve_model(agent, stage)

        system = (
            f"You are {agent.name}, a {agent.role}.\n"
            f"Motto: \"{agent.motto}\"\n\n"
            f"{agent.system_prompt}\n\n"
            "IMPORTANT: Be concise. No filler, no self-introductions, no preamble. "
            "Go straight to the point. Max 300 words per response. "
            "Do not explain who you are or what you can do -- just do the work."
        )

        full_text = ""
        cost = None

        from matoi.core.cost import CostRecord

        # Stream and render markdown live
        with Live(Markdown(""), console=console, refresh_per_second=4) as live:
            for chunk in self.provider.stream(model_id, system, user_msg):
                if isinstance(chunk, CostRecord):
                    cost = chunk
                else:
                    full_text += chunk
                    try:
                        live.update(Markdown(full_text))
                    except Exception:
                        live.update(full_text)

        console.print()

        if cost:
            cost.agent_slug = agent.slug
            cost.stage = stage
            self.cost_tracker.record(cost)

        return full_text

    def _commit_flow(self) -> None:
        """Pre-commit: debate on changes → commit → update graph → show cost."""
        cwd = Path.cwd()

        # Check for staged/unstaged changes
        result = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=cwd, capture_output=True, text=True,
        )
        changes = result.stdout.strip()

        if not changes:
            result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                cwd=cwd, capture_output=True, text=True,
            )
            changes = result.stdout.strip()

        if not changes:
            console.print("  [dim]No changes to commit.[/dim]")
            return

        console.print()
        console.print(Panel(changes, title="Changes", border_style="dim"))

        # ── Debate on changes ──
        if self.pm and self.provider and len(self.agents) >= 2:
            console.rule("[dim]Pre-commit debate[/dim]")

            # Get diff for context
            diff_result = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=cwd, capture_output=True, text=True,
            )
            diff = diff_result.stdout[:3000] if diff_result.stdout else changes

            # Quick review from each agent
            reviews: dict[str, str] = {}
            for agent in self.agents[:3]:  # max 3 reviewers
                if self.cost_tracker.is_over_budget():
                    break
                console.print(f"  [dim]{agent.name} reviewing...[/dim]")
                review = self._call_agent(agent, "expert_pass",
                    f"Review these code changes. Flag issues, risks, or improvements.\n\n{diff}",
                )
                reviews[agent.slug] = review

            # Check for conflicts
            if len(reviews) >= 2:
                from matoi.orchestrator.conflict import ConflictDetector
                detector = ConflictDetector(self.provider)
                conflicts = detector.detect(reviews)

                if conflicts:
                    console.print(f"  [bold]{len(conflicts)} conflict(s) in reviews:[/bold]")
                    for c in conflicts:
                        console.print(f"    [{c.severity:.1f}] {c.topic}")

                    from matoi.orchestrator.debate import DebateEngine
                    engine = DebateEngine(self.provider, self.router, self.registry, max_rounds=1)

                    for conflict in conflicts[:2]:  # max 2 debates
                        rounds = engine.run_debate(conflict)
                        transcript = engine.format_transcript(conflict, rounds)

                        # Save debate artifact
                        project_dir = get_project_dir()
                        debate_file = project_dir / "artifacts" / f"debate_{self.session_id}.md"
                        debate_file.parent.mkdir(parents=True, exist_ok=True)
                        debate_file.write_text(transcript)
                else:
                    console.print("  [dim]No conflicts in reviews. Clean to commit.[/dim]")

        # ── Commit ──
        console.print()
        msg = Prompt.ask("  Commit message", default="Update from Matoi session")

        subprocess.run(["git", "add", "-A"], cwd=cwd)
        result = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=cwd, capture_output=True, text=True,
        )

        if result.returncode == 0:
            console.print(f"  [green]Committed: {msg}[/green]")

            # Update code graph
            subprocess.run(
                ["code-review-graph", "build"],
                cwd=cwd, capture_output=True, timeout=30,
            )

            # Index into MemPalace
            if self.memory:
                self.memory.store_artifacts(self.session_id, cwd)
        else:
            console.print(f"  [red]Commit failed: {result.stderr[:200]}[/red]")

        # Show cost
        console.print()
        self._show_cost()

    def _show_agents(self) -> None:
        """Show all available agents."""
        table = Table(border_style="dim", show_lines=False)
        table.add_column("Slug", style="bold", min_width=22)
        table.add_column("Name", min_width=20)
        table.add_column("Type", width=8)

        for a in sorted(self.registry.list_all(), key=lambda x: x.category.value):
            active = "[green]*[/green] " if a in self.agents else "  "
            table.add_row(f"{active}{a.slug}", a.name, a.agent_type.value)

        console.print()
        console.print(table)
        console.print("  [dim]* = active in this session[/dim]")
        console.print()

    def _show_history(self) -> None:
        """Show task history for this session."""
        if not self.history:
            console.print("  [dim]No tasks run yet.[/dim]")
            return
        console.print()
        for i, h in enumerate(self.history, 1):
            console.print(f"  {i}. {h['task'][:60]} ({h['timestamp'][:16]})")
        console.print()

    def _execute_task(self, task: str) -> None:
        """Subagent-driven execution: PM decomposes, agents execute, critics review."""
        if not self.pm or not self.provider or not self.agents:
            console.print("  [dim]Need PM and team to execute.[/dim]")
            return

        from matoi.orchestrator.dispatch import SubagentDispatcher

        dispatcher = SubagentDispatcher(
            pm=self.pm,
            agents=self.agents,
            registry=self.registry,
            provider=self.provider,
            router=self.router,
        )

        results = dispatcher.execute(task, self._call_agent)

        # Save to history
        self.history.append({
            "task": f"[execute] {task}",
            "brief": "",
            "opinions": {r.agent_slug: r.output[:200] for r in results},
            "decision": f"{len(results)} subtasks: {sum(1 for r in results if r.status == 'DONE')} done, "
                        f"{sum(1 for r in results if r.status == 'BLOCKED')} blocked",
            "timestamp": datetime.now().isoformat(),
        })

    def _generate_standup(self) -> None:
        """PM generates session summary."""
        if not self.history or not self.pm or not self.provider:
            console.print("  [dim]No tasks to summarize.[/dim]")
            return

        # Build context from session history
        tasks_summary = ""
        for i, h in enumerate(self.history, 1):
            tasks_summary += f"\n### Task {i}: {h['task'][:100]}\n"
            if h.get("decision"):
                tasks_summary += f"Decision: {h['decision'][:300]}\n"

        cost = self.cost_tracker.summary()

        system = (
            f"You are {self.pm.name}, a {self.pm.role}.\n"
            "Generate a concise session standup report. Include:\n"
            "1. **Done** -- what was accomplished (bullet points)\n"
            "2. **Decisions** -- key decisions made\n"
            "3. **Blockers** -- open questions or blockers\n"
            "4. **Next steps** -- what to do next session\n\n"
            "Max 200 words. No filler."
        )

        user_msg = (
            f"Session with {len(self.history)} tasks.\n"
            f"Team: {', '.join(a.name for a in self.agents)}\n"
            f"Cost: ${cost['total_cost_usd']:.4f}, {cost.get('total_tokens', 0):,} tokens\n"
            f"\n{tasks_summary}"
        )

        console.rule("[bold]Session Standup[/bold]")
        standup = self._call_agent(self.pm, "synthesis", user_msg)

        # Save as artifact
        from matoi.core.config import get_project_dir
        project_dir = get_project_dir()
        artifacts_dir = project_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        standup_file = artifacts_dir / f"standup_{self.session_id}.md"
        standup_file.write_text(f"# Session Standup -- {self.session_id}\n\n{standup}")
        console.print(f"  [dim]Saved: {standup_file}[/dim]")

        # Index into MemPalace
        if self.memory:
            self.memory.store_artifacts(self.session_id, artifacts_dir)

    def _change_key(self) -> None:
        """Change API key."""
        console.print("\n  Get your key at: https://console.anthropic.com/settings/keys\n")
        key = Prompt.ask("  New API Key", password=True)
        if key.strip():
            config = load_global_config()
            config.anthropic_api_key = key.strip()
            save_global_config(config)
            os.environ["ANTHROPIC_API_KEY"] = key.strip()
            self.provider = AnthropicProvider()
            console.print("  [green]API key updated.[/green]\n")
        else:
            console.print("  [dim]Cancelled.[/dim]\n")

    def _show_help(self) -> None:
        console.print()
        for cmd, desc in COMMANDS.items():
            console.print(f"  [bold]{cmd:12}[/bold] {desc}")
        console.print()

    def _show_team(self) -> None:
        if not self.pm:
            console.print("  [dim]No PM selected.[/dim]")
            return
        self._show_pm_avatar()
        if self.agents:
            names = ", ".join(a.name for a in self.agents)
            console.print(f"  Team: {names}")
        console.print()

    def _show_cost(self) -> None:
        summary = self.cost_tracker.summary()
        breakdown = summary.get("breakdown", [])

        if not breakdown:
            console.print("  [dim]No costs yet.[/dim]")
            return

        table = Table(title="Session Cost", border_style="dim", show_lines=False)
        table.add_column("Agent", min_width=18)
        table.add_column("Stage", width=14)
        table.add_column("Tokens", justify="right", width=10)
        table.add_column("Cost", justify="right", style="yellow", width=10)

        for row in breakdown:
            tokens = row["input_tokens"] + row["output_tokens"]
            table.add_row(row["agent"], row["stage"], f"{tokens:,}", f"${row['cost_usd']:.4f}")

        table.add_section()
        table.add_row(
            "[bold]Total[/bold]", f"{summary['total_calls']} calls",
            f"{summary.get('total_tokens', 0):,}",
            f"[bold]${summary['total_cost_usd']:.4f}[/bold]",
        )

        console.print()
        console.print(table)
        console.print()
