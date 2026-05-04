# AI Agency Platform — Research

## Concept

**A CLI platform for running a complete AI startup** — from idea validation to product launch. Not just a dev team, but a complete cross-functional organization: strategists, researchers, marketers, designers, engineers — orchestrated through structured debate.

---

## Agent Categories (6 categories, 15+ roles)

| Category | Roles | Typical Tasks |
|---|---|---|
| **Strategy & Business** | CEO/Visionary, Business Analyst, Financial Modeler | Business model, unit economics, pitch deck, strategy |
| **Research** | Market Researcher, Competitive Analyst, UX Researcher | Market research, competitor analysis, customer interviews |
| **Marketing & Growth** | Growth Marketer, Content Strategist, Brand Designer | Positioning, GTM strategy, content plan, landing page |
| **Design & Product** | Product Designer, UX Writer | Wireframes, user flows, copywriting, design system |
| **Engineering** | Backend Engineer, Frontend Engineer, DevOps | Architecture, API, database, deployment |
| **Quality & Ops** | QA Strategist, Security Reviewer, PM (startup/delivery/enterprise) | Tests, security, process management |

### Example Tasks for the New Scope

```
agency task run --team my-startup "Validate the market for AI-powered pet care"
agency task run --team my-startup "Create go-to-market strategy for B2B SaaS"
agency task run --team my-startup "Design the MVP and estimate costs"
agency task run --team my-startup "Prepare a pitch deck for seed round"
agency task run --team my-startup "Analyze competitors in the AI writing space"
```

---

## Building Blocks (projects from projects.md)

| Component | Source Project | Role in the Platform |
|---|---|---|
| Workflows and skills | **superpowers** (165k stars), **gstack** (81k stars) | TDD, brainstorming, sub-agent dispatch, 23+ roles |
| Persistent memory | **claude-mem** (66k stars) | Shared memory between agents and sessions |
| Lightweight context preservation | **cpr** (~280 stars) | Compress/preserve/resume without heavy dependencies |
| Knowledge graph | **claude-knowledge-graph** (~22 stars) | Structured links between decisions |
| Skill format | **anthropics/skills** (123k stars) | Standard for agent skill descriptions |
| Context packaging for AI | **Repomix** (~23K stars) | Entire repo in one AI-friendly file, MCP server |
| AI code navigation | **code-review-graph** (~15K stars) | Codebase knowledge graph, 6.8-49x token savings |
| 3D architecture visualization | **CodeCharta** (~411 stars) | 3D code city: hotspots, metrics, version comparison |
| Git history visualization | **gitVis3D** (~6 stars) | 3D graph of team activity (bonus, not core) |

---

## What Problems Does It Solve?

1. **One AI = one bias.** GPT/Claude doesn't argue with itself. The platform creates real confrontation of opinions (marketer vs engineer, CEO vs QA, researcher vs PM) — a structured debate protocol.

2. **Solo founder without a team.** An indie hacker needs a researcher, marketer, designer, engineer, QA — but hiring them is not feasible. The platform provides a complete virtual startup team for $1-5 per task.

3. **LLMs are either expensive or bad.** Opus for everything = expensive, Haiku for everything = shallow. Cost-intelligent routing: Haiku for routine, Sonnet for core work, Opus for strategic decisions.

4. **Context is lost.** After a session — nothing. Persistent memory + knowledge graph provide a decision audit trail (who, when, and why decided X).

5. **Tool fragmentation.** Research in ChatGPT, code in Cursor, marketing somewhere else. The platform = a single entry point for the entire startup.

6. **All AI competitors are code-only.** MetaGPT, CrewAI, gstack, Aider — dev teams only. None cover the full startup cycle.

---

## Uniqueness

Four things that **no competitor has**:

1. **Complete startup, not just a dev team.** Market research → strategy → design → development → marketing → launch. All competitors (MetaGPT, CrewAI, gstack) are code-only.

2. **Structured debate as a formal protocol.** Conflict detection → targeted debate → synthesis → decision artifact. Not "two agents chatting" (ChatDev), but a managed process.

3. **PM as a real orchestrator with different strategies.** Startup PM (speed), Delivery PM (predictability), Enterprise PM (compliance). gstack has roles, but no management strategies.

4. **Cost-intelligent model routing + decision trail.** Task routing between Haiku/Sonnet/Opus + saving all decisions as artifacts (brief.md, debate.md, decision.md).

5. **Visual agent characters in CLI.** ASCII/Braille-art PM agent avatars with mottos and characteristics. Intuitive management style selection through visual identity — no competitor makes agents feel "alive" in the terminal.

---

## Differences from Similar Projects

| | MetaGPT | CrewAI | gstack | Aider | **Our Platform** |
|---|---|---|---|---|---|
| Multi-agent | pipeline | generic | roles | single | full startup team |
| Business roles | code-only | none | code-only | none | research, marketing, strategy |
| Debate/conflict | none | none | none | none | structured |
| PM orchestration | partial | none | partial (CEO) | none | with strategy selection |
| Cost routing | none | none | none | tracks | routes |
| Decision artifacts | none | none | none | none | yes |
| CLI-first | Python | Python | yes | yes | yes |

**Key difference:** all competitors are "AI dev team". We are "AI startup team". Broader scope, broader audience, broader market.

### Competitive Landscape (April 2026)

- **MetaGPT** (67k stars) — pipeline without debate, code-only
- **CrewAI** (46k) — generic framework, not for startups
- **AutoGen** (50k) — maintenance mode
- **ChatDev** (33k) — academic, pairwise chat, code-only
- **OpenHands** (68k) — single agent
- **Aider** (44k) — pair programming, CLI, cost-aware, but single agent
- **gstack** (81k) — Claude Code + roles, but dev-only, no debate
- **Squad** (2.2k) — CLI + team, but tied to Copilot, no debate

---

## Target Audience

**Primary (ready to pay now):**
- Solo founders — they need a complete team (research + strategy + marketing + dev) that they can't hire
- Indie hackers — they need marketing and GTM beyond code

**Secondary (ready to try):**
- Small startups (2-5 people) — they need virtual experts in areas where they have no people
- Tech leads — for design review and architecture decisions
- Non-technical founders — for technical expertise without hiring

**Tertiary (long-term):**
- Accelerators and incubators — tool for portfolio companies
- Freelancers — appear as an agency while working solo
- Education — observing debates between specialists

---

## Monetization

### Open-core + SaaS

| Tier | What's Included | Price |
|---|---|---|
| **Free / OSS** | CLI, basic roles (5), 1 PM strategy, local storage | $0 |
| **Pro** | All 15+ roles, all PM strategies, cost dashboard, debate protocol, cloud memory | $29-49/mo |
| **Team** | Shared knowledge graph, team artifacts, CI/CD integration, custom agents | $99-199/mo per team |

### Additional Channels

1. **Usage-based markup** — transparent surcharge on API calls (~20%)
2. **Role marketplace** — community sells specialized agents (platform takes 20-30%)
3. **Consulting/white-label** — customization for enterprise workflows

**Why they'll pay:** a solo founder with a startup idea spends weeks on market research, competitive analysis, GTM strategy. The platform does this in minutes for $1-5, with structured debate between a researcher, marketer, and strategist.

---

## One-Line Pitch

> "The first CLI platform where AI agents work as a complete startup team: from market validation to product launch — strategists, researchers, marketers, engineers argue on substance and produce artifacts."
