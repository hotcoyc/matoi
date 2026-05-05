# 纏 Matoi — Project Creation History

---

## Timeline

### Phase 0: The Birth of the Idea (before April 2026)

**Problem:** A single AI agent (ChatGPT, Claude) gives a linear answer without alternatives, doesn't argue with itself, doesn't create productive tension between different viewpoints. A solo founder needs a team, but hiring one is not feasible.

**Insight:** What if you assembled a virtual team of specialized AI agents that genuinely interact — argue, critique, propose alternatives, and arrive at a joint decision?

**Initial reference:** the [agency-agents](https://github.com/nacerallahchemssy/agency-agents) project — a library of agent descriptions. But what was needed was not a library, but an operating system for an AI team.

---

### Phase 1: First Prompt and Technical Specification (April 2026)

The first document was created — `project_promt.md` (502 lines). A detailed technical specification in the format of an assignment for a senior staff-level AI architect:

**Key decisions at this stage:**
- **CLI-first** — not web, but terminal. Terminal-first UX for a real workflow
- **Python for MVP** — simplicity, AI library ecosystem
- **Markdown + YAML frontmatter** for agent descriptions — one agent = one `.md` file
- **6-layer architecture:** CLI → Application → Orchestration → Agent Runtime → Storage → Model Gateway
- **Structured debate as a formal protocol**, not free-form chatting
- **Cost-aware execution** — different models for different steps (Haiku/Sonnet/Opus)
- **PM agents as a key differentiator** — Startup PM, Delivery PM, Enterprise PM, Product Strategist PM

**A 7-stage pipeline was defined:**
1. Intake (receiving the request)
2. PM Brief (formulating goals and constraints)
3. Independent Expert Pass (independent agent opinions)
4. Conflict Detection (identifying disagreements)
5. Debate (structured argument on conflicts)
6. Synthesis (final decision)
7. Artifacts (saving results)

**4 agent types were defined:**
- Coordinators (PM, tech lead)
- Executors (engineers, designers)
- Thinkers (architects, strategists, researchers)
- Critics (security, performance, accessibility reviewers)

A short English version was also created — `project_promt_for_claude.md` (37 lines) and an executive summary — `project_description.md` (33 lines).

---

### Phase 2: Competitor and Reference Research (April 2026)

In-depth market research was conducted. The document `projects.md` was created — an analysis of 8 GitHub projects as building blocks:

| Project | Stars | Role in the Platform |
|---------|-------|---------------------|
| **Superpowers** | 165k | Workflows and skills, TDD, sub-agent dispatch |
| **Anthropic Skills** | 123k | Standard for agent skill descriptions |
| **gstack** | 81k | 23 roles, Claude Code setup — but dev-only |
| **claude-mem** | 66k | Shared memory between agents and sessions |
| **cpr** | ~280 | Compress/preserve/resume context |
| **claude-knowledge-graph** | ~22 | Knowledge graph with Obsidian integration |
| **GitNexus** | — | Knowledge graph for codebases |
| **gitVis3D** | ~6 | 3D visualization (bonus) |

**Key takeaway:** all competitors (MetaGPT, CrewAI, gstack, Aider, ChatDev, OpenHands, Squad) are dev/code-only. None cover the full startup cycle.

---

### Phase 3: The Key Pivot — From Dev Team to Startup Team (April 23, 2026)

**This was the most important moment in the project's history.**

The original idea: "A CLI platform for orchestrating a dev team of AI agents" (engineers, QA, architect, PM).

**The pivot:** expanding scope from "dev team orchestrator" to "startup team orchestrator". Beyond engineers, the following were added:

1. **Strategy & Business** — CEO/Visionary, Business Analyst, Financial Modeler
2. **Research** — Market Researcher, Competitive Analyst, UX Researcher
3. **Marketing & Growth** — Growth Marketer, Content Strategist, Brand Designer
4. **Design & Product** — Product Designer, UX Writer
5. **Engineering** — Backend Engineer, Frontend Engineer, DevOps
6. **Quality & Ops** — QA Strategist, Security Reviewer, PM agents

**Why this matters:** it transformed the project from "yet another AI dev tool" into a unique product with no direct competitors. A complete startup pipeline: from market validation to product launch.

The document `research.md` (142 lines) was created — full research: concept, agent categories, competitive analysis, target audience, monetization.

---

### Phase 4: Positioning and Business Model (late April 2026)

**Target audience defined:**
- Primary: solo founders and indie hackers (need a complete team)
- Secondary: small startups (2-5 people), tech leads
- Tertiary: accelerators, freelancers, education

**Monetization defined (open-core + SaaS):**
- Free/OSS: CLI, 5 basic roles, 1 PM strategy
- Pro ($29-49/mo): all 15+ roles, all PM strategies, cost dashboard
- Team ($99-199/mo): shared knowledge graph, team artifacts, CI/CD

**Pitch formulated:**
> "The first CLI platform where AI agents work as a complete startup team: from market validation to product launch — strategists, researchers, marketers, engineers argue on substance and produce artifacts."

**4 unique differentiators defined:**
1. Complete startup, not just a dev team
2. Structured debate as a formal protocol
3. PM as a real orchestrator with different strategies
4. Cost-intelligent model routing + decision trail

---

### Phase 5: Technical Validation (late April 2026)

**Key technical decision:** use the Anthropic Python SDK directly (not Agent SDK) — for full control over each call, cost tracking, and custom orchestration.

**Artifact format defined:**
- `brief.md` — assignment from the PM
- `decision.md` — final decision with rationale
- `debate.md` — discussion transcript
- `tasks.json` — task decomposition
- `cost.json` — execution cost
- `agent-opinions/*.md` — each agent's opinion
- `conflicts.json` — identified conflicts

---

### Phase 6: Scaffolding and First Code (May 3, 2026)

The project moved from the design phase to the development phase.

**Full project structure created (scaffolding):**
- 6-layer architecture implemented as Python package `src/agency/`
- CLI Layer (Typer), Core (Pydantic models), Orchestrator (7-stage pipeline), Agent Runtime (registry + .md parser), Storage (sessions, artifacts, costs), Gateway (Anthropic SDK + model router)
- 4 PM agents with full .md descriptions
- 2 team presets (mvp-startup, full-product)
- 8 tests, all passing
- `agency` command works from the terminal

**Implemented CLI commands:**
- `agency agents list` — Rich table of all agents with categories and risk bars
- `agency agents show <slug>` — agent card with avatar, model policy, strengths/weaknesses
- `agency team create` — interactive PM selection with avatar gallery, agent selection

---

### Phase 7: Renaming to Matoi (May 3, 2026)

The project needed a unique name. After extensive search across ancient Roman, Norse, Japanese, Belarusian, and Old Russian names, the choice was:

**Matoi (纏)** — a Japanese firefighter's standard, around which the team rallies.

- PyPI, npm, GitHub — all available
- The metaphor is a perfect fit: standard → team assembly → coordinated action
- Short (5 letters), memorable, unique

**Renaming:**
- Package `agency` → `matoi`
- CLI command `agency` → `matoi`
- Subcommand `agents` → `roster` (shorter, more distinctive)

```
matoi roster list          # agent table
matoi roster show startup-pm  # agent card
matoi team create my-startup  # interactive PM selection
matoi team show my-startup    # display team with avatars
```

---

### Phase 8: Agents with Behavioral Patterns (May 3, 2026)

10 new agents were added with deep behavioral descriptions, inspired by the [Superpowers](https://github.com/obra/superpowers) project. Each agent has:
- Iron Law (core rule)
- Self-review checklist
- Escalation rules (when to stop)
- Debate style (how to argue)
- Anti-patterns (what not to do)

**Executors:** Backend Engineer (TDD), Frontend Engineer (user-focused), Product Designer (design-before-code), Growth Marketer (GTM experiments)

**Thinkers:** Market Researcher (data-driven), Competitive Analyst (differentiation), Business Analyst (financial modeling), UX Researcher (user evidence)

**Critics:** Security Reviewer (adversarial, OWASP), QA Strategist (spec compliance, distrustful by design)

Total: **14 agents** in 6 categories.

---

### Phase 9: Pixel-Art Avatars (May 3, 2026)

Each of the 14 agents received a unique pixel-art portrait (128x128 PNG). Avatars are automatically converted to Braille Unicode for terminal display.

Avatar system:
- PNG files in `assets/avatars/`
- Automatic resize and Braille conversion on load (via Pillow)
- Fallback to .txt if Pillow is not installed
- Color output via `chafa` (optional)

---

### Phase 10: MVP Pipeline — matoi run Works (May 3, 2026)

Anthropic API connected. A 3-stage pipeline implemented:

1. **PM Brief** — PM formulates the task (Haiku — cheap)
2. **Expert Pass** — each agent provides an independent opinion (Sonnet/Opus per policy)
3. **Synthesis** — PM synthesizes the final decision (Opus — critical decision)

**Artifacts saved to files:**
- `brief.md`, `opinion_*.md`, `decision.md`, `cost.json`

**Also implemented:**
- `matoi task plan` — dry run, shows model routing without API calls
- Budget enforcement — `--budget 1.0` limits spending
- Cost tracking per call

First test run: "Validate market for AI-powered pet care" — Startup PM + Market Researcher + Backend Engineer. PM produced a 4-week plan, researcher provided a market analysis with 13 sources, engineer suggested a tech stack. PM synthesized the decision: "AI Pet Health Triage for Dog Owners, landing page first."

---

### Phase 11: Knowledge Graph Memory (May 3, 2026)

A memory system based on a knowledge graph was implemented.

**How it works:**
- After each `matoi run`, Haiku extracts entities from artifacts (~$0.01/session)
- Nodes: decisions, insights, risks, rejected alternatives — with tags
- Edges: related_to, builds_on, contradicts, mitigates
- New nodes are automatically linked to previous ones via shared tags
- On the next run, the PM receives relevant context from the graph

**CLI commands:**
- `matoi memory show` — graph overview: nodes, edges, sessions
- `matoi memory search "query"` — text search
- `matoi memory clear` — clear

Graph is stored in `memory/graph.json`. First test: after two sessions — 8 nodes, 6 edges.

---

### Phase 12: New UX — matoi as a Tool for Any Project (May 3, 2026)

**Key redesign:** matoi now works not inside its own repo, but in any user directory.

**New flow:**
```
cd ~/my-project      # user is in their project
matoi                # launch → onboarding

→ Step 1: API key (saved globally in ~/.matoi/config.json)
→ Step 2: Project scan (languages, frameworks, git, tests, CI)
→ Step 3: Interactive team assembly with PM avatars

→ Creates ./matoi/ in the project:
   matoi/config.json      # team and settings
   matoi/memory/           # knowledge graph
   matoi/artifacts/        # session results
```

**Implemented:**
- `matoi` with no arguments = onboarding or status
- Project Scanner: detects languages, frameworks, git history, CI, Docker, tests
- Global config `~/.matoi/` for API key
- Project config `./matoi/` for team and artifacts
- `matoi run "task"` works from any initialized directory

---

### Phase 13: MemPalace, Visualization, Cost Tracking (May 4, 2026)

- **MemPalace** replaced the homegrown knowledge graph: 433 drawers, semantic search (96.6% recall), MCP with 29 tools
- **code-review-graph**: 210 nodes, 1317 edges, 28 MCP tools for AI code navigation
- **CodeCharta**: 3D code city (.cc.json.gz)
- **matoi viz**: graph/city/build/status commands
- **Real cost tracking**: Haiku $1/$5, Sonnet $3/$15, Opus $15/$75 per 1M tokens
- **matoi cost**: cost aggregation across all sessions with breakdown by model

---

### Phase 14: Streaming and Debate Engine (May 4, 2026)

**Streaming:** text appears token-by-token instead of waiting for the full response. Uses `client.messages.stream()` from the Anthropic SDK.

**Conflict Detection + Debate Engine — full 5-stage pipeline:**

```
1. PM Brief (Haiku)
2. Expert Pass (Sonnet/Opus, streaming)
3. Conflict Detection (Haiku -- scans for disagreements)
     |
     +-- conflicts found (severity >= 0.5) --> Debate
     |
     +-- no conflicts --> skip, go straight to Synthesis
     |
4. Debate (structured rounds: claim/critique/concession/recommendation)
5. Synthesis (Opus, streaming -- PM decides incorporating debate results)
```

**Debate protocol:**
- Each dissenting agent formulates claim + critique + concession + recommendation
- Max rounds configurable (default: 2)
- Budget-aware: skips debate if budget is exhausted
- Artifact: debate.md with full transcript

---

### Phase 15: MVP Polish (May 4, 2026)

- **Selective agent activation** -- Haiku analyzes the task, selects relevant agents, skips irrelevant ones
- **3 new agents** (total 17): Content Strategist, DevOps Engineer, Financial Modeler
- **matoi team list** -- view all saved teams
- Removed the duplicate `matoi task run` (kept `matoi run` + `matoi task plan`)

---

### Phase 16: Interactive REPL (May 4, 2026)

**Matoi became interactive.** Instead of one-shot `matoi run "task"` -- a full-featured session:

1. `matoi` opens a REPL with a prompt
2. Choose PM, describe the goal
3. PM recommends a team for the session
4. User enters tasks, agents respond (streaming + markdown)
5. `/commit` -- agents review diff, debate if conflicts, commit, update graph

Session commands: /help, /team, /agents, /cost, /history, /commit, /quit

---

### Phase 17: Phase B TUI (May 4, 2026)

Full-featured TUI via prompt_toolkit:

- Colored prompt `[project/PM] >` (green = ready, yellow = working)
- Bottom status bar: PM, team size, tokens, cost
- Tab autocomplete for commands (fuzzy: `/co` -> `/commit`, `/cost`)
- Tab autocomplete for @agents (fuzzy)
- Persistent history (`~/.matoi/history`, arrow keys, Ctrl+R)
- Alt+Enter for multiline
- Live markdown rendering (Rich Live + Markdown, code highlighting)
- Keybindings: Ctrl+C cancel, Ctrl+D quit, Ctrl+L clear

---

### Phase 18: Error Handling, History, Tests (May 4, 2026)

- **Error handling:** retry with backoff on rate limits (429), connection errors, server errors (5xx), overloaded (529). Auth errors -- immediate fail. REPL catches all errors, session doesn't crash.
- **matoi history** -- view past sessions, markdown-render artifacts, cost breakdown
- **33 tests** (was 8): cost tracker, model router, pricing, config, scanner, conflict, debate, activation, registry

---

### Phase 19: Distribution -- GitHub + PyPI (May 4, 2026)

- **GitHub repo** published: https://github.com/hotcoyc/matoi (public)
- **PyPI** published: https://pypi.org/project/matoi/
- **GitHub Actions** auto-publish: push tag `v*` -> builds and publishes to PyPI via trusted publisher (no tokens)
- **pipx install matoi** works globally from any directory
- Fixed: bundled agents/assets in wheel (hatch force-include)
- Fixed: SSH key setup for new GitHub account

---

### Phase 20: UX Fixes and Polish (May 4, 2026)

- **API key validation** on startup -- test call with Haiku, prompt to re-enter if invalid
- **PM gallery** replaced broken Braille panels with clean table
- **Auto/manual team selection** -- user chooses "auto" (PM recommends) or "manual" (pick from list)
- **Concise prompts** -- "Max 300 words. No self-introductions. Go straight to the point."
- **exit/quit/q** without slash exits session
- **/key** command to change API key mid-session
- **Inline PNG avatars** in Warp/iTerm2/Kitty terminals
- **New pixel-art avatars** for all 17 agents
- **All documentation translated to English**

---

### Phase 21: Fullscreen TUI Experiment (May 4, 2026)

Built fullscreen TUI with Textual (sidebar, tabs, color coding, progress indicators). Hit compatibility issues with Textual across Python versions. **Reverted to prompt_toolkit REPL** as default -- more stable and compatible. Fullscreen code kept for future iteration.

---

### Phase 22: Execution Mode, Standup, Interactive UX (May 2026)

**Execution Mode** (`/execute`): a second pipeline mode alongside Advisory. PM decomposes a task into subtasks and dispatches them to agents via `dispatch.py`. Each subtask gets a DONE or BLOCKED status. The PM tracks progress and reports results.

**Standup notes**: auto-generated on session exit. Summarize decisions made, work completed, and blockers encountered during the session.

**PM names**: all 4 PMs received character names -- Oliver (Startup), Aurora (Delivery), Marcus (Enterprise), Stella (Product Strategist). Names appear in prompts, menus, and standup notes.

**Interactive UX overhaul**:
- **Questionary** replaced raw input for PM selection (arrow-key navigation with descriptions) and team assembly (checkbox multi-select)
- **alive-progress** added animated spinners during pipeline stages (brief, expert pass, conflict detection, synthesis)

**New session commands**: `/execute`, `/standup`, `/key`

45+ commits, 33 tests, 17 agents (4 PMs, 6 executors, 5 thinkers, 2 critics). Version 0.2.0+.

---

### Current State (May 2026)

**Status:** published MVP, v0.2.0+. 45+ commits, 33 tests, 17 agents (4 PMs with names: Oliver/Aurora/Marcus/Stella, 6 executors, 5 thinkers, 2 critics). Available on PyPI and GitHub.

**Install:**
```bash
pipx install matoi
matoi
```

**What works:**
- `matoi` -- interactive REPL (prompt_toolkit: autocomplete, history, status bar, inline avatars)
- `matoi run "task"` -- one-shot pipeline
- `matoi history` -- view sessions and artifacts
- `matoi cost` -- cost breakdown by sessions and models
- `matoi roster list/show` -- 17 agents with pixel-art avatars
- `matoi team create/show/list` -- teams (Questionary arrow-key/checkbox menus)
- `matoi memory show/search/mine/wake-up` -- MemPalace
- `matoi viz graph/city/build/status` -- visualizations
- Two pipeline modes: Advisory (brief->expert->conflict->debate->synthesis) and Execution (/execute: PM decomposes->agents execute subtasks with DONE/BLOCKED)
- Session commands: /help, /team, /agents, /cost, /history, /standup, /execute, /commit, /key, /quit
- Standup notes auto-generated on session exit
- Streaming + live markdown rendering
- alive-progress spinners during pipeline stages
- Selective agent activation
- Pre-commit debate (/commit)
- Real cost tracking ($1/$5, $3/$15, $15/$75)
- Error handling with retry and graceful fallback
- Auto-publish: git tag -> GitHub Actions -> PyPI
- 33 tests, all passing

**Distribution:**
- GitHub: https://github.com/hotcoyc/matoi
- PyPI: https://pypi.org/project/matoi/
- Install: `pipx install matoi`

**What's next:**
- Fullscreen TUI (when Textual stabilizes)
- Agent marketplace
- Homebrew tap

---

## Key Principles Established Over Time

1. **Debate for quality, not for show** — agents argue only when real conflicts exist
2. **Selective activation** — not all agents are always active
3. **Artifacts > conversations** — the work product = files, not chat text
4. **Cost-awareness** — cheap models for routine, expensive for strategy
5. **PM is in charge** — not chaotic peer-to-peer, but a managed process
6. **CLI-first** — the terminal as the primary interface

---

## Idea Evolution (visual)

```
"AI dev team in CLI"
       │
       ▼
"Multi-agent orchestrator with debate"
       │
       ▼
"AI startup team — from research to launch"  ← key pivot
       │
       ▼
"Complete virtual startup team
 with PM orchestration, structured debate
 and cost-intelligent routing"
       │
       ▼
"纏 Matoi — CLI platform with 17 agents,      ← renaming + implementation
 pixel-art characters and a working CLI"
       │
       ▼
"Working MVP: pipeline with API,               ← first real run
 knowledge graph memory, onboarding
 in any project"
```

---

## Project Structure

```
matoi/
├── src/matoi/              # Main code (6 layers)
│   ├── cli/                # CLI Layer (Typer + Rich)
│   ├── core/               # Pydantic domain models
│   ├── orchestrator/       # 7-stage pipeline, debate, conflict, synthesis
│   ├── agents/             # Registry, runtime, activation
│   ├── storage/            # Artifacts, sessions, costs
│   └── gateway/            # Anthropic SDK, model router
├── agents/                 # 17 agents in .md (YAML frontmatter)
│   ├── coordinators/       # 4 PMs (Oliver, Aurora, Marcus, Stella)
│   ├── executors/          # 6: Backend, Frontend, Designer, Marketer, Content, DevOps
│   ├── thinkers/           # 5: Researcher, Competitive, Business, UX, Financial
│   └── critics/            # 2: Security, QA
├── teams/                  # Team presets (.yaml) and saved teams (.json)
├── assets/avatars/         # 17 pixel-art PNG + Braille .txt
├── artifacts/              # Pipeline output artifacts
├── tests/                  # pytest (33 tests)
├── scripts/                # Avatar generators
└── docs/                   # Project documentation
```

---

## Project Documents

| Document | Purpose |
|----------|---------|
| `docs/project_promt.md` | Detailed technical specification (RU) |
| `docs/project_promt_for_claude.md` | Short brief for Claude (EN) |
| `docs/project_description.md` | Executive summary |
| `docs/projects.md` | Analysis of 11 reference projects |
| `docs/research.md` | Market research, competitors, business model |
| `docs/obsidian_claude_code_memory.md` | Guide on Obsidian + Claude Code memory |
| `docs/project_history.md` | This document — project history |
| `CLAUDE.md` | Instructions for Claude Code |
| `README.md` | Project description |
