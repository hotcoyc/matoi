"""Fullscreen TUI for Matoi using Textual.

Layout:
+--------+-------------------------------------+
| Agents |  Header: PM | Team: 3 | $0.0042     |
|        |-------------------------------------|
| [PM]*  |  > User: Design the MVP             |
| Agent1 |                                     |
| Agent2 |  --- Startup PM -- brief ---         |
| Agent3 |  Goal: validate pet care market...   |
|        |                                     |
|        |  --- Backend Engineer ---            |
|        |  I recommend using FastAPI...        |
|        |-------------------------------------|
|        |  > type your task...                 |
+--------+-------------------------------------+
| /help /team /commit /quit       cost:$0.12   |
+----------------------------------------------+

Phase C2 features:
1. Sidebar with agents (who's active, who's talking)
2. Color coding per agent type
3. Progress indicator (which agent is thinking)
4. /commit in fullscreen
5. Tabs: chat / cost
6. PM info in header
"""

import subprocess
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
)

# Color coding per agent type
TYPE_COLORS = {
    "coordinator": "bold magenta",
    "executor": "bold cyan",
    "thinker": "bold yellow",
    "critic": "bold red",
}

TYPE_LABELS = {
    "coordinator": "PM",
    "executor": "EXE",
    "thinker": "THK",
    "critic": "CRT",
}


class AgentListItem(ListItem):
    """An agent in the sidebar."""
    def __init__(self, name: str, agent_type: str, slug: str, is_pm: bool = False) -> None:
        self.agent_name = name
        self.agent_type = agent_type
        self.slug = slug
        self.is_pm = is_pm
        label = TYPE_LABELS.get(agent_type, "")
        prefix = "*" if is_pm else " "
        super().__init__(Label(f"{prefix}[{label}] {name}"), id=f"agent-{slug}")


class ChatMessage(Static):
    """A single message in the chat area."""
    pass


class MatoiApp(App):
    """Fullscreen Matoi TUI."""

    TITLE = "Matoi"

    CSS = """
    /* Main layout */
    #main-layout {
        height: 1fr;
    }

    #sidebar {
        width: 26;
        background: $surface;
        border-right: solid $primary-background;
        padding: 0;
    }

    #sidebar-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
        background: $primary-background;
    }

    #agent-list {
        height: 1fr;
    }

    #content-area {
        width: 1fr;
    }

    /* Header */
    #header-bar {
        height: 3;
        background: $primary-background;
        padding: 0 2;
        content-align: center middle;
    }

    #pm-info {
        width: 1fr;
    }

    #stats-info {
        width: auto;
        text-align: right;
    }

    /* Chat */
    #chat-scroll {
        height: 1fr;
    }

    #chat-area {
        padding: 0 1;
    }

    /* Cost tab */
    #cost-area {
        padding: 1 2;
    }

    /* Input */
    #input-field {
        dock: bottom;
    }

    /* Messages */
    .user-msg {
        margin: 1 0 0 0;
        padding: 0 1;
        background: $surface;
        color: $text;
    }

    .agent-header-pm {
        margin: 1 0 0 0;
        padding: 0 1;
        color: magenta;
        text-style: bold;
    }

    .agent-header-exe {
        margin: 1 0 0 0;
        padding: 0 1;
        color: cyan;
        text-style: bold;
    }

    .agent-header-thk {
        margin: 1 0 0 0;
        padding: 0 1;
        color: yellow;
        text-style: bold;
    }

    .agent-header-crt {
        margin: 1 0 0 0;
        padding: 0 1;
        color: red;
        text-style: bold;
    }

    .agent-response {
        margin: 0 0 0 2;
        padding: 0 1;
    }

    .system-msg {
        margin: 1 0;
        padding: 0 1;
        color: $text-muted;
        text-style: italic;
    }

    .progress-msg {
        margin: 0;
        padding: 0 1;
        color: $text-muted;
    }

    /* Active agent highlight */
    .agent-active {
        background: $primary-background;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear", "Clear"),
        Binding("ctrl+t", "toggle_tab", "Tab"),
        Binding("escape", "focus_input", "Input", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.pm = None
        self.pm_name = ""
        self.agents = []
        self.provider = None
        self.router = None
        self.registry = None
        self.cost_tracker = None
        self.memory = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._ready = False
        self._current_tab = "chat"

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-layout"):
            # Sidebar
            with Vertical(id="sidebar"):
                yield Static("Team", id="sidebar-title")
                yield ListView(id="agent-list")

            # Content
            with Vertical(id="content-area"):
                # Header
                with Horizontal(id="header-bar"):
                    yield Static("Matoi", id="pm-info")
                    yield Static("", id="stats-info")

                # Tabbed content
                with TabbedContent(id="tabs"):
                    with TabPane("Chat", id="tab-chat"):
                        with VerticalScroll(id="chat-scroll"):
                            yield Vertical(id="chat-area")
                    with TabPane("Cost", id="tab-cost"):
                        yield Static("No costs yet.", id="cost-area")

                # Input
                yield Input(
                    placeholder="Type your task... (/help /commit /quit)",
                    id="input-field",
                )

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#input-field", Input).focus()
        self._init_session()

    def _init_session(self) -> None:
        """Initialize provider, registry, PM, team."""
        from matoi.cli.common import get_registry
        from matoi.core.config import (
            ensure_project_structure,
            get_project_dir,
            load_project_config,
            require_api_key,
        )
        from matoi.core.cost import Budget
        from matoi.gateway.provider import AnthropicProvider
        from matoi.gateway.router import ModelRouter
        from matoi.storage.costs import CostTracker
        from matoi.storage.memory import MemoryStore

        key = require_api_key()
        if not key:
            self._add_system("API key not found. Run 'matoi --classic' to configure.")
            return

        self.provider = AnthropicProvider()
        self.router = ModelRouter()
        self.registry = get_registry()
        self.cost_tracker = CostTracker(Budget(max_total_usd=10.0))

        project_dir = get_project_dir()
        if not (project_dir / "config.json").exists():
            ensure_project_structure()
        self.memory = MemoryStore(project_dir)

        # Load PM and team
        project_config = load_project_config()
        if project_config and project_config.pm:
            self.pm = self.registry.get(project_config.pm)
            if project_config.agents:
                for slug in project_config.agents:
                    agent = self.registry.get(slug)
                    if agent:
                        self.agents.append(agent)

        # Populate sidebar
        self._populate_sidebar()

        if self.pm:
            self.pm_name = self.pm.name
            self._update_header()
            self._add_system(f"PM: {self.pm.name} -- \"{self.pm.motto}\"")
            if self.agents:
                names = ", ".join(a.name for a in self.agents)
                self._add_system(f"Team: {names}")
            else:
                self._add_system("No team. Run 'matoi --classic' to set up.")
        else:
            self._add_system("No PM. Run 'matoi --classic' to set up first.")

        self._add_system("Ready. Type your task. /help for commands.")
        self._ready = True

    def _populate_sidebar(self) -> None:
        """Fill sidebar with PM and agents."""
        agent_list = self.query_one("#agent-list", ListView)
        if self.pm:
            agent_list.append(AgentListItem(
                self.pm.name, self.pm.agent_type.value, self.pm.slug, is_pm=True,
            ))
        for agent in self.agents:
            agent_list.append(AgentListItem(
                agent.name, agent.agent_type.value, agent.slug,
            ))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""

        if text.lower() in ("exit", "quit", "q", "/quit", "/exit"):
            self.exit()
            return

        if text.startswith("/"):
            self._handle_command(text)
            return

        self._add_user(text)
        if self._ready and self.pm and self.provider:
            self._run_task(text)

    def _handle_command(self, text: str) -> None:
        cmd = text.split()[0].lower()
        if cmd == "/help":
            self._add_system(
                "/help    -- show commands\n"
                "/team    -- show current team\n"
                "/cost    -- show session cost\n"
                "/commit  -- review changes, debate, commit\n"
                "/clear   -- clear chat\n"
                "/quit    -- exit\n"
                "ctrl+t   -- switch Chat/Cost tab"
            )
        elif cmd == "/team":
            if self.pm:
                names = ", ".join(a.name for a in self.agents) if self.agents else "none"
                self._add_system(f"PM: {self.pm.name}\nTeam: {names}")
        elif cmd == "/cost":
            self._update_cost_tab()
            # Switch to cost tab
            tabs = self.query_one("#tabs", TabbedContent)
            tabs.active = "tab-cost"
        elif cmd == "/clear":
            self.action_clear()
        elif cmd == "/commit":
            self._run_commit()
        else:
            self._add_system(f"Unknown: {cmd}. Type /help")

    @work(thread=True)
    def _run_task(self, task: str) -> None:
        """Run task through pipeline in background thread."""
        if not self.pm or not self.provider:
            return

        # Brief
        self._set_agent_active(self.pm.slug)
        self.call_from_thread(self._add_progress, f"{self.pm.name} is writing brief...")
        brief = self._call_agent_sync(self.pm, "brief",
            f"Create a brief for this task:\n{task}")
        self._clear_agent_active(self.pm.slug)

        # Expert pass
        opinions = {}
        for agent in self.agents:
            if self.cost_tracker and self.cost_tracker.is_over_budget():
                self.call_from_thread(self._add_system, "Budget limit reached.")
                break
            self._set_agent_active(agent.slug)
            self.call_from_thread(self._add_progress, f"{agent.name} is thinking...")
            opinion = self._call_agent_sync(agent, "expert_pass",
                f"## Task\n{task}\n\n## Brief\n{brief}")
            opinions[agent.slug] = opinion
            self._clear_agent_active(agent.slug)

        # Synthesis
        opinions_text = ""
        for slug, opinion in opinions.items():
            a = self.registry.get(slug)
            name = a.name if a else slug
            opinions_text += f"\n### {name}\n{opinion}\n"

        self._set_agent_active(self.pm.slug)
        self.call_from_thread(self._add_progress, f"{self.pm.name} is synthesizing...")
        self._call_agent_sync(self.pm, "synthesis",
            f"## Task\n{task}\n\n## Brief\n{brief}\n\n## Opinions\n{opinions_text}\n\n"
            "Synthesize: what to do, why, risks, next steps. Be concise.")
        self._clear_agent_active(self.pm.slug)

        self.call_from_thread(self._update_header)
        self.call_from_thread(self._update_cost_tab)

    @work(thread=True)
    def _run_commit(self) -> None:
        """Review changes, debate, commit."""
        cwd = Path.cwd()

        # Check for changes
        result = subprocess.run(
            ["git", "diff", "--stat"], cwd=cwd, capture_output=True, text=True,
        )
        diff_stat = result.stdout.strip()

        result2 = subprocess.run(
            ["git", "diff", "--cached", "--stat"], cwd=cwd, capture_output=True, text=True,
        )
        cached_stat = result2.stdout.strip()
        changes = diff_stat or cached_stat

        if not changes:
            self.call_from_thread(self._add_system, "No changes to commit.")
            return

        self.call_from_thread(self._add_system, f"Changes:\n{changes}")

        # Get diff for review
        diff_result = subprocess.run(
            ["git", "diff"], cwd=cwd, capture_output=True, text=True,
        )
        diff = diff_result.stdout[:3000] if diff_result.stdout else changes

        # Agent reviews
        if self.pm and self.provider and self.agents:
            reviews = {}
            for agent in self.agents[:2]:
                self._set_agent_active(agent.slug)
                self.call_from_thread(self._add_progress, f"{agent.name} reviewing...")
                review = self._call_agent_sync(agent, "expert_pass",
                    f"Review these code changes. Be concise. Flag issues only.\n\n{diff}")
                reviews[agent.slug] = review
                self._clear_agent_active(agent.slug)

            # Conflict detection
            if len(reviews) >= 2:
                from matoi.orchestrator.conflict import ConflictDetector
                detector = ConflictDetector(self.provider)
                conflicts = detector.detect(reviews)
                if conflicts:
                    self.call_from_thread(self._add_system,
                        f"{len(conflicts)} conflict(s) found. Running debate...")
                    from matoi.orchestrator.debate import DebateEngine
                    engine = DebateEngine(self.provider, self.router, self.registry, max_rounds=1)
                    for c in conflicts[:1]:
                        rounds = engine.run_debate(c)
                        transcript = engine.format_transcript(c, rounds)
                        self.call_from_thread(self._add_agent_response, transcript)
                else:
                    self.call_from_thread(self._add_system, "No conflicts. Clean to commit.")

        # Stage and commit
        subprocess.run(["git", "add", "-A"], cwd=cwd)
        result = subprocess.run(
            ["git", "commit", "-m", f"matoi session {self.session_id}"],
            cwd=cwd, capture_output=True, text=True,
        )
        if result.returncode == 0:
            self.call_from_thread(self._add_system, "Committed.")
        else:
            self.call_from_thread(self._add_system, f"Commit failed: {result.stderr[:200]}")

        self.call_from_thread(self._update_header)

    def _call_agent_sync(self, agent, stage: str, user_msg: str) -> str:
        """Call agent synchronously (runs in worker thread)."""
        from matoi.core.cost import CostRecord

        model_id = self.router.resolve_model(agent, stage)
        agent_type = agent.agent_type.value
        header_class = f"agent-header-{TYPE_LABELS.get(agent_type, 'exe').lower()}"

        system = (
            f"You are {agent.name}, a {agent.role}.\n"
            f"Motto: \"{agent.motto}\"\n\n"
            f"{agent.system_prompt}\n\n"
            "IMPORTANT: Be concise. Max 300 words. No self-introductions."
        )

        full_text = ""
        cost = None

        # Show header
        label = TYPE_LABELS.get(agent_type, "")
        self.call_from_thread(self._add_agent_header, f"[{label}] {agent.name} -- {stage}", header_class)

        for chunk in self.provider.stream(model_id, system, user_msg):
            if isinstance(chunk, CostRecord):
                cost = chunk
            else:
                full_text += chunk

        self.call_from_thread(self._add_agent_response, full_text)

        if cost and self.cost_tracker:
            cost.agent_slug = agent.slug
            cost.stage = stage
            self.cost_tracker.record(cost)

        return full_text

    # ── Agent activity indicator ──

    def _set_agent_active(self, slug: str) -> None:
        try:
            item = self.query_one(f"#agent-{slug}", AgentListItem)
            self.call_from_thread(item.add_class, "agent-active")
        except Exception:
            pass

    def _clear_agent_active(self, slug: str) -> None:
        try:
            item = self.query_one(f"#agent-{slug}", AgentListItem)
            self.call_from_thread(item.remove_class, "agent-active")
        except Exception:
            pass

    # ── Chat helpers ──

    def _add_user(self, text: str) -> None:
        chat = self.query_one("#chat-area")
        chat.mount(ChatMessage(f"> {text}", classes="user-msg"))
        self.query_one("#chat-scroll").scroll_end()

    def _add_agent_header(self, label: str, css_class: str = "agent-header-exe") -> None:
        chat = self.query_one("#chat-area")
        chat.mount(ChatMessage(f"--- {label} ---", classes=css_class))
        self.query_one("#chat-scroll").scroll_end()

    def _add_agent_response(self, text: str) -> None:
        chat = self.query_one("#chat-area")
        chat.mount(Markdown(text, classes="agent-response"))
        self.query_one("#chat-scroll").scroll_end()

    def _add_system(self, text: str) -> None:
        chat = self.query_one("#chat-area")
        chat.mount(ChatMessage(text, classes="system-msg"))
        self.query_one("#chat-scroll").scroll_end()

    def _add_progress(self, text: str) -> None:
        chat = self.query_one("#chat-area")
        chat.mount(ChatMessage(text, classes="progress-msg"))
        self.query_one("#chat-scroll").scroll_end()

    # ── Header / Cost ──

    def _update_header(self) -> None:
        pm_info = self.query_one("#pm-info", Static)
        stats_info = self.query_one("#stats-info", Static)

        pm_text = f"Matoi | {self.pm_name}" if self.pm_name else "Matoi"
        pm_info.update(pm_text)

        if self.cost_tracker:
            s = self.cost_tracker.summary()
            stats_info.update(
                f"Team: {len(self.agents)} | "
                f"Tokens: {s.get('total_tokens', 0):,} | "
                f"${s['total_cost_usd']:.4f}"
            )

    def _update_cost_tab(self) -> None:
        if not self.cost_tracker:
            return
        s = self.cost_tracker.summary()
        breakdown = s.get("breakdown", [])

        lines = [f"Total: ${s['total_cost_usd']:.4f} | Calls: {s['total_calls']} | Tokens: {s.get('total_tokens', 0):,}\n"]

        if breakdown:
            lines.append(f"{'Agent':<20} {'Stage':<14} {'Tokens':>8} {'Cost':>10}")
            lines.append("-" * 56)
            for row in breakdown:
                tokens = row.get("input_tokens", 0) + row.get("output_tokens", 0)
                lines.append(f"{row['agent']:<20} {row['stage']:<14} {tokens:>8,} ${row['cost_usd']:>9.4f}")

        cost_area = self.query_one("#cost-area", Static)
        cost_area.update("\n".join(lines))

    # ── Actions ──

    def action_clear(self) -> None:
        chat = self.query_one("#chat-area")
        chat.remove_children()

    def action_focus_input(self) -> None:
        self.query_one("#input-field", Input).focus()

    def action_toggle_tab(self) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        if tabs.active == "tab-chat":
            tabs.active = "tab-cost"
        else:
            tabs.active = "tab-chat"


def run_fullscreen() -> None:
    """Entry point for fullscreen TUI."""
    app = MatoiApp()
    app.run()
