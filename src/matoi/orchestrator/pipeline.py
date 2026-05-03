"""MVP orchestration pipeline.

Simplified 3-stage pipeline for first working version:
1. PM Brief — PM formulates goal, constraints, deliverables
2. Expert Pass — each active agent gives independent opinion
3. Synthesis — PM synthesizes final decision from all opinions

Conflict detection and debate will be added later.
"""

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel

from matoi.agents.registry import AgentRegistry
from matoi.core.agent import AgentDefinition
from matoi.core.cost import Budget
from matoi.core.team import TeamConfig
from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import ModelRouter
from matoi.storage.costs import CostTracker
from matoi.storage.memory import MemoryStore

console = Console()


class MVPPipeline:
    """3-stage MVP pipeline: brief → expert pass → synthesis."""

    def __init__(
        self,
        team: TeamConfig,
        registry: AgentRegistry,
        provider: AnthropicProvider,
        router: ModelRouter,
        output_dir: Path,
        memory: MemoryStore | None = None,
        budget: Budget | None = None,
    ) -> None:
        self.team = team
        self.registry = registry
        self.provider = provider
        self.router = router
        self.output_dir = output_dir
        self.memory = memory
        self.cost_tracker = CostTracker(budget or Budget())

    def run(self, task_description: str) -> Path:
        """Execute the full pipeline. Returns path to artifacts directory."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:6]
        session_dir = self.output_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        pm = self.registry.get(self.team.pm)
        if not pm:
            console.print(f"[red]PM '{self.team.pm}' not found in registry.[/red]")
            raise SystemExit(1)

        agents = []
        for slug in self.team.agents:
            agent = self.registry.get(slug)
            if agent:
                agents.append(agent)
            else:
                console.print(f"[yellow]Agent '{slug}' not found, skipping.[/yellow]")

        # ── Load memory context ──
        memory_context = ""
        if self.memory:
            memory_context = self.memory.get_context(task_description)
            if memory_context:
                console.print(Panel(
                    f"[dim]{len(self.memory.graph.nodes)} nodes in knowledge graph, "
                    f"injecting relevant context[/dim]",
                    title="🧠 Memory",
                    border_style="magenta",
                ))

        # ── Stage 1: PM Brief ──
        console.print()
        console.print(Panel(
            f"[bold]{task_description}[/bold]",
            title="纏 Task",
            border_style="white",
        ))
        console.print()

        brief = self._stage_brief(pm, task_description, memory_context)
        (session_dir / "brief.md").write_text(f"# Brief by {pm.name}\n\n{brief}")
        console.print(Panel(brief, title=f"[bold]📋 Brief by {pm.name}[/bold]", border_style="cyan"))

        # ── Stage 2: Expert Pass ──
        opinions: dict[str, str] = {}
        for agent in agents:
            if self.cost_tracker.is_over_budget():
                console.print("[yellow]Budget limit reached, skipping remaining agents.[/yellow]")
                break
            opinion = self._stage_expert_pass(agent, task_description, brief)
            opinions[agent.slug] = opinion

            (session_dir / f"opinion_{agent.slug}.md").write_text(
                f"# {agent.name}\n\n{opinion}"
            )
            console.print(Panel(
                opinion,
                title=f"[bold]{_type_icon(agent)} {agent.name}[/bold]",
                border_style="dim",
            ))

        # ── Stage 3: Synthesis ──
        decision = self._stage_synthesis(pm, task_description, brief, opinions)
        (session_dir / "decision.md").write_text(f"# Decision by {pm.name}\n\n{decision}")
        console.print(Panel(
            decision,
            title=f"[bold]🎯 Decision by {pm.name}[/bold]",
            border_style="green",
        ))

        # ── Cost summary ──
        cost_summary = self.cost_tracker.summary()
        cost_text = (
            f"Total cost: ${cost_summary['total_cost_usd']}\n"
            f"API calls: {cost_summary['total_calls']}\n"
            f"Premium calls: {cost_summary['premium_calls']}\n"
            f"Budget remaining: ${cost_summary['budget_remaining_usd']}"
        )
        (session_dir / "cost.json").write_text(json.dumps(cost_summary, indent=2))
        console.print()
        console.print(Panel(cost_text, title="💰 Cost", border_style="dim"))

        # ── Memory extraction ──
        if self.memory:
            artifacts = {"brief": brief, "decision": decision}
            for slug, opinion in opinions.items():
                agent = self.registry.get(slug)
                name = agent.name if agent else slug
                artifacts[f"opinion by {name}"] = opinion

            new_nodes = self.memory.extract_and_store(
                session_id=session_id,
                artifacts=artifacts,
                provider=self.provider,
            )
            if new_nodes:
                node_labels = ", ".join(n.label for n in new_nodes[:5])
                console.print(Panel(
                    f"Extracted {len(new_nodes)} nodes: {node_labels}",
                    title="🧠 Memory Updated",
                    border_style="magenta",
                ))

        console.print(f"\n[dim]Artifacts saved to: {session_dir}[/dim]\n")

        return session_dir

    def _stage_brief(self, pm: AgentDefinition, task: str, memory_context: str = "") -> str:
        """PM creates a brief from the raw task."""
        model_id = self.router.resolve_model(pm, "brief")
        system = (
            f"You are {pm.name}, a {pm.role}.\n"
            f"Motto: \"{pm.motto}\"\n\n"
            f"{pm.system_prompt}\n\n"
            "Your task: create a brief for the team. Include:\n"
            "1. Goal — what we're trying to achieve\n"
            "2. Constraints — budget, time, scope limits\n"
            "3. Deliverables — what the team should produce\n"
            "4. Open questions — what we don't know yet\n\n"
            "Be concise and actionable."
        )

        user_msg = task
        if memory_context:
            user_msg = f"{task}\n\n{memory_context}"

        with console.status(f"[bold cyan]{pm.name}[/bold cyan] is writing the brief..."):
            text, cost = self.provider.call(model_id, system, user_msg)

        cost.agent_slug = pm.slug
        cost.stage = "brief"
        self.cost_tracker.record(cost)
        return text

    def _stage_expert_pass(
        self, agent: AgentDefinition, task: str, brief: str
    ) -> str:
        """Agent gives independent opinion on the task."""
        model_id = self.router.resolve_model(agent, "expert_pass")
        system = (
            f"You are {agent.name}, a {agent.role}.\n"
            f"Motto: \"{agent.motto}\"\n\n"
            f"{agent.system_prompt}\n\n"
            "You are part of a team working on a task. "
            "Give your independent expert opinion. Include:\n"
            "1. Your understanding of the task\n"
            "2. Your specific recommendations from your area of expertise\n"
            "3. Risks and concerns you see\n"
            "4. What you disagree with or would do differently\n\n"
            "Be specific and actionable. Don't repeat what others said."
        )
        user_msg = f"## Task\n{task}\n\n## PM Brief\n{brief}"

        with console.status(f"[bold]{_type_icon(agent)} {agent.name}[/bold] is thinking..."):
            text, cost = self.provider.call(model_id, system, user_msg)

        cost.agent_slug = agent.slug
        cost.stage = "expert_pass"
        self.cost_tracker.record(cost)
        return text

    def _stage_synthesis(
        self,
        pm: AgentDefinition,
        task: str,
        brief: str,
        opinions: dict[str, str],
    ) -> str:
        """PM synthesizes final decision from all opinions."""
        model_id = self.router.resolve_model(pm, "synthesis")

        opinions_text = ""
        for slug, opinion in opinions.items():
            agent = self.registry.get(slug)
            name = agent.name if agent else slug
            opinions_text += f"\n### {name}\n{opinion}\n"

        system = (
            f"You are {pm.name}, a {pm.role}.\n"
            f"Motto: \"{pm.motto}\"\n\n"
            f"{pm.system_prompt}\n\n"
            "Synthesize a final decision from the team's opinions. Include:\n"
            "1. **Decision** — what we're going to do\n"
            "2. **Rationale** — why this approach, considering all opinions\n"
            "3. **Rejected alternatives** — what we considered but didn't choose\n"
            "4. **Risks** — what could go wrong\n"
            "5. **Next steps** — concrete action items\n\n"
            "Be decisive. Pick a direction, don't hedge."
        )
        user_msg = (
            f"## Original Task\n{task}\n\n"
            f"## Brief\n{brief}\n\n"
            f"## Team Opinions\n{opinions_text}"
        )

        with console.status(f"[bold green]{pm.name}[/bold green] is synthesizing the decision..."):
            text, cost = self.provider.call(model_id, system, user_msg)

        cost.agent_slug = pm.slug
        cost.stage = "synthesis"
        self.cost_tracker.record(cost)
        return text


def _type_icon(agent: AgentDefinition) -> str:
    icons = {
        "coordinator": "👔",
        "executor": "⚙️",
        "thinker": "🧠",
        "critic": "🔍",
    }
    return icons.get(agent.agent_type.value, "")
