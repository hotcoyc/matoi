# Third-Party Projects Used

Open-source projects integrated into Matoi.

---

## [MemPalace](https://github.com/mempalace/mempalace) -- agent memory

**What:** A hierarchical memory system for AI agents. ChromaDB + SQLite, semantic search (96.6% recall), knowledge graph with temporal triples.

**How we use it:**
- Cross-session memory -- pipeline artifacts are indexed automatically
- 433 project drawers loaded (code, docs, agents)
- 29 MCP tools for Claude Code
- Auto-save hooks (Stop, PreCompact)
- Knowledge graph for linking decisions
- Python API: `MemoryStack`, `search_memories()`, `KnowledgeGraph`

**License:** MIT | **Stars:** ~51K

---

## [code-review-graph](https://github.com/tirth8205/code-review-graph) -- AI code navigation

**What:** A codebase knowledge graph via Tree-sitter. Builds a map: files, functions, classes, dependencies, calls.

**How we use it:**
- 210 nodes, 1317 edges for our project
- 28 MCP tools for Claude Code (query_graph, detect_changes, get_impact_radius, semantic_search)
- Auto-update via git pre-commit hook and PostToolUse hook
- HTML visualization: `matoi viz graph`
- Token savings of 6.8-49x vs reading entire files

**License:** MIT | **Stars:** ~15K

---

## [CodeCharta](https://github.com/MaibornWolff/codecharta) -- 3D visualization

**What:** Code visualization as a 3D city. Files = buildings (height = complexity, area = lines of code), directories = districts.

**How we use it:**
- `matoi viz city` -- generates `.cc.json.gz` and opens the viewer
- `matoi viz build` -- rebuild during onboarding
- Visual architecture overview for new team members

**Requires:** Java 17+, npm | **License:** BSD-3 | **Stars:** ~411

---

## [Superpowers](https://github.com/obra/superpowers) -- agent behavioral patterns

**What:** An agentic skills framework with Iron Laws, self-review checklists, escalation rules.

**How we use it:**
- Inspiration for behavioral descriptions of Matoi's 17 agents
- Protocols from Superpowers adapted:
  - TDD discipline (Backend Engineer)
  - "No fixes without root cause" (Systematic Debugger -> QA)
  - Distrustful verification (Spec Compliance -> QA Strategist)
  - "Design before code" (Brainstormer -> Product Designer)
  - Anti-sycophancy (Code Review Recipient -> all Critics)

**License:** MIT | **Stars:** ~165K

---

## [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) -- LLM gateway

**What:** The official SDK for the Claude API.

**How we use it:**
- `client.messages.create()` -- non-streaming calls (conflict detection, activation)
- `client.messages.stream()` -- streaming calls (brief, expert pass, synthesis)
- Cost tracking via `message.usage.input_tokens/output_tokens`
- Error handling: retry on rate limits (429), connection errors, server errors (5xx), overloaded (529)

---

## [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) -- TUI

**What:** A library for interactive CLIs with autocomplete, history, keybindings.

**How we use it:**
- Interactive REPL session in `matoi`
- Colored prompt `[project/PM] >` (green/yellow)
- Tab autocomplete: `/commands` and `@agents` (fuzzy)
- Persistent history `~/.matoi/history`
- Bottom status bar: PM, team, tokens, cost
- Keybindings: Ctrl+C, Ctrl+D, Ctrl+L, Alt+Enter

---

## [Rich](https://github.com/Textualize/rich) -- terminal rendering

**What:** A library for beautiful terminal output.

**How we use it:**
- Rich Markdown: live rendering of agent responses (headings, lists, code)
- Rich Live: markdown updates during streaming
- Rich Table: agent tables, cost breakdown, team list
- Rich Panel: agent cards, avatars
- Rich Console: colored output, rule dividers

---

## [Pillow](https://github.com/python-pillow/Pillow) -- pixel-art avatars

**What:** An image processing library.

**How we use it:**
- Converting pixel-art PNGs (128x128) to Braille Unicode for the terminal
- Automatic resize to 30 characters width
- 17 agent avatars
