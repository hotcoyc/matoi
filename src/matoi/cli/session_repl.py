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
        self.history: list[dict] = []  # task-level history for standup
        self.context_history: list[dict] = []  # message-level history for compaction
        self.memory: MemoryStore | None = None
        self.prompt: MatoiPrompt | None = None

    def start(self) -> None:
        """Main entry point for interactive session."""
        from matoi import __version__
        console.print()
        try:
            import pyfiglet
            banner = pyfiglet.figlet_format("MATOI", font="electronic")
            console.print(f"[bold cyan]{banner}[/bold cyan]", end="", highlight=False)
        except ImportError:
            console.print("[bold cyan]MATOI[/bold cyan]")
        console.print(f"  [dim]Your startup team in the terminal.            v{__version__}[/dim]")
        console.print("  [dim]/help for commands, /commit before committing, /quit to exit.[/dim]")
        console.print()

        # ── Ensure API key ──
        self._ensure_api_key()
        self.provider = AnthropicProvider()

        # ── Ensure project initialized ──
        project_dir = get_project_dir()
        has_config = (project_dir / "config.json").exists()

        if not has_config:
            # First run -- full setup
            ensure_project_structure()
            _add_to_gitignore(Path.cwd())
            self._first_run_setup()
            self._new_session_setup()
        else:
            # Existing project -- ask continue or new
            import questionary
            choice = questionary.select(
                "Existing session found:",
                choices=[
                    questionary.Choice("Continue -- keep PM and team", value="continue"),
                    questionary.Choice("New session -- pick new PM and team", value="new"),
                ],
            ).ask()

            if choice == "new":
                self._new_session_setup()
            else:
                self._continue_session()

        # ── Setup memory ──
        self.memory = MemoryStore(project_dir)

        if self.prompt:
            self.prompt.update_status(
                team_size=len(self.agents),
                pm_name=self.pm.name if self.pm else "",
            )

        # ── REPL loop ──
        self._repl()

    def _new_session_setup(self) -> None:
        """Pick PM, describe goal, assemble team. Used on first run or new session."""
        self._pick_pm()

        agent_slugs = [a.slug for a in self.registry.list_all()]
        self.prompt = MatoiPrompt(
            project_name=Path.cwd().name,
            pm_name=self.pm.name if self.pm else "",
            agent_slugs=agent_slugs,
        )

        console.print()
        goal = self.prompt.ask_initial("What are you working on today?")
        console.print()

        if goal.strip():
            if self.pm and self.pm.slug == "enterprise-pm":
                goal_lower = goal.lower()
                simple_keywords = ["game", "tetris", "todo", "prototype", "mvp", "simple", "quick",
                                   "landing", "demo", "test", "try", "play", "fun"]
                if any(k in goal_lower for k in simple_keywords):
                    console.print(
                        f"  [dim]Hint: {self.pm.name} is compliance-focused. "
                        f"For quick builds, Oliver (Startup PM) might be faster.[/dim]"
                    )

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

    def _continue_session(self) -> None:
        """Load PM and team from saved config."""
        project_config = load_project_config()
        if project_config and project_config.pm:
            self.pm = self.registry.get(project_config.pm)
            if project_config.agents:
                for slug in project_config.agents:
                    agent = self.registry.get(slug)
                    if agent:
                        self.agents.append(agent)

        if self.pm:
            self._show_pm_avatar()
            if self.agents:
                names = ", ".join(a.name for a in self.agents)
                console.print(f"  Team: {names}")
        else:
            console.print("  [dim]No PM in saved config. Starting new session.[/dim]")
            self._new_session_setup()
            return

        agent_slugs = [a.slug for a in self.registry.list_all()]
        self.prompt = MatoiPrompt(
            project_name=Path.cwd().name,
            pm_name=self.pm.name if self.pm else "",
            agent_slugs=agent_slugs,
        )
        if self.prompt:
            self.prompt.update_status(
                team_size=len(self.agents),
                pm_name=self.pm.name if self.pm else "",
            )

    def _first_run_setup(self) -> None:
        """Auto-setup on first run: scan project, code graph, memory."""
        import shutil
        import subprocess
        import sys
        from rich.tree import Tree
        from matoi.core.scanner import scan_project

        cwd = Path.cwd()

        console.print("  [dim]First run -- analyzing project...[/dim]\n")

        # 1. Project structure
        scan = scan_project(cwd)
        console.print(f"  [bold]Project: {scan.name}[/bold]")
        console.print(f"  Files: {scan.total_files} | Dirs: {scan.total_dirs}")
        if scan.languages:
            top = sorted(scan.languages.items(), key=lambda x: x[1], reverse=True)[:5]
            langs = ", ".join(f"{lang} ({count})" for lang, count in top)
            console.print(f"  Languages: {langs}")
        if scan.frameworks:
            console.print(f"  Frameworks: {', '.join(scan.frameworks)}")
        if scan.is_git:
            console.print(f"  Git: {scan.git_commits} commits")
        console.print()

        # File tree
        if scan.file_tree:
            tree = Tree(f"[bold]{scan.name}/[/bold]")
            for line in scan.file_tree.strip().split("\n")[:15]:
                tree.add(line.strip())
            console.print(tree)
            console.print()

        # 2. Code graph (use sys.executable to find CLI in same venv)
        try:
            import code_review_graph  # noqa: F401
            crg_bin = shutil.which("code-review-graph") or f"{sys.executable.rsplit('/', 1)[0]}/code-review-graph"
            console.print("  [dim]Building code graph...[/dim]")
            result = subprocess.run(
                [crg_bin, "build"],
                cwd=cwd, capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                for line in (result.stderr + result.stdout).splitlines():
                    if "nodes" in line and "edges" in line:
                        console.print(f"  [green]Code graph: {line.strip()}[/green]")
                        break
                else:
                    console.print("  [green]Code graph built.[/green]")
                subprocess.run(
                    [crg_bin, "visualize"],
                    cwd=cwd, capture_output=True, text=True, timeout=30,
                )
        except (ImportError, Exception):
            pass

        # 3. CodeCharta (3D city)
        if shutil.which("ccsh"):
            try:
                console.print("  [dim]Building 3D code city...[/dim]")
                env = os.environ.copy()
                java17 = "/opt/homebrew/opt/openjdk@17/bin"
                if Path(java17).exists():
                    env["PATH"] = f"{java17}:{env.get('PATH', '')}"
                output_name = cwd.name or "project"
                src_arg = "src/" if (cwd / "src").is_dir() else "."
                subprocess.run(
                    ["ccsh", "unifiedparser", f"-o={output_name}", src_arg],
                    cwd=cwd, capture_output=True, text=True, timeout=120, env=env,
                )
                console.print("  [green]3D city built.[/green]")
            except (subprocess.TimeoutExpired, Exception):
                pass

        console.print()

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
            "Respond with ONLY a JSON array of agent slugs. Nothing else.\n"
            "No explanation, no markdown, no text before or after the array.\n"
            f"Example response: [\"backend-engineer\", \"frontend-engineer\"]\n\n"
            f"Available agents:\n{agents_desc}"
        )

        model_id = MODEL_MAP[self.pm.model_policy.brief]

        try:
            from alive_progress import alive_bar
            with alive_bar(title=f"  {self.pm.name} assembling team", bar=False, spinner="dots_waves"):
                text, cost = self.provider.call(model_id, system, goal, max_tokens=500)
            cost.agent_slug = self.pm.slug
            cost.stage = "team_recommend"
            self.cost_tracker.record(cost)

            # Parse response -- extract JSON array from anywhere in text
            import re
            text = text.strip()
            # Try to find JSON array in response
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                text = match.group(0)
            else:
                # Strip markdown fences
                if text.startswith("```"):
                    text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("```", 1)[0]
                text = text.strip()
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
        """Call an agent with live markdown rendering and context compaction."""
        from rich.live import Live
        from matoi.orchestrator.compaction import needs_compaction, compact_history

        model_id = self.router.resolve_model(agent, stage)

        # Check compaction before call
        if needs_compaction(self.context_history, model_id):
            console.print("  [dim]Compacting context...[/dim]")
            self.context_history = compact_history(self.context_history, self.provider)

        # Build context-aware user message
        context_prefix = ""

        # Include task-level history (decisions from previous tasks)
        if self.history:
            task_context = "## Session history\n"
            for h in self.history[-3:]:  # last 3 tasks
                task_context += f"- Task: {h['task'][:100]}\n"
                if h.get("decision"):
                    task_context += f"  Decision: {h['decision'][:200]}\n"
            context_prefix += task_context + "\n"

        # Include recent message-level context
        if self.context_history:
            recent_context = self.context_history[-6:]  # last 6 exchanges
            msg_context = "## Recent conversation\n"
            for msg in recent_context:
                role = msg.get("role", "")
                content = msg.get("content", "")[:300]
                if content:
                    msg_context += f"[{role}]: {content}\n"
            context_prefix += msg_context + "\n"

        system = (
            f"You are {agent.name}, a {agent.role}.\n"
            f"Motto: \"{agent.motto}\"\n\n"
            f"{agent.system_prompt}\n\n"
            "CRITICAL RULES:\n"
            "1. Be concise. Max 200 words of explanation. No filler, no self-introductions.\n"
            "2. ADAPT to task complexity. Simple task = simple answer. "
            "Do NOT add compliance gates, sign-off documents, or open-question blockers "
            "for straightforward tasks.\n"
            "3. If the task is clear enough to start, START. Do not ask for more context "
            "unless genuinely missing critical information.\n"
            "4. Do the work, not the paperwork. Produce deliverables, not process documents.\n"
            "5. When writing code: put COMPLETE file content in a code block tagged with the filename.\n"
            "   Example: ```index.html\\n<full code>\\n```\n"
            "   Do NOT show code inline in your explanation. Just say what the file does.\n"
            "   The system will automatically save files to disk.\n"
            "6. Your text response should only describe WHAT you created and WHY. Not the code itself."
        )

        full_msg = f"{context_prefix}{user_msg}" if context_prefix else user_msg

        full_text = ""
        cost = None

        from matoi.core.cost import CostRecord

        # Stream with spinner -- don't show raw code
        with console.status(f"[dim]{agent.name} working...[/dim]"):
            for chunk in self.provider.stream(model_id, system, full_msg):
                if isinstance(chunk, CostRecord):
                    cost = chunk
                else:
                    full_text += chunk

        # Show only text, strip all code blocks
        display_text = _strip_all_code_blocks(full_text)
        if display_text.strip():
            console.print(Markdown(display_text.strip()))
        console.print()

        if cost:
            cost.agent_slug = agent.slug
            cost.stage = stage
            self.cost_tracker.record(cost)

        # Extract and write any files from code blocks
        from matoi.orchestrator.dispatch import _extract_and_write_files
        written = _extract_and_write_files(full_text, Path.cwd())
        if written:
            for f in written:
                console.print(f"  [green]Created: {f}[/green]")

        # Track in context history
        self.context_history.append({"role": "user", "content": user_msg[:500]})
        self.context_history.append({"role": agent.slug, "content": full_text[:500]})

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
        """Generate session summary -- no LLM call, just facts."""
        if not self.history:
            return

        import subprocess
        from rich.table import Table
        from matoi.core.config import get_project_dir

        console.rule("[bold]Session Summary[/bold]")

        # 1. Files created/modified
        cwd = Path.cwd()
        result = subprocess.run(
            ["git", "diff", "--name-status", "HEAD~1"],
            cwd=cwd, capture_output=True, text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            console.print("\n  [bold]Files:[/bold]")
            for line in result.stdout.strip().split("\n")[:15]:
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    status, name = parts
                    label = {"A": "created", "M": "modified", "D": "deleted"}.get(status, status)
                    console.print(f"    {name} [dim]({label})[/dim]")
        else:
            # No git -- check for new files in CWD
            from matoi.orchestrator.dispatch import _extract_and_write_files
            # Just list files from history context
            pass

        # 2. Tasks worked on
        console.print(f"\n  [bold]Tasks:[/bold] {len(self.history)}")
        for h in self.history:
            console.print(f"    - {h['task'][:80]}")

        # 3. Debates/conflicts
        # Check if any debate artifacts exist
        project_dir = get_project_dir()
        debate_files = list((project_dir / "artifacts").glob(f"debate_{self.session_id}*")) if (project_dir / "artifacts").exists() else []
        if debate_files:
            console.print(f"\n  [bold]Debates:[/bold] {len(debate_files)} conflict(s) resolved")
        else:
            console.print(f"\n  [bold]Debates:[/bold] none")

        # 4. Save standup as artifact
        artifacts_dir = project_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        standup_lines = [f"# Session {self.session_id}", ""]
        standup_lines.append(f"PM: {self.pm.name if self.pm else 'none'}")
        standup_lines.append(f"Team: {', '.join(a.name for a in self.agents)}")
        standup_lines.append(f"Tasks: {len(self.history)}")
        for h in self.history:
            standup_lines.append(f"  - {h['task'][:100]}")
        standup_file = artifacts_dir / f"standup_{self.session_id}.md"
        standup_file.write_text("\n".join(standup_lines))

        console.print()

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
        table.add_column("Model", width=16)
        table.add_column("Tokens", justify="right", width=10)
        table.add_column("Cost", justify="right", style="yellow", width=10)

        for row in breakdown:
            tokens = row["input_tokens"] + row["output_tokens"]
            model_short = row.get("model", "").replace("claude-", "").replace("-20251001", "")
            table.add_row(row["agent"], row["stage"], model_short, f"{tokens:,}", f"${row['cost_usd']:.4f}")

        table.add_section()
        table.add_row(
            "[bold]Total[/bold]", f"{summary['total_calls']} calls", "",
            f"{summary.get('total_tokens', 0):,}",
            f"[bold]${summary['total_cost_usd']:.4f}[/bold]",
        )

        console.print()
        console.print(table)
        console.print()


def _strip_all_code_blocks(text: str) -> str:
    """Remove ALL code blocks from display text. Keep only prose."""
    import re
    return re.sub(r"```[\s\S]*?```", "", text).strip()


def _add_to_gitignore(cwd: Path) -> None:
    """Add .matoi/ to project's .gitignore. AI data stays local."""
    gitignore = cwd / ".gitignore"
    entry = ".matoi/"

    if gitignore.exists():
        content = gitignore.read_text()
        if entry in content:
            return
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n# Matoi AI workspace (local only)\n{entry}\n"
        gitignore.write_text(content)
    else:
        gitignore.write_text(f"# Matoi AI workspace (local only)\n{entry}\n")
