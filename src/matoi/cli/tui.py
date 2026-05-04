"""TUI prompt with prompt_toolkit.

Features:
- Colored prompt with project/PM indicator
- Multiline input (Alt+Enter for newline)
- Command autocomplete (/ prefix)
- Agent autocomplete (@ prefix)
- Persistent history (~/.matoi/history)
- Bottom status bar (PM, team, cost, tokens)
- Keybindings: Ctrl+C cancel, Ctrl+D quit, Ctrl+L clear, Tab complete
"""

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion, FuzzyWordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from matoi.core.config import get_global_dir

# ── Style ──

MATOI_STYLE = Style.from_dict({
    "prompt": "bold #87d7ff",
    "prompt.project": "#5f8787",
    "prompt.pm": "bold #d7af5f",
    "bottom-toolbar": "bg:#1c1c1c #808080",
    "bottom-toolbar.key": "#d7af5f",
    "bottom-toolbar.value": "#ffffff",
})

# ── Commands ──

COMMANDS = [
    "/help",
    "/team",
    "/cost",
    "/commit",
    "/key",
    "/quit",
    "/exit",
    "/history",
    "/agents",
]


class MatoiCompleter(Completer):
    """Autocomplete for / commands and @ agent mentions. Fuzzy matching."""

    def __init__(self, agent_slugs: list[str] | None = None) -> None:
        self.agent_slugs = agent_slugs or []

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)

        # Command completion (fuzzy)
        if text.startswith("/"):
            query = word.lower().lstrip("/")
            for cmd in COMMANDS:
                cmd_name = cmd.lstrip("/")
                if not query or query in cmd_name:
                    yield Completion(cmd, start_position=-len(word), display_meta="command")

        # Agent mention completion (fuzzy)
        elif "@" in text:
            at_pos = text.rfind("@")
            partial = text[at_pos + 1:].lower()
            for slug in self.agent_slugs:
                if not partial or partial in slug.lower():
                    yield Completion(
                        slug,
                        start_position=-len(text[at_pos + 1:]),
                        display_meta="agent",
                    )


class MatoiPrompt:
    """Interactive prompt for Matoi sessions."""

    def __init__(
        self,
        project_name: str = "",
        pm_name: str = "",
        agent_slugs: list[str] | None = None,
    ) -> None:
        self.project_name = project_name or Path.cwd().name
        self.pm_name = pm_name
        self.cost_usd = 0.0
        self.total_tokens = 0
        self.team_size = 0

        # History file
        history_path = get_global_dir() / "history"
        self.history = FileHistory(str(history_path))

        # Completer
        self.completer = MatoiCompleter(agent_slugs)

        # Key bindings
        self.bindings = self._create_bindings()

        # Session
        self.session: PromptSession = PromptSession(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            complete_while_typing=False,
            style=MATOI_STYLE,
            key_bindings=self.bindings,
            bottom_toolbar=self._toolbar,
            multiline=False,  # Enter sends, Alt+Enter for newline
            enable_open_in_editor=False,
        )

        self._first_prompt = True
        self._working = False

    def ask(self) -> str | None:
        """Show prompt and get user input. Returns None on Ctrl+D/exit."""
        self._working = False
        prompt_text = self._build_prompt()

        try:
            result = self.session.prompt(prompt_text)
            self._first_prompt = False
            return result
        except KeyboardInterrupt:
            return ""  # Ctrl+C = cancel current input
        except EOFError:
            return None  # Ctrl+D = quit

    def set_working(self, working: bool = True) -> None:
        """Set working state (changes prompt color)."""
        self._working = working

    def ask_initial(self, question: str) -> str:
        """Ask a one-time question (like goal description)."""
        try:
            return self.session.prompt(
                HTML(f"<b>{question}</b> "),
                bottom_toolbar=self._toolbar,
            )
        except (KeyboardInterrupt, EOFError):
            return ""

    def ask_choice(self, question: str, choices: list[str]) -> str:
        """Ask for a choice from a list."""
        completer = FuzzyWordCompleter(choices)
        try:
            return self.session.prompt(
                HTML(f"  {question} "),
                completer=completer,
                bottom_toolbar=self._toolbar,
            )
        except (KeyboardInterrupt, EOFError):
            return choices[0] if choices else ""

    def update_status(
        self,
        cost_usd: float | None = None,
        total_tokens: int | None = None,
        team_size: int | None = None,
        pm_name: str | None = None,
    ) -> None:
        """Update bottom toolbar values."""
        if cost_usd is not None:
            self.cost_usd = cost_usd
        if total_tokens is not None:
            self.total_tokens = total_tokens
        if team_size is not None:
            self.team_size = team_size
        if pm_name is not None:
            self.pm_name = pm_name

    def _build_prompt(self) -> HTML:
        parts = []
        if self.project_name:
            parts.append(f"<prompt.project>{self.project_name}</prompt.project>")
        if self.pm_name:
            short_pm = self.pm_name.split()[0] if self.pm_name else ""
            parts.append(f"<prompt.pm>{short_pm}</prompt.pm>")

        prefix = "/".join(parts)
        # Green when ready, yellow when working
        arrow_color = "#d7af5f" if self._working else "#87d787"
        if prefix:
            return HTML(f"<prompt>[{prefix}]</prompt> <style fg='{arrow_color}' bold='true'>&gt;</style> ")
        return HTML(f"<style fg='{arrow_color}' bold='true'>&gt;</style> ")

    def _toolbar(self) -> HTML:
        parts = []
        if self.pm_name:
            parts.append(f"<key>PM:</key> <value>{self.pm_name}</value>")
        if self.team_size:
            parts.append(f"<key>Team:</key> <value>{self.team_size}</value>")
        if self.total_tokens:
            parts.append(f"<key>Tokens:</key> <value>{self.total_tokens:,}</value>")
        parts.append(f"<key>Cost:</key> <value>${self.cost_usd:.4f}</value>")

        hint = "  alt+enter: newline | /help | /commit | /quit" if self._first_prompt else ""

        return HTML(" | ".join(parts) + f"  <prompt.project>{hint}</prompt.project>")

    def _create_bindings(self) -> KeyBindings:
        bindings = KeyBindings()

        @bindings.add("c-l")
        def clear_screen(event):
            """Ctrl+L: clear screen."""
            event.app.renderer.clear()

        return bindings
