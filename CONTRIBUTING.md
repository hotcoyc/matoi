# Contributing to Matoi

Thanks for the interest. Matoi is in alpha (0.3.x), so APIs and on-disk
formats may shift. PRs and issues are welcome.

## Development setup

```bash
git clone <repo>
cd ai-agency-platform
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run locally:

```bash
matoi
```

Run tests and lint:

```bash
pytest
ruff check src tests
```

## Project layout

- `src/matoi/cli/` — Typer + Rich + prompt_toolkit + Questionary
- `src/matoi/core/` — Pydantic models
- `src/matoi/orchestrator/` — pipeline, dispatch, debate, conflict, synthesis, compaction
- `src/matoi/agents/` — registry, activation
- `src/matoi/storage/` — artifacts, sessions, cost tracking
- `src/matoi/gateway/` — Anthropic SDK + model routing
- `agents/` — 17 agent `.md` files (YAML frontmatter)
- `teams/` — team presets (`.yaml`)
- `tests/` — pytest

## Conventions

- Python 3.11+, type hints everywhere.
- Pydantic v2 for all data models.
- Anthropic Python SDK (not Agent SDK).
- Code, comments, docs, and commit messages: English.
- One agent = one `.md` file with YAML frontmatter.
- Per-project state lives in `.matoi/` (memory, artifacts, config).
- Version is owned by `pyproject.toml`; do not duplicate the number in docs or code.

## Commit and PR style

- Commit messages: short imperative subject (`Fix: ...`, `Add: ...`, `Release vX.Y.Z`).
  See `git log --oneline` for prior style.
- One logical change per PR. Bundle docs touch-ups with the feature they describe.
- Update `CHANGELOG.md` under the next unreleased version (or under the current
  pre-release version, if you're cutting it).

## Releasing

1. Bump `version` in `pyproject.toml`.
2. Add a `CHANGELOG.md` entry.
3. Commit as `Release vX.Y.Z`.
4. Tag and publish (process TBD — see release plan).

## Reporting issues

Include: Matoi version (`pip show matoi`), Python version, OS, the command you
ran, and the full traceback. For pipeline issues, include the artifact files
from `.matoi/artifacts/` if you can.
