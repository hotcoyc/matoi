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

        all_agents = []
        for slug in self.team.agents:
            agent = self.registry.get(slug)
            if agent:
                all_agents.append(agent)
            else:
                console.print(f"[yellow]Agent '{slug}' not found, skipping.[/yellow]")

        # ── Selective activation ──
        if len(all_agents) > 2:
            from matoi.agents.activation import ActivationEngine
            activator = ActivationEngine(self.provider)
            agents = activator.select_active(all_agents, task_description)
            if len(agents) < len(all_agents):
                active_names = ", ".join(a.name for a in agents)
                skipped = [a.name for a in all_agents if a not in agents]
                console.print(f"  [dim]Active: {active_names}[/dim]")
                console.print(f"  [dim]Skipped: {', '.join(skipped)}[/dim]")
            else:
                console.print(f"  [dim]All {len(agents)} agents active[/dim]")
        else:
            agents = all_agents

        # ── Load memory context ──
        memory_context = ""
        if self.memory:
            memory_context = self.memory.get_context(task_description)
            if memory_context:
                console.print(Panel(
                    "[dim]Injecting relevant context from MemPalace[/dim]",
                    title="Memory",
                    border_style="magenta",
                ))

        # ── Stage 1: PM Brief ──
        console.print()
        console.print(Panel(
            f"[bold]{task_description}[/bold]",
            title="Task",
            border_style="white",
        ))
        console.print()

        console.rule("[bold cyan]Stage 1: Brief[/bold cyan]")
        brief = self._stage_brief(pm, task_description, memory_context)
        (session_dir / "brief.md").write_text(f"# Brief by {pm.name}\n\n{brief}")

        # ── Stage 2: Expert Pass ──
        opinions: dict[str, str] = {}
        for agent in agents:
            if self.cost_tracker.is_over_budget():
                console.print("[yellow]Budget limit reached, skipping remaining agents.[/yellow]")
                break

            console.rule(f"[dim]Stage 2: Expert Pass[/dim]")
            opinion = self._stage_expert_pass(agent, task_description, brief)
            opinions[agent.slug] = opinion

            (session_dir / f"opinion_{agent.slug}.md").write_text(
                f"# {agent.name}\n\n{opinion}"
            )

        # ── Stage 3: Conflict Detection ──
        debate_context = ""
        if len(opinions) >= 2 and not self.cost_tracker.is_over_budget():
            console.rule("[dim]Stage 3: Conflict Detection[/dim]")
            from matoi.orchestrator.conflict import ConflictDetector
            from matoi.orchestrator.debate import DebateEngine

            detector = ConflictDetector(self.provider)
            conflicts = detector.detect(opinions)

            if conflicts:
                console.print(f"  [bold]{len(conflicts)} conflict(s) detected:[/bold]")
                for c in conflicts:
                    console.print(f"    [{c.severity:.1f}] {c.topic} ({', '.join(c.agents)})")
                console.print()

                # ── Stage 4: Debate ──
                console.rule("[dim]Stage 4: Debate[/dim]")
                engine = DebateEngine(
                    provider=self.provider,
                    router=self.router,
                    registry=self.registry,
                    max_rounds=self.cost_tracker.budget.max_debate_rounds,
                )

                all_transcripts = []
                for conflict in conflicts:
                    if self.cost_tracker.is_over_budget():
                        console.print("[yellow]Budget limit reached, skipping remaining debates.[/yellow]")
                        break
                    rounds = engine.run_debate(conflict)
                    transcript = engine.format_transcript(conflict, rounds)
                    all_transcripts.append(transcript)

                if all_transcripts:
                    debate_text = "\n\n---\n\n".join(all_transcripts)
                    (session_dir / "debate.md").write_text(f"# Debate Transcript\n\n{debate_text}")
                    debate_context = f"\n\n## Debate Results\n{debate_text}"
                    console.print()
            else:
                console.print("  [dim]No significant conflicts found. Skipping debate.[/dim]")
                console.print()

        # ── Stage 5: Synthesis ──
        console.rule("[bold green]Stage 5: Synthesis[/bold green]")
        decision = self._stage_synthesis(pm, task_description, brief, opinions, debate_context)
        (session_dir / "decision.md").write_text(f"# Decision by {pm.name}\n\n{decision}")

        # ── Cost summary ──
        cost_summary = self.cost_tracker.summary()
        (session_dir / "cost.json").write_text(json.dumps(cost_summary, indent=2))
        console.print()
        _render_cost_table(cost_summary)

        # ── Index artifacts into MemPalace ──
        if self.memory:
            count = self.memory.store_artifacts(session_id, session_dir)
            if count > 0:
                console.print(Panel(
                    f"Indexed {count} drawers into MemPalace",
                    title="Memory Updated",
                    border_style="magenta",
                ))

            # Add key decision to knowledge graph
            self.memory.add_to_knowledge_graph(
                subject=f"session:{session_id}",
                predicate="decided",
                obj=decision[:200],
                source_file=str(session_dir / "decision.md"),
            )

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
            "Be concise. Max 150 words. No self-introductions. Adapt to complexity -- simple task = simple brief. Do NOT add compliance gates for straightforward tasks."
        )

        user_msg = task
        if memory_context:
            user_msg = f"{task}\n\n{memory_context}"

        text, cost = _stream_call(
            self.provider, model_id, system, user_msg,
            label=f"{pm.name} -- brief",
        )
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
            "Be concise. Max 200 words. No self-introductions. Go straight to recommendations. If the task is clear, do the work -- don't ask for more context."
        )
        user_msg = f"## Task\n{task}\n\n## PM Brief\n{brief}"

        text, cost = _stream_call(
            self.provider, model_id, system, user_msg,
            label=f"{_type_icon(agent)} {agent.name}",
        )
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
        debate_context: str = "",
    ) -> str:
        """PM synthesizes final decision from all opinions and debate results."""
        model_id = self.router.resolve_model(pm, "synthesis")

        opinions_text = ""
        for slug, opinion in opinions.items():
            agent = self.registry.get(slug)
            name = agent.name if agent else slug
            opinions_text += f"\n### {name}\n{opinion}\n"

        debate_instruction = ""
        if debate_context:
            debate_instruction = (
                "\nIMPORTANT: The team debated specific conflicts. "
                "Address each debated topic explicitly in your decision. "
                "Explain which side you chose and why.\n"
            )

        system = (
            f"You are {pm.name}, a {pm.role}.\n"
            f"Motto: \"{pm.motto}\"\n\n"
            f"{pm.system_prompt}\n\n"
            "Synthesize a final decision from the team's opinions. Include:\n"
            "1. **Decision** -- what we're going to do\n"
            "2. **Rationale** -- why this approach, considering all opinions\n"
            "3. **Rejected alternatives** -- what we considered but didn't choose\n"
            "4. **Risks** -- what could go wrong\n"
            "5. **Next steps** -- concrete action items\n"
            f"{debate_instruction}\n"
            "Be decisive. Pick a direction, don't hedge."
        )
        user_msg = (
            f"## Original Task\n{task}\n\n"
            f"## Brief\n{brief}\n\n"
            f"## Team Opinions\n{opinions_text}"
            f"{debate_context}"
        )

        text, cost = _stream_call(
            self.provider, model_id, system, user_msg,
            label=f"{pm.name} -- synthesis",
        )
        cost.agent_slug = pm.slug
        cost.stage = "synthesis"
        self.cost_tracker.record(cost)
        return text


def _stream_call(
    provider: AnthropicProvider,
    model_id: str,
    system: str,
    user_msg: str,
    label: str = "",
) -> tuple[str, "CostRecord"]:
    """Stream an LLM call with live markdown rendering. Returns (full_text, cost)."""
    from rich.live import Live
    from rich.markdown import Markdown

    from matoi.core.cost import CostRecord
    from matoi.gateway.provider import APIError

    console.print(f"  [bold]{label}[/bold]")

    full_text = ""
    cost = None

    try:
        with Live(Markdown(""), console=console, refresh_per_second=4) as live:
            for chunk in provider.stream(model_id, system, user_msg):
                if isinstance(chunk, CostRecord):
                    cost = chunk
                else:
                    full_text += chunk
                    try:
                        live.update(Markdown(full_text))
                    except Exception:
                        live.update(full_text)
    except APIError as e:
        console.print(f"\n  [red]API error: {e}[/red]")
        if not e.retryable:
            console.print("  [dim]This error is not retryable.[/dim]")
    except Exception as e:
        console.print(f"\n  [red]Error: {e}[/red]")

    console.print()

    if cost is None:
        cost = CostRecord(
            agent_slug="", stage="",
            model_tier=provider._infer_tier(model_id),
            model_id=model_id,
        )

    return full_text, cost


def _type_icon(agent: AgentDefinition) -> str:
    icons = {
        "coordinator": "[PM]",
        "executor": "[EXE]",
        "thinker": "[THK]",
        "critic": "[CRT]",
    }
    return icons.get(agent.agent_type.value, "")


def _render_cost_table(cost_summary: dict) -> None:
    """Render a detailed cost breakdown table."""
    from rich.table import Table

    breakdown = cost_summary.get("breakdown", [])

    table = Table(title="Cost Breakdown", border_style="dim", show_lines=False)
    table.add_column("Agent", style="bold", min_width=18)
    table.add_column("Stage", width=12)
    table.add_column("Model", width=28)
    table.add_column("In tokens", justify="right", width=10)
    table.add_column("Out tokens", justify="right", width=10)
    table.add_column("Cost", justify="right", style="yellow", width=10)

    for row in breakdown:
        model_short = row["model"].replace("claude-", "").replace("-20251001", "")
        table.add_row(
            row["agent"],
            row["stage"],
            model_short,
            f"{row['input_tokens']:,}",
            f"{row['output_tokens']:,}",
            f"${row['cost_usd']:.4f}",
        )

    # Totals row
    table.add_section()
    table.add_row(
        "[bold]Total[/bold]",
        "",
        f"{cost_summary['total_calls']} calls",
        f"{sum(r['input_tokens'] for r in breakdown):,}",
        f"{sum(r['output_tokens'] for r in breakdown):,}",
        f"[bold]${cost_summary['total_cost_usd']:.4f}[/bold]",
    )

    console.print(table)
    console.print(
        f"  [dim]Budget remaining: ${cost_summary['budget_remaining_usd']:.4f} "
        f"| Tokens: {cost_summary.get('total_tokens', 0):,}[/dim]"
    )
