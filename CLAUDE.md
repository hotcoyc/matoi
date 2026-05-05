# 纏 Matoi

A CLI platform where AI agents work as a complete startup team.

## Project Structure

- `src/matoi/` — main platform code
  - `cli/` — CLI Layer (Typer), commands `matoi roster|team|task|session`, REPL (`session_repl.py`)
  - `core/` — Pydantic domain models (agent, team, task, session, cost, config, scanner)
  - `orchestrator/` — Advisory pipeline, dispatch (execution mode), debate engine, conflict detection, synthesis
    - `pipeline.py` — Advisory mode (brief->expert->conflict->debate->synthesis)
    - `dispatch.py` — Execution mode (/execute: PM decomposes->agents execute subtasks)
    - `conflict.py` — Conflict detection
    - `debate.py` — Structured debate engine
    - `synthesis.py` — PM synthesis
  - `agents/` — Agent Runtime: registry (.md parser), activation logic
  - `storage/` — Artifacts writer, session persistence, cost tracking (SQLite/JSON)
  - `gateway/` — Model Gateway: cost-intelligent routing, Anthropic SDK wrapper
- `agents/` — Agent registry: 17 .md files with YAML frontmatter (4 PMs, 6 executors, 5 thinkers, 2 critics)
- `teams/` — Team presets (.yaml)
- `assets/avatars/` — Inline PNG avatars (Warp/iTerm2/Kitty) + Braille .txt fallback
- `artifacts/` — Output artifacts (brief.md, decision.md, debate.md, tasks.json, cost.json)
- `tests/` — pytest
- `docs/` — Project documentation and research

## Conventions

- Python 3.11+, type hints everywhere
- Pydantic v2 for all data models
- Typer for CLI, Rich for terminal rendering (markdown, tables, panels)
- Questionary for interactive menus (arrow-key select, checkbox)
- alive-progress for animated spinners during pipeline stages
- prompt_toolkit for REPL (autocomplete, history, status bar)
- Anthropic Python SDK (not Agent SDK) — full control over each call
- Agent definitions: Markdown + YAML frontmatter, one file per agent
- Code and comment language: English
- Documentation language: English

## Key Principles

- Debate for quality, not for show — arguments only when real conflicts exist
- Artifacts > conversations — the result = files, not chat text
- Cost-aware — Haiku for routine, Sonnet for work, Opus for strategy
- PM is in charge — not chaotic peer-to-peer, but a managed pipeline

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
