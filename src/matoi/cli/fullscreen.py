"""Fullscreen TUI for Matoi using Textual.

Layout:
+------------------------------------------+
| [PM Avatar] PM Name | Team: 3 | $0.0042  |  <- Header
+------------------------------------------+
|                                          |
|  > User: Design the MVP                 |  <- Chat area
|                                          |
|  --- Startup PM -- brief ---             |
|  Goal: validate pet care market...       |
|                                          |
|  --- Backend Engineer ---                |
|  I recommend using FastAPI...            |
|                                          |
+------------------------------------------+
| > type your task...                      |  <- Input
+------------------------------------------+
| /help /team /commit /quit    cost:$0.12  |  <- Footer
+------------------------------------------+
"""

import os
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown, Static


class ChatMessage(Static):
    """A single message in the chat area."""
    pass


class MatoiApp(App):
    """Fullscreen Matoi TUI."""

    CSS = """
    #chat-area {
        height: 1fr;
        overflow-y: auto;
        padding: 0 1;
    }

    #input-area {
        dock: bottom;
        height: 3;
        padding: 0 1;
    }

    #input-field {
        width: 1fr;
    }

    #header-bar {
        dock: top;
        height: 3;
        background: $surface;
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

    .user-msg {
        margin: 1 0 0 0;
        padding: 0 1;
        color: $text;
    }

    .agent-header {
        margin: 1 0 0 0;
        padding: 0 1;
        color: $accent;
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
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear", "Clear"),
        Binding("escape", "focus_input", "Focus input", show=False),
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

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static("Matoi", id="pm-info"),
            Static("", id="stats-info"),
            id="header-bar",
        )
        yield VerticalScroll(id="chat-area")
        yield Input(placeholder="Type your task... (/help, /commit, /quit)", id="input-field")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#input-field", Input).focus()
        self._init_session()

    def _init_session(self) -> None:
        """Initialize provider, registry, PM, team."""
        from matoi.cli.common import get_registry
        from matoi.core.config import (
            get_project_dir,
            load_global_config,
            load_project_config,
            require_api_key,
            ensure_project_structure,
        )
        from matoi.core.cost import Budget
        from matoi.gateway.provider import AnthropicProvider
        from matoi.gateway.router import ModelRouter
        from matoi.storage.costs import CostTracker
        from matoi.storage.memory import MemoryStore

        # API key
        key = require_api_key()
        if not key:
            self._add_system("API key not found. Set it in ~/.matoi/config.json or run matoi init.")
            return

        self.provider = AnthropicProvider()
        self.router = ModelRouter()
        self.registry = get_registry()
        self.cost_tracker = CostTracker(Budget(max_total_usd=10.0))

        # Project
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

        if self.pm:
            self.pm_name = self.pm.name
            self._update_header()
            self._add_system(f"PM: {self.pm.name} -- \"{self.pm.motto}\"")
            if self.agents:
                names = ", ".join(a.name for a in self.agents)
                self._add_system(f"Team: {names}")
            else:
                self._add_system("No team configured. Run 'matoi' to set up.")
        else:
            self._add_system("No PM configured. Run 'matoi' to set up first.")

        self._add_system("Type your task. /help for commands.")
        self._ready = True

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return

        event.input.value = ""

        # Exit commands
        if text.lower() in ("exit", "quit", "q", "/quit", "/exit"):
            self.exit()
            return

        # Commands
        if text.startswith("/"):
            self._handle_command(text)
            return

        # Run task
        self._add_user(text)
        if self._ready and self.pm and self.provider:
            self._run_task(text)

    def _handle_command(self, cmd: str) -> None:
        cmd = cmd.split()[0].lower()
        if cmd == "/help":
            self._add_system(
                "/help -- show commands\n"
                "/team -- show current team\n"
                "/cost -- show session cost\n"
                "/commit -- review, debate, commit\n"
                "/clear -- clear chat\n"
                "/quit -- exit"
            )
        elif cmd == "/team":
            if self.pm:
                names = ", ".join(a.name for a in self.agents) if self.agents else "none"
                self._add_system(f"PM: {self.pm.name}\nTeam: {names}")
            else:
                self._add_system("No PM configured.")
        elif cmd == "/cost":
            if self.cost_tracker:
                s = self.cost_tracker.summary()
                self._add_system(
                    f"Cost: ${s['total_cost_usd']:.4f} | "
                    f"Calls: {s['total_calls']} | "
                    f"Tokens: {s.get('total_tokens', 0):,}"
                )
        elif cmd == "/clear":
            self.action_clear()
        elif cmd == "/commit":
            self._add_system("Commit flow not yet available in fullscreen mode. Use 'matoi' CLI.")
        else:
            self._add_system(f"Unknown command: {cmd}")

    @work(thread=True)
    def _run_task(self, task: str) -> None:
        """Run task through pipeline in background thread."""
        from matoi.core.cost import CostRecord

        if not self.pm or not self.provider:
            return

        # Brief
        self.call_from_thread(self._add_agent_header, f"{self.pm.name} -- brief")
        brief = self._call_agent_sync(self.pm, "brief",
            f"Create a brief for this task:\n{task}")

        # Expert pass
        opinions = {}
        for agent in self.agents:
            if self.cost_tracker and self.cost_tracker.is_over_budget():
                self.call_from_thread(self._add_system, "Budget limit reached.")
                break
            self.call_from_thread(self._add_agent_header, agent.name)
            opinion = self._call_agent_sync(agent, "expert_pass",
                f"## Task\n{task}\n\n## Brief\n{brief}")
            opinions[agent.slug] = opinion

        # Synthesis
        opinions_text = ""
        for slug, opinion in opinions.items():
            a = self.registry.get(slug)
            name = a.name if a else slug
            opinions_text += f"\n### {name}\n{opinion}\n"

        self.call_from_thread(self._add_agent_header, f"{self.pm.name} -- synthesis")
        self._call_agent_sync(self.pm, "synthesis",
            f"## Task\n{task}\n\n## Brief\n{brief}\n\n## Opinions\n{opinions_text}\n\n"
            "Synthesize: what to do, why, risks, next steps.")

        # Update header
        if self.cost_tracker:
            self.call_from_thread(self._update_header)

    def _call_agent_sync(self, agent, stage: str, user_msg: str) -> str:
        """Call agent synchronously (runs in worker thread)."""
        from matoi.core.cost import CostRecord

        model_id = self.router.resolve_model(agent, stage)
        system = (
            f"You are {agent.name}, a {agent.role}.\n"
            f"Motto: \"{agent.motto}\"\n\n"
            f"{agent.system_prompt}\n\n"
            "IMPORTANT: Be concise. Max 300 words. No self-introductions, no preamble."
        )

        full_text = ""
        cost = None

        for chunk in self.provider.stream(model_id, system, user_msg):
            if isinstance(chunk, CostRecord):
                cost = chunk
            else:
                full_text += chunk

        # Display response as markdown
        self.call_from_thread(self._add_agent_response, full_text)

        if cost and self.cost_tracker:
            cost.agent_slug = agent.slug
            cost.stage = stage
            self.cost_tracker.record(cost)

        return full_text

    def _add_user(self, text: str) -> None:
        chat = self.query_one("#chat-area")
        msg = ChatMessage(f"> {text}", classes="user-msg")
        chat.mount(msg)
        chat.scroll_end()

    def _add_agent_header(self, label: str) -> None:
        chat = self.query_one("#chat-area")
        msg = ChatMessage(f"--- {label} ---", classes="agent-header")
        chat.mount(msg)
        chat.scroll_end()

    def _add_agent_response(self, text: str) -> None:
        chat = self.query_one("#chat-area")
        md = Markdown(text, classes="agent-response")
        chat.mount(md)
        chat.scroll_end()

    def _add_system(self, text: str) -> None:
        chat = self.query_one("#chat-area")
        msg = ChatMessage(text, classes="system-msg")
        chat.mount(msg)
        chat.scroll_end()

    def _update_header(self) -> None:
        pm_info = self.query_one("#pm-info", Static)
        stats_info = self.query_one("#stats-info", Static)

        pm_text = f"Matoi | {self.pm_name}" if self.pm_name else "Matoi"
        pm_info.update(pm_text)

        if self.cost_tracker:
            s = self.cost_tracker.summary()
            stats_info.update(
                f"Team: {len(self.agents)} | "
                f"${s['total_cost_usd']:.4f}"
            )

    def action_clear(self) -> None:
        chat = self.query_one("#chat-area")
        chat.remove_children()

    def action_focus_input(self) -> None:
        self.query_one("#input-field", Input).focus()


def run_fullscreen() -> None:
    """Entry point for fullscreen TUI."""
    app = MatoiApp()
    app.run()
