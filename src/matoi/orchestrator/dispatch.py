"""Subagent-driven task execution.

PM breaks a task into subtasks, assigns each to a specific agent,
critic agents review results. Agents return statuses:
DONE, DONE_WITH_CONCERNS, BLOCKED, NEEDS_CONTEXT.
"""

import json
import re
from pathlib import Path

from rich.console import Console
from rich.table import Table

from matoi.agents.registry import AgentRegistry
from matoi.core.agent import AgentDefinition
from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import MODEL_MAP, ModelRouter
from matoi.core.agent import ModelTier

console = Console()

DECOMPOSE_PROMPT = """\
You are {name}, a {role}.
Break this task into 2-5 concrete subtasks.
For each subtask, assign the best agent from the available team.

Available agents:
{agents_list}

Return ONLY a JSON array:
[
  {{"subtask": "description", "agent": "agent-slug", "reason": "why this agent"}}
]

No markdown fences. No explanation. Just JSON.
"""


class SubtaskResult:
    """Result of a subtask execution."""
    def __init__(self, subtask: str, agent_slug: str, status: str, output: str) -> None:
        self.subtask = subtask
        self.agent_slug = agent_slug
        self.status = status  # DONE, DONE_WITH_CONCERNS, BLOCKED, NEEDS_CONTEXT
        self.output = output


class SubagentDispatcher:
    """PM decomposes task, dispatches subtasks to agents, collects results."""

    def __init__(
        self,
        pm: AgentDefinition,
        agents: list[AgentDefinition],
        registry: AgentRegistry,
        provider: AnthropicProvider,
        router: ModelRouter,
    ) -> None:
        self.pm = pm
        self.agents = agents
        self.registry = registry
        self.provider = provider
        self.router = router
        self._agent_map = {a.slug: a for a in agents}

    def execute(self, task: str, call_agent_fn) -> list[SubtaskResult]:
        """Decompose task and execute subtasks. Returns results.

        call_agent_fn(agent, stage, user_msg) -> str
        is provided by the session to handle streaming/display.
        """
        # Step 1: PM decomposes task
        subtasks = self._decompose(task)
        if not subtasks:
            return []

        # Show plan
        console.print()
        table = Table(title="Execution Plan", border_style="dim")
        table.add_column("#", width=3, justify="right")
        table.add_column("Subtask", min_width=30)
        table.add_column("Agent", width=20)

        for i, st in enumerate(subtasks, 1):
            agent = self._agent_map.get(st.get("agent", ""))
            name = agent.name if agent else st.get("agent", "?")
            table.add_row(str(i), st["subtask"][:60], name)

        console.print(table)
        console.print()

        # Step 2: Execute each subtask
        results = []
        for i, st in enumerate(subtasks, 1):
            agent_slug = st.get("agent", "")
            agent = self._agent_map.get(agent_slug)
            if not agent:
                results.append(SubtaskResult(
                    st["subtask"], agent_slug, "BLOCKED",
                    f"Agent '{agent_slug}' not in team.",
                ))
                continue

            console.rule(f"[dim]Subtask {i}/{len(subtasks)}: {agent.name}[/dim]")

            user_msg = (
                f"## Your subtask\n{st['subtask']}\n\n"
                f"## Context (original task)\n{task}\n\n"
                f"## Working directory\n{Path.cwd()}\n\n"
                "IMPORTANT: If your subtask requires writing code, include the FULL file content "
                "in a code block with the filename as the language tag. Example:\n"
                "```index.html\n<full file content here>\n```\n"
                "```style.css\n<full file content here>\n```\n\n"
                "Write complete, working files. No placeholders, no TODOs, no truncation.\n\n"
                "At the end, state your status:\n"
                "- DONE -- if completed successfully\n"
                "- DONE_WITH_CONCERNS -- if done but you have concerns\n"
                "- BLOCKED -- if you can't proceed\n"
                "- NEEDS_CONTEXT -- if you need more information"
            )

            output = call_agent_fn(agent, "expert_pass", user_msg)

            # Extract and write files from code blocks
            written = _extract_and_write_files(output, Path.cwd())
            if written:
                console.print(f"  [green]Wrote {len(written)} file(s): {', '.join(written)}[/green]")

            # Extract status from output
            status = "DONE"
            for s in ["BLOCKED", "NEEDS_CONTEXT", "DONE_WITH_CONCERNS"]:
                if s in output.upper():
                    status = s
                    break

            results.append(SubtaskResult(st["subtask"], agent_slug, status, output))

        # Step 3: Summary
        self._show_results(results)
        return results

    def _decompose(self, task: str) -> list[dict]:
        """PM breaks task into subtasks with agent assignments."""
        agents_list = ""
        for a in self.agents:
            agents_list += f"- {a.slug}: {a.name} ({a.role})\n"

        prompt = DECOMPOSE_PROMPT.format(
            name=self.pm.name,
            role=self.pm.role,
            agents_list=agents_list,
        )

        model_id = MODEL_MAP[self.pm.model_policy.brief]

        try:
            from alive_progress import alive_bar
            with alive_bar(title=f"  {self.pm.name} planning subtasks", bar=False, spinner="dots_waves"):
                text, _ = self.provider.call(model_id, prompt, task, max_tokens=500)
        except ImportError:
            text, _ = self.provider.call(model_id, prompt, task, max_tokens=500)

        # Parse JSON
        try:
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            console.print("  [yellow]Could not parse subtask plan.[/yellow]")
            return []

    def _show_results(self, results: list[SubtaskResult]) -> None:
        """Show summary of subtask results."""
        console.print()
        table = Table(title="Results", border_style="dim")
        table.add_column("Subtask", min_width=30)
        table.add_column("Agent", width=20)
        table.add_column("Status", width=20)

        status_colors = {
            "DONE": "green",
            "DONE_WITH_CONCERNS": "yellow",
            "BLOCKED": "red",
            "NEEDS_CONTEXT": "magenta",
        }

        for r in results:
            agent = self._agent_map.get(r.agent_slug)
            name = agent.name if agent else r.agent_slug
            color = status_colors.get(r.status, "white")
            table.add_row(r.subtask[:50], name, f"[{color}]{r.status}[/{color}]")

        console.print(table)

        blocked = [r for r in results if r.status in ("BLOCKED", "NEEDS_CONTEXT")]
        if blocked:
            console.print(f"\n  [yellow]{len(blocked)} subtask(s) need attention.[/yellow]")


def _extract_and_write_files(output: str, cwd: Path) -> list[str]:
    """Extract code blocks with filenames and write to disk.

    Looks for patterns like:
    ```filename.ext
    <content>
    ```
    """
    written = []
    # Match ```filename\n...\n```
    pattern = r"```(\S+\.\w+)\n(.*?)```"
    matches = re.findall(pattern, output, re.DOTALL)

    for filename, content in matches:
        # Skip non-file language tags
        if filename in ("bash", "shell", "sh", "python", "json", "yaml", "text", "plaintext",
                         "javascript", "typescript", "html", "css", "sql", "markdown", "md"):
            continue

        # Safety: no path traversal
        if ".." in filename or "/" in filename:
            continue

        filepath = cwd / filename
        try:
            filepath.write_text(content.strip() + "\n")
            written.append(filename)
        except Exception:
            pass

    return written
