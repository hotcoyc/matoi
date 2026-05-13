# Matoi

A CLI platform where AI agents work as a complete startup team: from market validation to product launch -- strategists, researchers, marketers, engineers argue on substance and produce artifacts.

*Matoi -- a Japanese firefighter's standard, around which the team rallies.*

> **Status: alpha (0.3.x).** APIs, command names, and on-disk layout may change between
> minor versions. Requires an Anthropic API key — usage is billed by Anthropic; a typical
> task with 3 agents runs $0.30–0.80 (see [Cost Routing](#cost-routing)).
> Changes per release: [CHANGELOG.md](CHANGELOG.md).

## Contents

- [Why Matoi](#why-matoi)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Two Pipeline Modes](#two-pipeline-modes)
- [17 Agents](#17-agents)
- [CLI Commands](#cli-commands)
- [Session Commands](#session-commands)
- [Cost Routing](#cost-routing)
- [Integrations](#integrations)
- [Project Structure](#project-structure)
- [Requirements](#requirements)

## Why Matoi

| | |
|---|---|
| **Full startup team** | Research, strategy, marketing, design, engineering, QA -- not just code |
| **Structured debate** | Agents disagree, debate, PM decides. Not "three bots agreeing" |
| **Two modes** | Advisory (opinions + synthesis) or Execution (subtasks + DONE/BLOCKED) |
| **4 PM styles** | Oliver ships fast, Aurora plans milestones, Marcus documents, Stella advocates users |
| **Smart routing** | Haiku $1/M, Sonnet $3/M, Opus $15/M -- right model for right task |
| **Per-project memory** | MemPalace in `.matoi/` -- agents remember past decisions |
| **Code graph** | Auto-built dependency graph with 28 MCP tools -- agents navigate code, not files |
| **3D code city** | CodeCharta visualization -- see your codebase as a city of buildings |
| **Long sessions** | Auto-compaction at 85% context -- hours without degradation |
| **Local & private** | `.matoi/` auto-added to `.gitignore` -- AI data never enters your repo |
| **Pre-commit review** | `/commit` -- agents review diff, debate, then commit |
| **Cost tracking** | Every call: agent, model, tokens, USD. Per-session breakdown |
| **One command** | `pipx install matoi && matoi` -- that's it |

## Quick Start

```bash
pipx install matoi
matoi
```

On first launch, Matoi asks for an Anthropic API key, scans the project, builds a code graph, and shows you the main menu.

## How It Works

```
$ matoi

███╗   ███╗ █████╗ ████████╗ ██████╗ ██╗
████╗ ████║██╔══██╗╚══██╔══╝██╔═══██╗██║
██╔████╔██║███████║   ██║   ██║   ██║██║
██║╚██╔╝██║██╔══██║   ██║   ██║   ██║██║
██║ ╚═╝ ██║██║  ██║   ██║   ╚██████╔╝██║
╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝

  Your startup team in the terminal.
  v0.3.10

  Project: my-project
  Files: 42 | Dirs: 8
  Languages: Python (28), JavaScript (6)
  Git: 156 commits

  Code graph: 210 nodes, 1317 edges
  3D city built.

? What would you like to do?
  > Start working -- select PM and team
    View code graph -- open in browser
    View 3D city -- open CodeCharta
    Browse agents -- see all 17 agents
    Session history -- past sessions and costs
    Quit
```

You type tasks -- the agent team works behind a spinner (no live code streaming). Only descriptions and "Created: filename" appear in the console. Tab autocompletes commands and @agents with descriptions. Alt+Enter for multiline.

On repeated launch in the same project, Matoi offers to continue the previous session or start a new one.

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

## CLI Commands

```bash
matoi                                # interactive session
matoi run "task"                     # one-shot pipeline
matoi run "task" --budget 1.0        # with USD budget cap (default: 5.0)
matoi cost                           # cost breakdown by sessions and models
matoi history                        # browse past sessions and artifacts
matoi demo                           # record a demo GIF (requires VHS)

matoi roster list                    # agent table
matoi roster list --category research # filter
matoi roster show startup-pm         # card with pixel-art avatar

matoi team create                    # assemble a team
matoi team add <team> <agent>        # add an agent
matoi team remove <team> <agent>     # remove an agent
matoi team list / show               # view teams
matoi team recommend "task"          # PM suggests a composition

matoi session list                   # recent sessions
matoi session artifacts <id>         # artifacts from a session

matoi memory show                    # MemPalace status
matoi memory search "query"          # semantic memory search
matoi memory mine .                  # index files into memory
matoi memory wake-up                 # startup context (Layer 0 + 1)
matoi memory clear                   # wipe palace + knowledge graph

matoi viz graph                      # dependency graph in browser
matoi viz city                       # 3D code city (CodeCharta)
matoi viz build                      # rebuild all visualizations
matoi viz status                     # visualization status

matoi task plan "task" -t demo       # dry run, no API calls
```

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

On session exit, a summary is printed: files created, tasks completed, debates held, and a cost table with model column. The summary is also saved as an artifact and indexed in MemPalace.

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
| **MemPalace** | Per-project memory: semantic search (96.6% recall), knowledge graph, auto-save |
| **code-review-graph** | AI code navigation: 28 MCP tools, auto-update on commit |
| **CodeCharta** | 3D code architecture visualization |
| **Questionary** | Arrow-key select, checkbox menus for PM/team selection |
| **alive-progress** | Animated spinners during pipeline stages |
| **prompt_toolkit** | REPL: autocomplete, history, status bar |
| **Rich** | Live markdown rendering, tables, panels |

## Project Structure

```
~/my-project/
  .matoi/
    config.json          -- PM + team for this project
    artifacts/           -- standup reports, debate transcripts
    memory/
      palace/            -- MemPalace per-project (semantic search)
      knowledge_graph.sqlite3  -- per-project knowledge graph
  index.html             -- files created by agents (in project root)

~/.matoi/
  config.json            -- API key (global, shared across projects)
  history                -- input history (shared)
```

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
