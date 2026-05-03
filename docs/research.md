# AI Agency Platform — Research

## Концепция

**CLI-платформа для организации полного AI-стартапа** — от валидации идеи до запуска продукта. Не просто dev-команда, а полная кросс-функциональная организация: стратеги, ресерчеры, маркетологи, дизайнеры, инженеры — оркестрируемые через structured debate.

---

## Категории агентов (6 категорий, 15+ ролей)

| Категория | Роли | Типичные задачи |
|---|---|---|
| **Strategy & Business** | CEO/Visionary, Business Analyst, Financial Modeler | Бизнес-модель, unit economics, pitch deck, стратегия |
| **Research** | Market Researcher, Competitive Analyst, UX Researcher | Ресерч рынка, анализ конкурентов, customer interviews |
| **Marketing & Growth** | Growth Marketer, Content Strategist, Brand Designer | Позиционирование, GTM-стратегия, контент-план, лендинг |
| **Design & Product** | Product Designer, UX Writer | Wireframes, user flows, копирайтинг, дизайн-система |
| **Engineering** | Backend Engineer, Frontend Engineer, DevOps | Архитектура, API, БД, деплой |
| **Quality & Ops** | QA Strategist, Security Reviewer, PM (startup/delivery/enterprise) | Тесты, безопасность, управление процессом |

### Примеры задач нового scope

```
agency task run --team my-startup "Validate the market for AI-powered pet care"
agency task run --team my-startup "Create go-to-market strategy for B2B SaaS"
agency task run --team my-startup "Design the MVP and estimate costs"
agency task run --team my-startup "Prepare a pitch deck for seed round"
agency task run --team my-startup "Analyze competitors in the AI writing space"
```

---

## Building Blocks (проекты из projects.md)

| Компонент | Проект-донор | Роль в платформе |
|---|---|---|
| Воркфлоу и скиллы | **superpowers** (165k ⭐), **gstack** (81k ⭐) | TDD, brainstorming, dispatch субагентов, 23+ ролей |
| Персистентная память | **claude-mem** (66k ⭐) | Shared memory между агентами и сессиями |
| Лёгкое сохранение контекста | **cpr** (~280 ⭐) | Compress/preserve/resume без тяжёлых зависимостей |
| Граф знаний | **claude-knowledge-graph** (~22 ⭐) | Структурированные связи между решениями |
| Формат скиллов | **anthropics/skills** (123k ⭐) | Стандарт описания навыков агентов |
| Упаковка контекста для AI | **Repomix** (~23K ⭐) | Весь репо в один AI-friendly файл, MCP-сервер |
| Навигация AI по коду | **code-review-graph** (~15K ⭐) | Граф знаний кодовой базы, экономия токенов 6.8-49x |
| 3D-визуализация архитектуры | **CodeCharta** (~411 ⭐) | 3D-город кода: hotspots, метрики, сравнение версий |
| Визуализация git-истории | **gitVis3D** (~6 ⭐) | 3D-граф работы команды (бонус, не ядро) |

---

## Какие проблемы решает?

1. **Один AI = один bias.** GPT/Claude не спорит сам с собой. Платформа создаёт реальную конфронтацию мнений (маркетолог vs инженер, CEO vs QA, ресерчер vs PM) — structured debate протокол.

2. **Solo-фаундер без команды.** Инди-хакеру нужны ресерчер, маркетолог, дизайнер, инженер, QA — но нанять их невозможно. Платформа даёт полную виртуальную стартап-команду за $1-5 на задачу.

3. **LLM либо дорого, либо плохо.** Opus на всё = дорого, Haiku на всё = поверхностно. Cost-intelligent routing: Haiku для рутины, Sonnet для основной работы, Opus для стратегических решений.

4. **Контекст теряется.** После сессии — пустота. Persistent memory + knowledge graph дают аудит решений (кто, когда, почему решил X).

5. **Фрагментация инструментов.** Ресерч в ChatGPT, код в Cursor, маркетинг в ещё одном месте. Платформа = единая точка входа для всего стартапа.

6. **Все AI-конкуренты — только про код.** MetaGPT, CrewAI, gstack, Aider — только dev-команда. Никто не покрывает полный стартап-цикл.

---

## Уникальность

Четыре вещи, которых **нет ни у одного конкурента**:

1. **Полный стартап, не только dev team.** Ресерч рынка → стратегия → дизайн → разработка → маркетинг → запуск. Все конкуренты (MetaGPT, CrewAI, gstack) — только код.

2. **Structured debate как формальный протокол.** Conflict detection → targeted debate → synthesis → decision artifact. Не "два агента переписываются" (ChatDev), а управляемый процесс.

3. **PM как реальный оркестратор с разными стратегиями.** Startup PM (скорость), Delivery PM (предсказуемость), Enterprise PM (compliance). gstack имеет роли, но нет управленческих стратегий.

4. **Cost-intelligent model routing + decision trail.** Роутинг задач между Haiku/Sonnet/Opus + сохранение всех решений как артефакты (brief.md, debate.md, decision.md).

5. **Визуальные персонажи агентов в CLI.** ASCII/Braille-арт аватары PM-агентов с девизами и характеристиками. Интуитивный выбор стиля управления через визуальную идентичность — ни один конкурент не делает агентов "живыми" в терминале.

---

## Отличия от похожих проектов

| | MetaGPT | CrewAI | gstack | Aider | **Наша платформа** |
|---|---|---|---|---|---|
| Multi-agent | ✅ pipeline | ✅ generic | ✅ roles | ❌ single | ✅ full startup team |
| Бизнес-роли | ❌ только код | ❌ | ❌ только код | ❌ | ✅ research, marketing, strategy |
| Debate/conflict | ❌ | ❌ | ❌ | ❌ | ✅ structured |
| PM-оркестрация | частично | ❌ | частично (CEO) | ❌ | ✅ с выбором стратегии |
| Cost routing | ❌ | ❌ | ❌ | ✅ отслеживает | ✅ роутит |
| Decision artifacts | ❌ | ❌ | ❌ | ❌ | ✅ |
| CLI-first | ❌ Python | ❌ Python | ✅ | ✅ | ✅ |

**Ключевое отличие:** все конкуренты — это "AI dev team". Мы — "AI startup team". Шире scope, шире аудитория, шире рынок.

### Конкурентный ландшафт (апрель 2026)

- **MetaGPT** (67k stars) — pipeline без debate, только код
- **CrewAI** (46k) — generic framework, не для стартапов
- **AutoGen** (50k) — maintenance mode
- **ChatDev** (33k) — академический, pairwise chat, только код
- **OpenHands** (68k) — single agent
- **Aider** (44k) — pair programming, CLI, cost-aware, но single agent
- **gstack** (81k) — Claude Code + роли, но только dev, нет debate
- **Squad** (2.2k) — CLI + team, но привязан к Copilot, нет debate

---

## Целевая аудитория

**Primary (готовы платить сейчас):**
- Solo-фаундеры — им нужна полная команда (ресерч + стратегия + маркетинг + dev), которую они не могут нанять
- Инди-хакеры — нужен маркетинг и GTM помимо кода

**Secondary (готовы попробовать):**
- Маленькие стартапы (2-5 чел) — нужны виртуальные эксперты в областях, где нет людей
- Tech leads — для design review и architecture decisions
- Non-technical фаундеры — для технической экспертизы без найма

**Tertiary (long-term):**
- Акселераторы и инкубаторы — инструмент для портфельных компаний
- Фрилансеры — выглядеть как agency, работая одному
- Обучение — наблюдение за дебатами между специалистами

---

## Монетизация

### Open-core + SaaS

| Tier | Что входит | Цена |
|---|---|---|
| **Free / OSS** | CLI, базовые роли (5), 1 PM-стратегия, local storage | $0 |
| **Pro** | Все 15+ ролей, все PM-стратегии, cost dashboard, debate protocol, cloud memory | $29-49/мес |
| **Team** | Shared knowledge graph, team artifacts, CI/CD интеграция, custom agents | $99-199/мес за команду |

### Дополнительные каналы

1. **Usage-based markup** — прозрачная наценка на API-вызовы (~20%)
2. **Marketplace ролей** — комьюнити продаёт специализированных агентов (платформа берёт 20-30%)
3. **Consulting/white-label** — настройка под enterprise workflow

**Почему будут платить:** solo-фаундер с идеей стартапа тратит недели на ресерч рынка, конкурентный анализ, GTM стратегию. Платформа делает это за минуты и $1-5, с structured debate между ресерчером, маркетологом и стратегом.

---

## Pitch одной строкой

> "Первая CLI-платформа, где AI-агенты работают как полная стартап-команда: от валидации рынка до запуска продукта — стратеги, ресерчеры, маркетологи, инженеры спорят по существу и выдают артефакты."
