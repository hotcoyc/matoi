# Matoi

A CLI platform where AI agents work as a complete startup team: from market validation to product launch -- strategists, researchers, marketers, engineers argue on substance and produce artifacts.

*Matoi -- a Japanese firefighter's standard, around which the team rallies.*

## Quick Start

```bash
git clone <repo-url>
cd matoi
pip install -e .
matoi
```

On first launch, Matoi will ask for an Anthropic API key, scan the project, build a code graph, and offer to assemble a team.

## How It Works

```
$ matoi

  Matoi -- your startup team in the terminal.

  API key: ok
  PM: Startup PM -- "Ship it by Friday."

  What are you working on today? > Design MVP for pet care app

  Team: Backend Engineer, Product Designer, Market Researcher

  [ai-agency-platform/Startup] > _
```

You enter tasks -- the agent team responds in real time with markdown rendering. Before a commit, agents review changes and debate if there are disagreements.

## Pipeline

Each task goes through 6 stages:

```
1. Selective Activation  -- Haiku selects relevant agents
2. PM Brief              -- PM formulates the task
3. Expert Pass           -- each agent provides their opinion (streaming)
4. Conflict Detection    -- Haiku looks for disagreements
5. Debate                -- structured rounds if conflicts are found
6. Synthesis             -- PM makes the decision incorporating debate results
```

Debates are triggered automatically when agents disagree with each other. If there are no conflicts -- they are skipped.

## 17 Agents

**PM [PM]** -- 4 management styles:

| Agent | Style |
|-------|-------|
| Startup PM | Speed, ship fast, cut scope |
| Delivery PM | Predictability, milestones |
| Enterprise PM | Documentation, compliance |
| Product Strategist PM | User value |

**Executors [EXE]** -- implementation:

| Agent | Principle |
|-------|---------|
| Backend Engineer | No production code without a failing test first |
| Frontend Engineer | The user doesn't care about your architecture |
| Product Designer | Design it before you build it |
| Growth Marketer | Every channel is a hypothesis |
| Content Strategist | Content without strategy is just noise |
| DevOps Engineer | If it's not automated, it's broken |

**Thinkers [THK]** -- research:

| Agent | Principle |
|-------|---------|
| Market Researcher | Data first, opinions second |
| Competitive Analyst | Know your enemy. Build what they can't copy |
| Business Analyst | If you can't model it, you don't understand it |
| UX Researcher | Talk to users, not about users |
| Financial Modeler | A spreadsheet is a hypothesis. Test it |

**Critics [CRT]** -- review:

| Agent | Principle |
|-------|---------|
| Security Reviewer | Trust nothing. Verify everything |
| QA Strategist | No completion claims without verification evidence |

Each agent is a `.md` file with YAML frontmatter: role, debate style, model policy, strengths, weaknesses, activation rules.

## Session Commands

```
/help     -- all commands
/team     -- current team
/agents   -- all 17 agents
/cost     -- session cost
/history  -- tasks in this session
/commit   -- review -> debate -> commit -> update graph
/quit     -- exit (Ctrl+D)
```

Tab -- autocomplete for commands and @agents. Alt+Enter -- multiline input.

## CLI Commands

```bash
matoi                          # interactive session
matoi run "task"               # one-shot pipeline
matoi cost                     # cost breakdown by sessions and models

matoi roster list              # agent table
matoi roster show startup-pm   # card with pixel-art avatar

matoi team create              # assemble a team
matoi team show / list         # view teams

matoi memory show              # MemPalace status
matoi memory search "query"    # semantic memory search

matoi viz graph                # dependency graph in browser
matoi viz city                 # 3D code city (CodeCharta)

matoi task plan "task" -t demo  # dry run
```

## Cost Routing

Different models for different stages -- not "expensive for everything":

| Stage | Model | Price (in/out per 1M) |
|-------|-------|---------------------|
| Activation, Brief, Conflict Detection | Haiku | $1 / $5 |
| Expert Pass, Debate | Sonnet | $3 / $15 |
| Synthesis | Opus | $15 / $75 |

A typical task with 3 agents without debate: $0.30-0.80.

## Integrations

| Tool | What It Does |
|------|-------------|
| **Anthropic API** | Streaming LLM calls, cost routing |
| **MemPalace** | Memory: semantic search, knowledge graph, auto-save |
| **code-review-graph** | AI code navigation: 28 MCP tools, auto-update |
| **CodeCharta** | 3D code architecture visualization |
| **prompt_toolkit** | TUI: autocomplete, history, status bar |

## Project Structure

```
src/matoi/
  cli/           -- Typer + Rich + prompt_toolkit
  core/          -- Pydantic models (Agent, Team, Task, Cost, Config)
  orchestrator/  -- Pipeline, ConflictDetector, DebateEngine
  agents/        -- Registry, Activation, Runtime
  storage/       -- MemPalace wrapper, Artifacts, Costs
  gateway/       -- Anthropic SDK, ModelRouter, Pricing

agents/          -- 17 agent .md files (YAML frontmatter)
assets/avatars/  -- pixel-art PNG + Braille .txt
```

## Requirements

- Python 3.11+
- Anthropic API key
- Optional: code-review-graph, CodeCharta (Java 17+), chafa
