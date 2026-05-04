# 纏 Matoi

CLI-платформа, где AI-агенты работают как полная стартап-команда.

## Project Structure

- `src/matoi/` — основной код платформы
  - `cli/` — CLI Layer (Typer), команды `matoi roster|team|task|session`
  - `core/` — Pydantic domain models (agent, team, task, session, cost)
  - `orchestrator/` — 7-stage pipeline, debate engine, conflict detection, synthesis
  - `agents/` — Agent Runtime: registry (.md parser), context builder, activation logic
  - `storage/` — Artifacts writer, session persistence, cost tracking (SQLite/JSON)
  - `gateway/` — Model Gateway: cost-intelligent routing, Anthropic SDK wrapper
- `agents/` — Agent registry: .md files with YAML frontmatter (coordinators, executors, thinkers, critics)
- `teams/` — Team presets (.yaml)
- `assets/avatars/` — Braille-арт персонажей PM
- `artifacts/` — Output artifacts (brief.md, decision.md, debate.md, tasks.json, cost.json)
- `tests/` — pytest
- `docs/` — проектная документация и ресерч

## Conventions

- Python 3.11+, type hints everywhere
- Pydantic v2 for all data models
- Typer for CLI, Rich for terminal output
- Anthropic Python SDK (not Agent SDK) — full control over each call
- Agent definitions: Markdown + YAML frontmatter, one file per agent
- Язык кода и комментариев: English
- Язык документации: Russian

## Key Principles

- Debate ради качества, не ради шоу — спор только при реальных конфликтах
- Артефакты > разговоры — результат = файлы, не текст чата
- Cost-aware — Haiku для рутины, Sonnet для работы, Opus для стратегии
- PM управляет — не хаотичный peer-to-peer, а управляемый pipeline

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
