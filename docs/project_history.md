# 纏 Matoi — История создания проекта

---

## Таймлайн

### Фаза 0: Зарождение идеи (до апреля 2026)

**Проблема:** Один AI-агент (ChatGPT, Claude) даёт линейный ответ без альтернатив, не спорит сам с собой, не создаёт полезного напряжения между разными точками зрения. Solo-фаундеру нужна команда, но нанять её невозможно.

**Инсайт:** Что если собрать виртуальную команду из специализированных AI-агентов, которые реально взаимодействуют — спорят, критикуют, предлагают альтернативы и приходят к совместному решению?

**Первичный референс:** проект [agency-agents](https://github.com/nacerallahchemssy/agency-agents) — библиотека агентных описаний. Но нужна не библиотека, а операционная система AI-команды.

---

### Фаза 1: Первый промпт и техническая спецификация (апрель 2026)

Создан первый документ — `project_promt.md` (502 строки). Детальная техническая спецификация в формате задания для senior staff-level AI architect:

**Ключевые решения на этом этапе:**
- **CLI-first** — не веб, а терминал. Terminal-first UX для реального рабочего процесса
- **Python для MVP** — простота, экосистема AI-библиотек
- **Markdown + YAML frontmatter** для описания агентов — один агент = один `.md` файл
- **6-слойная архитектура:** CLI → Application → Orchestration → Agent Runtime → Storage → Model Gateway
- **Structured debate как формальный протокол**, а не свободная болтовня
- **Cost-aware execution** — разные модели для разных шагов (Haiku/Sonnet/Opus)
- **PM-агенты как ключевая дифференциация** — Startup PM, Delivery PM, Enterprise PM, Product Strategist PM

**Определён 7-этапный pipeline:**
1. Intake (получение запроса)
2. PM Brief (формулировка цели и ограничений)
3. Independent Expert Pass (независимые мнения агентов)
4. Conflict Detection (выявление расхождений)
5. Debate (структурированный спор по конфликтам)
6. Synthesis (итоговое решение)
7. Artifacts (сохранение результатов)

**Определены 4 типа агентов:**
- Coordinators (PM, tech lead)
- Executors (инженеры, дизайнеры)
- Thinkers (архитекторы, стратеги, исследователи)
- Critics (security, performance, accessibility reviewers)

Создана также краткая английская версия — `project_promt_for_claude.md` (37 строк) и executive summary — `project_description.md` (33 строки).

---

### Фаза 2: Исследование конкурентов и референсов (апрель 2026)

Проведён глубокий ресёрч рынка. Создан документ `projects.md` — анализ 8 GitHub-проектов как building blocks:

| Проект | Stars | Роль в платформе |
|--------|-------|-----------------|
| **Superpowers** | 165k | Воркфлоу и скиллы, TDD, dispatch субагентов |
| **Anthropic Skills** | 123k | Стандарт описания навыков агентов |
| **gstack** | 81k | 23 роли, Claude Code setup — но только dev |
| **claude-mem** | 66k | Shared memory между агентами и сессиями |
| **cpr** | ~280 | Compress/preserve/resume контекста |
| **claude-knowledge-graph** | ~22 | Граф знаний с Obsidian-интеграцией |
| **GitNexus** | — | Knowledge graph для кодовых баз |
| **gitVis3D** | ~6 | 3D-визуализация (бонус) |

**Ключевой вывод:** все конкуренты (MetaGPT, CrewAI, gstack, Aider, ChatDev, OpenHands, Squad) — только dev/code. Никто не покрывает полный стартап-цикл.

---

### Фаза 3: Ключевой поворот — от dev team к startup team (23 апреля 2026)

**Это был самый важный момент в истории проекта.**

Исходная идея: "CLI-платформа для оркестрации dev-команды из AI-агентов" (инженеры, QA, architect, PM).

**Поворот:** расширение scope с "dev team orchestrator" до "startup team orchestrator". Помимо инженеров появились:

1. **Strategy & Business** — CEO/Visionary, Business Analyst, Financial Modeler
2. **Research** — Market Researcher, Competitive Analyst, UX Researcher
3. **Marketing & Growth** — Growth Marketer, Content Strategist, Brand Designer
4. **Design & Product** — Product Designer, UX Writer
5. **Engineering** — Backend Engineer, Frontend Engineer, DevOps
6. **Quality & Ops** — QA Strategist, Security Reviewer, PM-агенты

**Почему это важно:** это превратило проект из "ещё одного AI dev tool" в уникальный продукт без прямых конкурентов. Полный стартап-пайплайн: от валидации рынка до запуска продукта.

Создан документ `research.md` (142 строки) — полный ресёрч: концепция, категории агентов, конкурентный анализ, целевая аудитория, монетизация.

---

### Фаза 4: Позиционирование и бизнес-модель (конец апреля 2026)

**Определена целевая аудитория:**
- Primary: solo-фаундеры и инди-хакеры (нужна полная команда)
- Secondary: маленькие стартапы (2-5 чел), tech leads
- Tertiary: акселераторы, фрилансеры, обучение

**Определена монетизация (open-core + SaaS):**
- Free/OSS: CLI, 5 базовых ролей, 1 PM-стратегия
- Pro ($29-49/мес): все 15+ ролей, все PM-стратегии, cost dashboard
- Team ($99-199/мес): shared knowledge graph, team artifacts, CI/CD

**Сформулирован pitch:**
> "Первая CLI-платформа, где AI-агенты работают как полная стартап-команда: от валидации рынка до запуска продукта — стратеги, ресерчеры, маркетологи, инженеры спорят по существу и выдают артефакты."

**Определены 4 уникальных дифференциатора:**
1. Полный стартап, не только dev team
2. Structured debate как формальный протокол
3. PM как реальный оркестратор с разными стратегиями
4. Cost-intelligent model routing + decision trail

---

### Фаза 5: Техническая валидация (конец апреля 2026)

**Ключевое техническое решение:** использовать Anthropic Python SDK напрямую (не Agent SDK) — для полного контроля над каждым вызовом, cost tracking и кастомной оркестрацией.

**Определён формат артефактов:**
- `brief.md` — задание от PM
- `decision.md` — итоговое решение с rationale
- `debate.md` — протокол дискуссии
- `tasks.json` — декомпозиция задач
- `cost.json` — стоимость выполнения
- `agent-opinions/*.md` — мнения каждого агента
- `conflicts.json` — выявленные конфликты

---

### Фаза 6: Scaffolding и первый код (3 мая 2026)

Проект перешёл из фазы проектирования в фазу разработки.

**Создана полная структура проекта (scaffolding):**
- 6-слойная архитектура реализована как Python-пакет `src/agency/`
- CLI Layer (Typer), Core (Pydantic models), Orchestrator (7-stage pipeline), Agent Runtime (registry + .md parser), Storage (sessions, artifacts, costs), Gateway (Anthropic SDK + model router)
- 4 PM-агента с полными .md описаниями
- 2 team presets (mvp-startup, full-product)
- 8 тестов, все проходят
- Команда `agency` работает из терминала

**Реализованы CLI-команды:**
- `agency agents list` — Rich-таблица всех агентов с категориями и risk bars
- `agency agents show <slug>` — карточка агента с аватаром, model policy, strengths/weaknesses
- `agency team create` — интерактивный выбор PM с галереей аватаров, выбор агентов

---

### Фаза 7: Ренейминг в Matoi (3 мая 2026)

Проект нуждался в уникальном имени. После обширного поиска по древнеримским, скандинавским, японским, белорусским и древнерусским названиям выбрано:

**Matoi (纏)** — знамя японских пожарных, за которым собирается команда.

- PyPI, npm, GitHub — всё свободно
- Метафора идеально подходит: знамя → сбор команды → координированное действие
- Короткое (5 букв), запоминаемое, уникальное

**Переименование:**
- Пакет `agency` → `matoi`
- CLI команда `agency` → `matoi`
- Подкоманда `agents` → `roster` (короче, оригинальнее)

```
matoi roster list          # таблица агентов
matoi roster show startup-pm  # карточка агента
matoi team create my-startup  # интерактивный выбор PM
matoi team show my-startup    # вывод команды с аватарами
```

---

### Фаза 8: Агенты с поведенческими паттернами (3 мая 2026)

Добавлено 10 новых агентов с глубокими поведенческими описаниями, вдохновлёнными проектом [Superpowers](https://github.com/obra/superpowers). Каждый агент имеет:
- Iron Law (главное правило)
- Self-review checklist
- Escalation rules (когда остановиться)
- Debate style (как спорить)
- Anti-patterns (что не делать)

**Executors (⚙️):** Backend Engineer (TDD), Frontend Engineer (user-focused), Product Designer (design-before-code), Growth Marketer (GTM experiments)

**Thinkers (🧠):** Market Researcher (data-driven), Competitive Analyst (differentiation), Business Analyst (financial modeling), UX Researcher (user evidence)

**Critics (🔍):** Security Reviewer (adversarial, OWASP), QA Strategist (spec compliance, distrustful by design)

Итого: **14 агентов** в 6 категориях.

---

### Фаза 9: Pixel-art аватары (3 мая 2026)

Каждый из 14 агентов получил уникальный pixel-art портрет (128x128 PNG). Аватары автоматически конвертируются в Braille Unicode для отображения в терминале.

Система аватаров:
- PNG-файлы в `assets/avatars/`
- Автоматический ресайз и конвертация в Braille при загрузке (через Pillow)
- Fallback на .txt если Pillow не установлен
- Цветной вывод через `chafa` (опционально)

---

### Фаза 10: MVP Pipeline — matoi run работает (3 мая 2026)

Подключен Anthropic API. Реализован 3-стадийный pipeline:

1. **PM Brief** — PM формулирует задачу (Haiku — дёшево)
2. **Expert Pass** — каждый агент даёт независимое мнение (Sonnet/Opus по policy)
3. **Synthesis** — PM синтезирует финальное решение (Opus — критическое решение)

**Артефакты сохраняются в файлы:**
- `brief.md`, `opinion_*.md`, `decision.md`, `cost.json`

**Также реализовано:**
- `matoi task plan` — dry run, показывает маршрутизацию моделей без API вызовов
- Budget enforcement — `--budget 1.0` ограничивает расход
- Cost tracking по каждому вызову

Первый тестовый прогон: "Validate market for AI-powered pet care" — Startup PM + Market Researcher + Backend Engineer. PM выдал 4-недельный план, ресёрчер дал анализ рынка с 13 источниками, инженер предложил стек. PM синтезировал решение: "AI Pet Health Triage for Dog Owners, landing page first."

---

### Фаза 11: Knowledge Graph Memory (3 мая 2026)

Реализована система памяти на основе knowledge graph.

**Как работает:**
- После каждого `matoi run` Haiku извлекает сущности из артефактов (~$0.01/сессия)
- Nodes: decisions, insights, risks, rejected alternatives — с тегами
- Edges: related_to, builds_on, contradicts, mitigates
- Новые ноды автоматически связываются с предыдущими через shared tags
- При следующем run PM получает релевантный контекст из графа

**CLI команды:**
- `matoi memory show` — обзор графа: ноды, рёбра, сессии
- `matoi memory search "query"` — текстовый поиск
- `matoi memory clear` — очистка

Граф хранится в `memory/graph.json`. Первый тест: после двух сессий — 8 nodes, 6 edges.

---

### Фаза 12: Новый UX — matoi как инструмент для любого проекта (3 мая 2026)

**Ключевая переделка:** matoi теперь работает не внутри своего репо, а в любой директории пользователя.

**Новый flow:**
```
cd ~/my-project      # пользователь в своём проекте
matoi                # запуск → онбординг

→ Step 1: API key (сохраняется глобально в ~/.matoi/config.json)
→ Step 2: Project scan (языки, фреймворки, git, тесты, CI)
→ Step 3: Интерактивная сборка команды с PM аватарами

→ Создаётся ./matoi/ в проекте:
   matoi/config.json      # команда и настройки
   matoi/memory/           # knowledge graph
   matoi/artifacts/        # результаты сессий
```

**Реализовано:**
- `matoi` без аргументов = онбординг или статус
- Project Scanner: определяет языки, фреймворки, git history, CI, Docker, тесты
- Глобальный конфиг `~/.matoi/` для API key
- Проектный конфиг `./matoi/` для команды и артефактов
- `matoi run "task"` работает из любой инициализированной директории

---

### Текущее состояние (конец дня 3 мая 2026)

**Статус:** работающий MVP. Pipeline реально вызывает API, агенты дают мнения, PM синтезирует решения, память накапливается.

**Что работает:**
- `matoi` — онбординг в любом проекте (API key → scan → team)
- `matoi run "task"` — 3-стадийный pipeline с Anthropic API
- `matoi task plan` — dry run с маршрутизацией моделей
- `matoi roster list/show` — 14 агентов с pixel-art аватарами
- `matoi team create/show` — интерактивная сборка команды
- `matoi memory show/search` — knowledge graph
- Cost-intelligent routing: Haiku/Sonnet/Opus по стадии и агенту
- Budget enforcement
- 8 тестов, все проходят

**Что предстоит:**
- Conflict detection и debate engine (стадии 4-5 pipeline)
- Больше агентов (Content Strategist, DevOps, Financial Modeler)
- GitHub repo + PyPI + Homebrew (когда готов к релизу)
- 3D визуализация проекта (CodeCharta/browser)
- Streaming вывод (сейчас ждёт полный ответ)
- Реальный cost tracking (цены за токены)

**Git-история (9 коммитов):**
```
9e01dad Redesign UX: matoi works in any project directory
a88ec08 Implement knowledge graph memory system
35aada9 Implement MVP pipeline: matoi run with Anthropic API
5c8a382 Update project history and description for Matoi
63b7853 Add 14 custom pixel-art avatars, auto-resize PNG to Braille
25019d9 Add API key check for matoi run, implement matoi team show
ead0ba9 Add 10 agents: executors, thinkers, critics with Superpowers-inspired behaviors
8105fd3 Rename project to Matoi (纏), implement CLI roster and team create
755a4fd Initial scaffolding: project structure, domain models, CLI, agent registry
```

---

## Ключевые принципы, определённые за всё время

1. **Debate ради качества, не ради шоу** — агенты спорят только при реальных конфликтах
2. **Selective activation** — не все агенты активны всегда
3. **Артефакты > разговоры** — результат работы = файлы, не текст чата
4. **Cost-awareness** — дешёвые модели для рутины, дорогие для стратегии
5. **PM управляет** — не хаотичный peer-to-peer, а управляемый процесс
6. **CLI-first** — терминал как основной интерфейс

---

## Эволюция идеи (визуально)

```
"AI dev team в CLI"
       │
       ▼
"Multi-agent orchestrator с debate"
       │
       ▼
"AI startup team — от ресёрча до запуска"  ← ключевой поворот
       │
       ▼
"Полная виртуальная стартап-команда
 с PM-оркестрацией, structured debate
 и cost-intelligent routing"
       │
       ▼
"纏 Matoi — CLI-платформа с 14 агентами,  ← ренейминг + реализация
 pixel-art персонажами и работающим CLI"
       │
       ▼
"Работающий MVP: pipeline с API,           ← первый реальный прогон
 knowledge graph memory, onboarding
 в любом проекте"
```

---

## Структура проекта

```
matoi/
├── src/matoi/              # Основной код (6 слоёв)
│   ├── cli/                # CLI Layer (Typer + Rich)
│   ├── core/               # Pydantic domain models
│   ├── orchestrator/       # 7-stage pipeline, debate, conflict, synthesis
│   ├── agents/             # Registry, runtime, activation
│   ├── storage/            # Artifacts, sessions, costs
│   └── gateway/            # Anthropic SDK, model router
├── agents/                 # 14 агентов в .md (YAML frontmatter)
│   ├── coordinators/       # 4 PM-агента
│   ├── executors/          # Backend, Frontend, Designer, Marketer
│   ├── thinkers/           # Researcher, Analyst, UX
│   └── critics/            # Security, QA
├── teams/                  # Team presets (.yaml) и сохранённые команды (.json)
├── assets/avatars/         # 14 pixel-art PNG + Braille .txt
├── artifacts/              # Выходные артефакты pipeline
├── tests/                  # pytest (8 тестов)
├── scripts/                # Генераторы аватаров
└── docs/                   # Проектная документация
```

---

## Документы проекта

| Документ | Назначение |
|----------|-----------|
| `docs/project_promt.md` | Детальная техническая спецификация (RU) |
| `docs/project_promt_for_claude.md` | Краткий бриф для Claude (EN) |
| `docs/project_description.md` | Executive summary |
| `docs/projects.md` | Анализ 11 референсных проектов |
| `docs/research.md` | Ресёрч рынка, конкуренты, бизнес-модель |
| `docs/obsidian_claude_code_memory.md` | Гайд по Obsidian + Claude Code памяти |
| `docs/project_history.md` | Этот документ — история проекта |
| `CLAUDE.md` | Инструкции для Claude Code |
| `README.md` | Описание проекта |
