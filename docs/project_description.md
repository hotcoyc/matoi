# 纏 Matoi — описание проекта

*Matoi (纏) — знамя японских пожарных, за которым собирается команда.*

---

## Что это

CLI-платформа, где AI-агенты работают как полная стартап-команда. Solo-фаундер получает виртуальную команду — стратеги, ресерчеры, маркетологи, дизайнеры, инженеры — которые взаимодействуют, спорят по существу и выдают готовые артефакты.

## Проблема

1. **Один AI = один bias.** Не спорит сам с собой, не показывает альтернативы
2. **Solo-фаундер без команды.** Нужны ресерчер, маркетолог, инженер, QA — нанять невозможно
3. **LLM либо дорого, либо плохо.** Opus на всё = дорого, Haiku на всё = поверхностно
4. **Контекст теряется.** После сессии — пустота, нет аудита решений
5. **Все AI-конкуренты — только код.** MetaGPT, CrewAI, gstack — dev team, не startup team

## Как это работает

```bash
# Инициализация в любом проекте
cd ~/my-project
matoi                # API key -> scan -> code graph -> team assembly

# Запустить задачу
matoi run "Validate market for AI-powered pet care"
```

**6-стадийный pipeline:**
1. **Selective Activation** -- Haiku анализирует задачу и выбирает релевантных агентов из команды. Нерелевантные пропускаются (экономия токенов)
2. **PM Brief** -- PM формулирует цель, ограничения, deliverables (Haiku)
3. **Expert Pass** -- каждый активный агент независимо даёт мнение (Sonnet/Opus, streaming)
4. **Conflict Detection** -- Haiku сканирует мнения, находит расхождения (severity >= 0.5)
5. **Debate** -- если конфликты найдены: structured rounds (claim/critique/concession/recommendation). Если нет -- пропускается
6. **Synthesis** -- PM синтезирует решение с учётом дебатов (Opus, streaming)

Артефакты: brief.md, opinion_*.md, debate.md, decision.md, cost.json

## 17 агентов в 6 категориях

### Coordinators [PM] -- PM-агенты с разными стилями
| Агент | Стиль | Risk Tolerance |
|-------|-------|---------------|
| **Startup PM** | Скорость, ship fast, режь scope | Высокий (0.8) |
| **Delivery PM** | Предсказуемость, декомпозиция, milestones | Низкий (0.3) |
| **Enterprise PM** | Документация, compliance, аудит | Минимальный (0.1) |
| **Product Strategist PM** | Ценность для пользователя, research first | Средний (0.5) |

### Executors [EXE] -- реализация
| Агент | Iron Law |
|-------|---------|
| **Backend Engineer** | No production code without a failing test first |
| **Frontend Engineer** | The user doesn't care about your architecture |
| **Product Designer** | Design it before you build it |
| **Growth Marketer** | Every channel is a hypothesis until the data says otherwise |
| **Content Strategist** | Content without strategy is just noise |
| **DevOps Engineer** | If it's not automated, it's broken |

### Thinkers [THK] -- исследования и стратегия
| Агент | Iron Law |
|-------|---------|
| **Market Researcher** | Data first, opinions second. No claims without sources |
| **Competitive Analyst** | Know your enemy. Then build what they can't copy |
| **Business Analyst** | If you can't model it, you don't understand it |
| **UX Researcher** | Talk to users, not about users |
| **Financial Modeler** | A spreadsheet is a hypothesis. Test it |

### Critics [CRT] -- проверка и качество
| Агент | Iron Law |
|-------|---------|
| **Security Reviewer** | Trust nothing. Verify everything |
| **QA Strategist** | No completion claims without fresh verification evidence |

## CLI-команды

```bash
matoi                                   # Онбординг: API key, scan, graph, team
matoi run "задача"                      # 6-стадийный pipeline со streaming
matoi run "задача" --budget 1.0         # С лимитом бюджета
matoi cost                              # Стоимость по сессиям и моделям

matoi roster list                       # Таблица всех 17 агентов
matoi roster list --category research   # Фильтр по категории
matoi roster show startup-pm            # Карточка с pixel-art аватаром

matoi team create my-startup            # Интерактивный выбор PM + агентов
matoi team show my-startup              # Вывод команды с аватаром PM
matoi team list                         # Все сохранённые команды
matoi team add my-startup backend-engineer   # Добавить агента
matoi team remove my-startup qa-strategist   # Убрать агента

matoi memory show                       # MemPalace: drawers, wings, rooms
matoi memory search "query"             # Семантический поиск
matoi memory mine .                     # Индексация файлов
matoi memory wake-up                    # Контекст для начала сессии

matoi viz graph                         # Граф зависимостей в браузере
matoi viz city                          # 3D-город кода (CodeCharta)
matoi viz build                         # Пересборка визуализаций
matoi viz status                        # Статус визуализаций

matoi task plan "задача" --team demo    # Dry run с маршрутизацией моделей
```

## Технический стек

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.11+ |
| CLI | Typer + Rich |
| Модели | Pydantic v2 |
| LLM | Anthropic Python SDK (не Agent SDK) |
| Агенты | Markdown + YAML frontmatter |
| Аватары | Pixel-art PNG → Braille Unicode (Pillow) |
| Память | MemPalace (ChromaDB + SQLite, 96.6% recall) |
| Code graph | code-review-graph (Tree-sitter, 28 MCP tools) |
| 3D визуализация | CodeCharta (.cc.json.gz) |
| Streaming | Anthropic SDK stream(), token-by-token вывод |
| Тесты | pytest |
| Линтер | ruff |

## Cost-intelligent routing

| Стадия | Модель | Цена (in/out per 1M) | Зачем |
|--------|--------|---------------------|-------|
| Selective Activation | Haiku | $1 / $5 | Выбор релевантных агентов |
| Brief | Haiku | $1 / $5 | Структуризация задачи |
| Expert Pass | Sonnet | $3 / $15 | Основная экспертная работа |
| Conflict Detection | Haiku | $1 / $5 | Сканирование расхождений |
| Debate | Sonnet | $3 / $15 | Structured rounds по конфликтам |
| Synthesis | Opus | $15 / $75 | Критическое итоговое решение |

## Архитектура (6 слоёв)

```
CLI Layer (Typer + Rich)
    ↓
Core (Pydantic models: Agent, Team, Task, Session, Cost)
    ↓
Orchestrator (Pipeline, Debate Engine, Conflict Detector, Synthesis)
    ↓
Agent Runtime (Registry, Context Builder, Activation Logic)
    ↓
Storage (Artifacts Writer, Session Store, Cost Tracker)
    ↓
Gateway (Model Router, Anthropic SDK Provider)
```

## Ключевые принципы

1. **Debate ради качества, не ради шоу** — спор только при реальных конфликтах
2. **Selective activation** — не все агенты активны на каждой задаче
3. **Артефакты > разговоры** — результат = файлы (brief.md, decision.md), не текст чата
4. **Cost-awareness** — Haiku для рутины, Opus для стратегии
5. **PM управляет** — не хаотичный peer-to-peer, а управляемый pipeline
6. **CLI-first** — терминал как основной интерфейс
7. **Визуальная идентичность** — pixel-art аватары делают агентов "живыми"

## Уникальность (чего нет у конкурентов)

1. **Полный стартап, не только dev team** — ресерч → стратегия → дизайн → разработка → маркетинг
2. **Structured debate как формальный протокол** — conflict detection → targeted debate → synthesis
3. **PM как реальный оркестратор с разными стратегиями** — 4 стиля управления
4. **Cost-intelligent model routing** — не "дорого на всё", а smart routing
5. **Визуальные персонажи в CLI** — pixel-art аватары с характером

## Конкуренты

Все — только dev/code:
- MetaGPT (67k stars) — pipeline без debate
- CrewAI (46k) — generic framework
- gstack (81k) — Claude Code + роли, но только dev
- Aider (44k) — pair programming, single agent
- ChatDev (33k) — pairwise chat, академический

**Matoi — первый full-startup-team orchestrator.**

---

*Pitch одной строкой: "纏 Matoi — первая CLI-платформа, где AI-агенты работают как полная стартап-команда: от валидации рынка до запуска продукта."*
