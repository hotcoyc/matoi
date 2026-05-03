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
# Создать команду
matoi team create my-startup

# Запустить задачу
matoi run "Validate market for AI-powered pet care" --team my-startup
```

**7-этапный pipeline:**
1. **Intake** — получение задачи от пользователя
2. **PM Brief** — PM формулирует цель, ограничения, deliverables
3. **Expert Pass** — каждый агент независимо даёт экспертное мнение
4. **Conflict Detection** — система выявляет реальные расхождения
5. **Debate** — структурированный спор (claim → critique → alternative → tradeoff)
6. **Synthesis** — PM синтезирует итоговое решение
7. **Artifacts** — результаты сохраняются в файлы

## 14 агентов в 6 категориях

### Coordinators (👔) — PM-агенты с разными стилями
| Агент | Стиль | Risk Tolerance |
|-------|-------|---------------|
| **Startup PM** | Скорость, ship fast, режь scope | Высокий (0.8) |
| **Delivery PM** | Предсказуемость, декомпозиция, milestones | Низкий (0.3) |
| **Enterprise PM** | Документация, compliance, аудит | Минимальный (0.1) |
| **Product Strategist PM** | Ценность для пользователя, research first | Средний (0.5) |

### Executors (⚙️) — реализация
| Агент | Iron Law |
|-------|---------|
| **Backend Engineer** | No production code without a failing test first |
| **Frontend Engineer** | The user doesn't care about your architecture |
| **Product Designer** | Design it before you build it |
| **Growth Marketer** | Every channel is a hypothesis until the data says otherwise |

### Thinkers (🧠) — исследования и стратегия
| Агент | Iron Law |
|-------|---------|
| **Market Researcher** | Data first, opinions second. No claims without sources |
| **Competitive Analyst** | Know your enemy. Then build what they can't copy |
| **Business Analyst** | If you can't model it, you don't understand it |
| **UX Researcher** | Talk to users, not about users |

### Critics (🔍) — проверка и качество
| Агент | Iron Law |
|-------|---------|
| **Security Reviewer** | Trust nothing. Verify everything |
| **QA Strategist** | No completion claims without fresh verification evidence |

## CLI-команды

```bash
matoi roster list                    # Таблица всех 14 агентов
matoi roster list --category research  # Фильтр по категории
matoi roster show startup-pm         # Карточка агента с pixel-art аватаром

matoi team create my-startup         # Интерактивный выбор PM + агентов
matoi team show my-startup           # Вывод команды с аватаром PM
matoi team add my-startup backend-engineer  # Добавить агента
matoi team remove my-startup qa-strategist  # Убрать агента

matoi task run "задача" --team my-startup  # Запуск pipeline
matoi task plan "задача" --team my-startup # Dry run

matoi cost                           # Стоимость сессий
matoi init                           # Инициализация проекта
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
| Хранение | JSON/SQLite |
| Тесты | pytest |
| Линтер | ruff |

## Cost-intelligent routing

| Стадия | Модель | Зачем |
|--------|--------|-------|
| Brief | Haiku | Простая структуризация задачи |
| Expert Pass | Sonnet | Основная экспертная работа |
| Debate | Sonnet/Opus | Зависит от сложности конфликта |
| Synthesis | Opus | Критическое итоговое решение |

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
