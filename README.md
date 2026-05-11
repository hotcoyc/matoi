# Matoi

A CLI platform where AI agents work as a complete startup team: from market validation to product launch -- strategists, researchers, marketers, engineers argue on substance and produce artifacts.

*Matoi -- a Japanese firefighter's standard, around which the team rallies.*

## Quick Start

```bash
pipx install matoi          # from PyPI
# or
git clone https://github.com/hotcoyc/matoi
cd matoi && pip install -e .

matoi
```

On first launch, Matoi will ask for an Anthropic API key, scan the project, build a code graph, and offer to assemble a team.

## How It Works

```
$ matoi

  Matoi -- your startup team in the terminal.

  API key: ok
  ? Choose PM: (use arrow keys)
    > Oliver  -- Startup PM, "Ship it by Friday."
      Aurora  -- Delivery PM, predictability and milestones
      Marcus  -- Enterprise PM, documentation and compliance
      Stella  -- Product Strategist PM, user value first

  What are you working on today? > Design MVP for pet care app

  Team: Backend Engineer, Product Designer, Market Researcher

  [ai-agency-platform/Oliver] > _
```

You enter tasks -- the agent team responds in real time with markdown rendering. Before a commit, agents review changes and debate if there are disagreements. Long sessions are handled automatically -- old context is compressed when it reaches 85% of the model's window, while full history is preserved in MemPalace.

## Two Pipeline Modes

### Advisory Mode (default)

Each task goes through 5 stages:

```
1. PM Brief              -- PM formulates the task
2. Expert Pass           -- each agent provides their opinion (streaming)
3. Conflict Detection    -- Haiku looks for disagreements
4. Debate                -- structured rounds if conflicts are found
5. Synthesis             -- PM makes the decision incorporating debate results
```

Debates are triggered automatically when agents disagree with each other. If there are no conflicts -- they are skipped.

### Execution Mode (/execute)

PM decomposes the task into subtasks and dispatches them to agents:

```
/execute Build authentication module

PM decomposes -> 4 subtasks:
  [DONE]    Backend Engineer: design auth schema
  [DONE]    Security Reviewer: threat model
  [BLOCKED] Frontend Engineer: login UI (waiting on schema)
  [DONE]    QA Strategist: test plan
```

Each subtask gets a status: DONE or BLOCKED. The PM tracks progress and reports results.

### Context Compaction

Long sessions are handled automatically. When conversation history reaches 85% of the context window (~170K tokens), old messages are summarized via Haiku (~$0.003). Recent messages stay verbatim. Full history is preserved in MemPalace.

```
Session: 15 tasks, 50+ agent responses
  -> context at 85% (170K tokens)
  -> old messages compressed to summary (500 tokens)
  -> last 6 messages kept as-is
  -> session continues without degradation
```

## 17 Agents

**PM [PM]** -- 4 management styles:

| Agent | Name | Style |
|-------|------|-------|
| Startup PM | Oliver | Speed, ship fast, cut scope |
| Delivery PM | Aurora | Predictability, milestones |
| Enterprise PM | Marcus | Documentation, compliance |
| Product Strategist PM | Stella | User value |

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
/standup  -- auto-generated standup notes for the session
/execute  -- PM decomposes task into subtasks, agents execute with DONE/BLOCKED
/commit   -- review -> debate -> commit -> update graph
/key      -- change API key mid-session
/quit     -- exit (Ctrl+D)
```

Tab -- autocomplete for commands and @agents. Alt+Enter -- multiline input.

On session exit, standup notes are auto-generated summarizing what was done, decisions made, and blockers.

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
| **Questionary** | Arrow-key select, checkbox menus (PM/team selection) |
| **alive-progress** | Animated spinners during pipeline stages |

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
