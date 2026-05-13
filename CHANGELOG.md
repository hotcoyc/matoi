# Changelog

All notable changes to Matoi are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Versions match `pyproject.toml`.

## [0.3.10] — 2026-05

- Add `matoi demo` command + VHS tape for recording GIFs.
- 3D city: show full file path so it can be dragged into the viewer.
- Fix: session history in the main menu reads artifacts directly.
- Fix: "Browse agents" in the main menu uses `self.registry` directly.
- README: compact "Why Matoi" table with 13 features.

## [0.3.9] — 2026-05

- Banner: serif "I" with wider top and bottom strokes.
- Docs: main menu, block banner.

## [0.3.8] — 2026-05

- Add main menu before PM selection (graph, 3D city, browse agents, history, start working).

## [0.3.7] — 2026-05

- Copilot-style banner with block characters; spacing fixes for tagline/version/help.
- Show project structure and code graph on first run.
- Auto-add `.matoi/` to `.gitignore` on first run.
- Rename project dir `matoi/` → `.matoi/` (hidden).
- Fix: locate `code-review-graph` binary in pipx venv.

## [0.3.2] — 2026-04

- Per-project memory: `.matoi/memory/` instead of `~/.mempalace/`.
- Docs refresh for per-project memory and cleaner UX.

## [0.3.1] — 2026-04

- Fix MemPalace API: use `mine()` not `mine_directory()`, silent errors.

## [0.3.0] — 2026-04

- Hide ALL code from console; show only descriptions and "Created: filename".

## [0.2.9] — 2026-04

- Replace LLM standup with clean programmatic summary.
- Add descriptions to command autocomplete.
- Fix: team recommendation JSON parsing.

Older versions (0.1.x — 0.2.5): see `git log --grep=Release`.
