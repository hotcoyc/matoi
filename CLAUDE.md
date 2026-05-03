# AI Agency Platform

CLI-платформа, где AI-агенты работают как полная стартап-команда.

## Project Structure

- `src/agency/` — основной код платформы
  - `cli/` — CLI Layer (Typer), команды `agency agents|team|task|session`
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
