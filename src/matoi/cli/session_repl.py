"""Interactive REPL session for Matoi.

Flow:
1. Pick PM (or use saved)
2. Describe your goal
3. PM recommends team
4. REPL: user types tasks, agents respond (streaming)
5. /commit → debate on changes → commit → update graph → show cost
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

from matoi.agents.registry import AgentRegistry
from matoi.cli.common import get_package_root, get_registry, load_avatar
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
    "/cost": "Show session cost so far",
    "/commit": "Run debate on changes, commit, update graph",
    "/quit": "End session",
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
        self.history: list[dict] = []  # conversation history
        self.memory: MemoryStore | None = None

    def start(self) -> None:
        """Main entry point for interactive session."""
        console.print()
        console.print(Panel(
            "[bold]Matoi[/bold] -- your startup team in the terminal.\n"
            "Type your task. Agents will respond.\n"
            "Type /help for commands, /quit to exit.",
            border_style="bold white",
        ))
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
                console.print(f"  PM: [bold]{self.pm.name}[/bold] -- \"{self.pm.motto}\"")
            else:
                self._pick_pm()
        else:
            self._pick_pm()

        # ── Describe goal → PM recommends team ──
        console.print()
        goal = Prompt.ask("[bold]What are you working on today?[/bold]")
        console.print()

        if goal.strip():
            self._recommend_team(goal)

        # ── REPL loop ──
        self._repl(goal)

    def _ensure_api_key(self) -> None:
        """Check API key, prompt if missing."""
        key = require_api_key()
        if not key:
            console.print("  API key not found.\n")
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
        else:
            console.print("  [dim]API key: ok[/dim]")

    def _pick_pm(self) -> None:
        """Interactive PM selection."""
        from matoi.cli.team import _render_pm_gallery, PM_COLORS

        coordinators = self.registry.list_by_type("coordinator")
        if not coordinators:
            console.print("[red]No PM agents found.[/red]")
            raise SystemExit(1)

        _render_pm_gallery(coordinators)

        choices_display = ", ".join(
            f"[bold]{i + 1}[/bold]={c.slug}" for i, c in enumerate(coordinators)
        )
        console.print(f"\n  {choices_display}")

        choice = Prompt.ask(
            "\n  Select PM",
            choices=[str(i + 1) for i in range(len(coordinators))],
        )
        self.pm = coordinators[int(choice) - 1]
        console.print(f"\n  PM: [bold]{self.pm.name}[/bold]")

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

        console.print(f"  [dim]{self.pm.name} is assembling your team...[/dim]")

        try:
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
        """Main REPL loop."""
        console.print()
        console.rule("[dim]Session started. Type your tasks.[/dim]")
        console.print()

        while True:
            try:
                user_input = Prompt.ask("[bold]>[/bold]")
            except (KeyboardInterrupt, EOFError):
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            # ── Commands ──
            if user_input.startswith("/"):
                if user_input == "/quit" or user_input == "/exit":
                    break
                elif user_input == "/help":
                    self._show_help()
                elif user_input == "/team":
                    self._show_team()
                elif user_input == "/cost":
                    self._show_cost()
                elif user_input == "/commit":
                    self._commit_flow()
                else:
                    console.print(f"  [dim]Unknown command: {user_input}. Type /help[/dim]")
                continue

            # ── Run task ──
            self._run_task(user_input)

        # ── Session end ──
        console.print()
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
        """Call an agent with streaming output."""
        model_id = self.router.resolve_model(agent, stage)

        system = (
            f"You are {agent.name}, a {agent.role}.\n"
            f"Motto: \"{agent.motto}\"\n\n"
            f"{agent.system_prompt}"
        )

        full_text = ""
        cost = None

        from matoi.core.cost import CostRecord

        for chunk in self.provider.stream(model_id, system, user_msg):
            if isinstance(chunk, CostRecord):
                cost = chunk
            else:
                console.print(chunk, end="", highlight=False)
                full_text += chunk

        console.print()
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

    def _show_help(self) -> None:
        console.print()
        for cmd, desc in COMMANDS.items():
            console.print(f"  [bold]{cmd:12}[/bold] {desc}")
        console.print()

    def _show_team(self) -> None:
        if not self.pm:
            console.print("  [dim]No PM selected.[/dim]")
            return
        console.print(f"\n  PM: [bold]{self.pm.name}[/bold]")
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
