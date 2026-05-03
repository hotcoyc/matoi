# AI Agency Platform — История создания проекта

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

### Текущее состояние (май 2026)

**Статус:** фаза проектирования и валидации идеи. Код ещё не написан.

**Что есть:**
- 5 документов проектирования (~755 строк)
- Детальная техническая спецификация
- Конкурентный анализ
- Бизнес-модель и монетизация
- Чёткое позиционирование

**Что предстоит:**
- Scaffolding проекта (folder structure, pyproject.toml)
- Pydantic domain models
- Agent registry schema
- Team composition logic
- Orchestrator и debate engine
- CLI на Typer
- MVP первого end-to-end pipeline

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
```

---

## Документы проекта

| Документ | Назначение | Строк |
|----------|-----------|-------|
| `project_promt.md` | Детальная техническая спецификация (RU) | 502 |
| `project_promt_for_claude.md` | Краткий бриф для Claude (EN) | 37 |
| `project_description.md` | Executive summary | 33 |
| `projects.md` | Анализ референсных проектов | 41 |
| `research.md` | Ресёрч рынка, конкуренты, бизнес-модель | 142 |
| `obsidian_claude_code_memory.md` | Гайд по Obsidian + Claude Code памяти | — |
| `project_history.md` | Этот документ — история проекта | — |
