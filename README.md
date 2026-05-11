# Matoi

A CLI platform where AI agents work as a complete startup team: from market validation to product launch -- strategists, researchers, marketers, engineers argue on substance and produce artifacts.

*Matoi -- a Japanese firefighter's standard, around which the team rallies.*

## Why Matoi

**A full startup team, not just a dev tool.**
Every competitor (MetaGPT, CrewAI, gstack, Aider) only covers code. Matoi covers research, strategy, marketing, design, engineering, and QA -- the full startup pipeline from idea validation to launch.

**Agents that actually disagree.**
Not "three agents taking turns agreeing." Conflicts are detected automatically. When agents disagree, structured debate rounds run: claim, critique, concession, recommendation. The PM makes the final call.

**Two modes of work.**
Advisory: "what should we do?" -- the team gives opinions, debates, PM synthesizes.
Execution: "do it" -- PM breaks the task into subtasks, assigns each to the right agent, tracks DONE/BLOCKED status.

**PMs with character.**
Four PMs with genuinely different decision-making styles. Oliver cuts scope and ships fast. Aurora plans milestones and tracks blockers. Marcus demands documentation. Stella asks "but what does the user need?" This is not cosmetic -- it changes the output.

**Cost-intelligent routing.**
Haiku ($1/M) for routine work, Sonnet ($3/M) for expert opinions, Opus ($15/M) for strategic decisions. Not "expensive model for everything." A typical task with 3 agents costs $0.30-0.80.

**Memory that persists.**
MemPalace (96.6% recall) stores decisions, context, and knowledge across sessions. Agents don't start from zero every time. The PM's brief references what the team decided last week.

**Sessions that last for hours.**
Context compaction kicks in at 85% of the window. Old messages are summarized via Haiku (~$0.003). Recent messages stay verbatim. Full history preserved in MemPalace. No degradation, no token explosion.

**Pre-commit debate.**
Type `/commit` and agents review your diff, flag issues, debate disagreements, then commit. Built-in code review by your team before every push.

**Real cost tracking.**
Every API call tracked: agent, stage, model, tokens, cost in USD. Per-session and per-model breakdowns. You always know exactly what you're spending.

**One command to start.**
`pipx install matoi && matoi` -- that's it. API key on first run, project auto-scanned, code graph built, team assembled.

## Quick Start

```bash
pipx install matoi
matoi
```

On first launch, Matoi asks for an Anthropic API key, scans the project, builds a code graph, initializes memory, and offers to assemble a team.

## How It Works

```
$ matoi

_|      _|    _|_|    _|_|_|_|_|    _|_|    _|_|_|
_|_|  _|_|  _|    _|      _|      _|    _|    _|
_|  _|  _|  _|_|_|_|      _|      _|    _|    _|
_|      _|  _|    _|      _|      _|    _|    _|
_|      _|  _|    _|      _|        _|_|    _|_|_|

  ? Choose PM: (use arrow keys)
    > Oliver  -- Startup PM, "Ship it by Friday."
      Aurora  -- Delivery PM, predictability and milestones
      Marcus  -- Enterprise PM, documentation and compliance
      Stella  -- Product Strategist PM, user value first

  What are you working on today? > Design MVP for pet care app
  ? Assemble team: Auto -- PM recommends team

  Team: Backend Engineer, Product Designer, Market Researcher

  [my-project/Oliver] > _
```

You type tasks -- the agent team responds in real time with streaming markdown. Tab autocompletes commands and @agents. Alt+Enter for multiline.

## Two Pipeline Modes

### Advisory Mode (default)

```
1. Selective Activation   -- Haiku picks relevant agents for this task
2. PM Brief               -- PM formulates goal, constraints, deliverables
3. Expert Pass            -- each agent gives opinion (streaming + markdown)
4. Conflict Detection     -- Haiku scans for disagreements (severity >= 0.5)
5. Debate                 -- structured rounds if conflicts found, skipped if not
6. Synthesis              -- PM decides, incorporating debate results
```

### Execution Mode (/execute)

```
/execute Build authentication module

PM decomposes -> 4 subtasks:
  [DONE]    Backend Engineer: design auth schema
  [DONE]    Security Reviewer: threat model
  [BLOCKED] Frontend Engineer: login UI (waiting on schema)
  [DONE]    QA Strategist: test plan
```

### Context Compaction

```
Session: 15 tasks, 50+ agent responses
  -> context at 85% (170K tokens)
  -> old messages compressed to summary (500 tokens)
  -> last 6 messages kept as-is
  -> session continues without degradation
```

## 17 Agents

**PM** -- 4 management styles:

| Name | Role | Style |
|------|------|-------|
| Oliver | Startup PM | Speed, ship fast, cut scope |
| Aurora | Delivery PM | Predictability, milestones |
| Marcus | Enterprise PM | Documentation, compliance |
| Stella | Product Strategist PM | User value first |

**Executors** -- implementation:

| Agent | Principle |
|-------|---------|
| Backend Engineer | No production code without a failing test first |
| Frontend Engineer | The user doesn't care about your architecture |
| Product Designer | Design it before you build it |
| Growth Marketer | Every channel is a hypothesis |
| Content Strategist | Content without strategy is just noise |
| DevOps Engineer | If it's not automated, it's broken |

**Thinkers** -- research and strategy:

| Agent | Principle |
|-------|---------|
| Market Researcher | Data first, opinions second |
| Competitive Analyst | Know your enemy. Build what they can't copy |
| Business Analyst | If you can't model it, you don't understand it |
| UX Researcher | Talk to users, not about users |
| Financial Modeler | A spreadsheet is a hypothesis. Test it |

**Critics** -- review and quality:

| Agent | Principle |
|-------|---------|
| Security Reviewer | Trust nothing. Verify everything |
| QA Strategist | No completion claims without verification evidence |

Each agent is a `.md` file with YAML frontmatter: role, debate style, model policy, strengths, weaknesses, activation rules.

## Session Commands

```
/help      -- all commands
/team      -- current team
/agents    -- all 17 agents
/cost      -- session cost breakdown
/history   -- tasks in this session
/standup   -- generate session summary
/execute   -- PM decomposes task, agents execute subtasks
/commit    -- review diff -> debate -> commit -> update graph
/key       -- change API key
exit       -- exit session (also: quit, q, Ctrl+D)
```

On session exit, a standup is auto-generated: what was done, decisions made, blockers, next steps. Saved as artifact, indexed in MemPalace.

## Cost Routing

| Stage | Model | Price (in/out per 1M) |
|-------|-------|---------------------|
| Activation, Brief, Conflict Detection, Compaction | Haiku | $1 / $5 |
| Expert Pass, Debate | Sonnet | $3 / $15 |
| Synthesis | Opus | $15 / $75 |

Typical task with 3 agents, no debate: $0.30-0.80.

## Integrations

| Tool | What It Does |
|------|-------------|
| **Anthropic API** | Streaming LLM calls, cost routing, retry with backoff |
| **MemPalace** | Memory: semantic search (96.6% recall), knowledge graph, auto-save |
| **code-review-graph** | AI code navigation: 28 MCP tools, auto-update on commit |
| **CodeCharta** | 3D code architecture visualization |
| **Questionary** | Arrow-key select, checkbox menus for PM/team selection |
| **alive-progress** | Animated spinners during pipeline stages |
| **prompt_toolkit** | REPL: autocomplete, history, status bar |
| **Rich** | Live markdown rendering, tables, panels |

## Project Structure

```
src/matoi/
  cli/           -- Typer + Rich + prompt_toolkit + Questionary
  core/          -- Pydantic models (Agent, Team, Task, Cost, Config)
  orchestrator/  -- Pipeline, Dispatch, Debate, Conflict, Compaction
  agents/        -- Registry, Activation, Runtime
  storage/       -- MemPalace wrapper, Artifacts, Costs
  gateway/       -- Anthropic SDK, ModelRouter, Pricing

agents/          -- 17 agent .md files (YAML frontmatter)
assets/avatars/  -- pixel-art PNG avatars
```

## Requirements

- Python 3.11+
- Anthropic API key
- Optional: CodeCharta (Java 17+ for 3D visualization)
