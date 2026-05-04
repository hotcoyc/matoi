# 纏 Matoi — Project Description

*Matoi (纏) — a Japanese firefighter's standard, around which the team rallies.*

---

## What It Is

A CLI platform where AI agents work as a complete startup team. A solo founder gets a virtual team — strategists, researchers, marketers, designers, engineers — who interact, argue on substance, and produce ready-made artifacts.

## The Problem

1. **One AI = one bias.** It doesn't argue with itself, doesn't show alternatives
2. **Solo founder without a team.** You need a researcher, marketer, engineer, QA — hiring is not an option
3. **LLMs are either expensive or bad.** Opus for everything = expensive, Haiku for everything = shallow
4. **Context is lost.** After a session — nothing, no audit trail for decisions
5. **All AI competitors are code-only.** MetaGPT, CrewAI, gstack — dev team, not startup team

## How It Works

```bash
# Initialize in any project
cd ~/my-project
matoi                # API key -> scan -> code graph -> team assembly

# Run a task
matoi run "Validate market for AI-powered pet care"
```

**6-stage pipeline:**
1. **Selective Activation** -- Haiku analyzes the task and selects relevant agents from the team. Irrelevant ones are skipped (token savings)
2. **PM Brief** -- PM formulates the goal, constraints, deliverables (Haiku)
3. **Expert Pass** -- each active agent independently provides their opinion (Sonnet/Opus, streaming)
4. **Conflict Detection** -- Haiku scans opinions, finds disagreements (severity >= 0.5)
5. **Debate** -- if conflicts are found: structured rounds (claim/critique/concession/recommendation). If none -- skipped
6. **Synthesis** -- PM synthesizes the decision incorporating debate results (Opus, streaming)

Artifacts: brief.md, opinion_*.md, debate.md, decision.md, cost.json

## 17 Agents in 6 Categories

### Coordinators [PM] -- PM agents with different styles
| Agent | Style | Risk Tolerance |
|-------|-------|---------------|
| **Startup PM** | Speed, ship fast, cut scope | High (0.8) |
| **Delivery PM** | Predictability, decomposition, milestones | Low (0.3) |
| **Enterprise PM** | Documentation, compliance, audit | Minimal (0.1) |
| **Product Strategist PM** | User value, research first | Medium (0.5) |

### Executors [EXE] -- implementation
| Agent | Iron Law |
|-------|---------|
| **Backend Engineer** | No production code without a failing test first |
| **Frontend Engineer** | The user doesn't care about your architecture |
| **Product Designer** | Design it before you build it |
| **Growth Marketer** | Every channel is a hypothesis until the data says otherwise |
| **Content Strategist** | Content without strategy is just noise |
| **DevOps Engineer** | If it's not automated, it's broken |

### Thinkers [THK] -- research and strategy
| Agent | Iron Law |
|-------|---------|
| **Market Researcher** | Data first, opinions second. No claims without sources |
| **Competitive Analyst** | Know your enemy. Then build what they can't copy |
| **Business Analyst** | If you can't model it, you don't understand it |
| **UX Researcher** | Talk to users, not about users |
| **Financial Modeler** | A spreadsheet is a hypothesis. Test it |

### Critics [CRT] -- review and quality
| Agent | Iron Law |
|-------|---------|
| **Security Reviewer** | Trust nothing. Verify everything |
| **QA Strategist** | No completion claims without fresh verification evidence |

## CLI Commands

```bash
matoi                                   # Onboarding: API key, scan, graph, team
matoi run "task"                        # 6-stage pipeline with streaming
matoi run "task" --budget 1.0           # With budget limit
matoi cost                              # Cost breakdown by sessions and models

matoi roster list                       # Table of all 17 agents
matoi roster list --category research   # Filter by category
matoi roster show startup-pm            # Agent card with pixel-art avatar

matoi team create my-startup            # Interactive PM + agent selection
matoi team show my-startup              # Display team with PM avatar
matoi team list                         # All saved teams
matoi team add my-startup backend-engineer   # Add an agent
matoi team remove my-startup qa-strategist   # Remove an agent

matoi memory show                       # MemPalace: drawers, wings, rooms
matoi memory search "query"             # Semantic search
matoi memory mine .                     # File indexing
matoi memory wake-up                    # Session startup context

matoi viz graph                         # Dependency graph in browser
matoi viz city                          # 3D code city (CodeCharta)
matoi viz build                         # Rebuild visualizations
matoi viz status                        # Visualization status

matoi task plan "task" --team demo      # Dry run with model routing
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| CLI | Typer + Rich |
| Models | Pydantic v2 |
| LLM | Anthropic Python SDK (not Agent SDK) |
| Agents | Markdown + YAML frontmatter |
| Avatars | Pixel-art PNG → Braille Unicode (Pillow) |
| Memory | MemPalace (ChromaDB + SQLite, 96.6% recall) |
| Code graph | code-review-graph (Tree-sitter, 28 MCP tools) |
| 3D visualization | CodeCharta (.cc.json.gz) |
| Streaming | Anthropic SDK stream(), token-by-token output |
| Tests | pytest |
| Linter | ruff |

## Cost-intelligent routing

| Stage | Model | Price (in/out per 1M) | Purpose |
|-------|-------|---------------------|---------|
| Selective Activation | Haiku | $1 / $5 | Selecting relevant agents |
| Brief | Haiku | $1 / $5 | Task structuring |
| Expert Pass | Sonnet | $3 / $15 | Core expert work |
| Conflict Detection | Haiku | $1 / $5 | Scanning for disagreements |
| Debate | Sonnet | $3 / $15 | Structured rounds on conflicts |
| Synthesis | Opus | $15 / $75 | Critical final decision |

## Architecture (6 layers)

```
CLI Layer (Typer + Rich)
    ↓
Core (Pydantic models: Agent, Team, Task, Session, Cost)
    ↓
Orchestrator (Pipeline, Debate Engine, Conflict Detector, Synthesis)
    ↓
Agent Runtime (Registry, Context Builder, Activation Logic)
    ↓
Storage (Artifacts Writer, Session Store, Cost Tracker)
    ↓
Gateway (Model Router, Anthropic SDK Provider)
```

## Key Principles

1. **Debate for quality, not for show** — arguments only when real conflicts exist
2. **Selective activation** — not all agents are active on every task
3. **Artifacts > conversations** — the result = files (brief.md, decision.md), not chat text
4. **Cost-awareness** — Haiku for routine, Opus for strategy
5. **PM is in charge** — not chaotic peer-to-peer, but a managed pipeline
6. **CLI-first** — the terminal as the primary interface
7. **Visual identity** — pixel-art avatars make agents feel "alive"

## Uniqueness (what competitors lack)

1. **Complete startup, not just a dev team** — research → strategy → design → development → marketing
2. **Structured debate as a formal protocol** — conflict detection → targeted debate → synthesis
3. **PM as a real orchestrator with different strategies** — 4 management styles
4. **Cost-intelligent model routing** — not "expensive for everything", but smart routing
5. **Visual characters in CLI** — pixel-art avatars with personality

## Competitors

All are code/dev-only:
- MetaGPT (67k stars) — pipeline without debate
- CrewAI (46k) — generic framework
- gstack (81k) — Claude Code + roles, but dev-only
- Aider (44k) — pair programming, single agent
- ChatDev (33k) — pairwise chat, academic

**Matoi — the first full-startup-team orchestrator.**

---

*One-line pitch: "纏 Matoi — the first CLI platform where AI agents work as a complete startup team: from market validation to product launch."*
