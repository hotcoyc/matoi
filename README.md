# Matoi

CLI-платформа, где AI-агенты работают как полная стартап-команда: от валидации рынка до запуска продукта -- стратеги, ресерчеры, маркетологи, инженеры спорят по существу и выдают артефакты.

*Matoi -- знамя японских пожарных, за которым собирается команда.*

## Quick Start

```bash
git clone <repo-url>
cd matoi
pip install -e .
matoi
```

При первом запуске Matoi попросит API key от Anthropic, отсканирует проект, построит граф кода и предложит собрать команду.

## Как работает

```
$ matoi

  Matoi -- your startup team in the terminal.

  API key: ok
  PM: Startup PM -- "Ship it by Friday."

  What are you working on today? > Design MVP for pet care app

  Team: Backend Engineer, Product Designer, Market Researcher

  [ai-agency-platform/Startup] > _
```

Вы вводите задачи -- команда агентов отвечает в реальном времени с markdown-рендерингом. Перед коммитом агенты ревьюят изменения и дебатируют если есть разногласия.

## Pipeline

Каждая задача проходит 6 стадий:

```
1. Selective Activation  -- Haiku выбирает релевантных агентов
2. PM Brief              -- PM формулирует задачу
3. Expert Pass           -- каждый агент даёт мнение (streaming)
4. Conflict Detection    -- Haiku ищет расхождения
5. Debate                -- structured rounds если конфликты найдены
6. Synthesis             -- PM принимает решение с учётом дебатов
```

Дебаты запускаются автоматически когда агенты не согласны друг с другом. Если конфликтов нет -- пропускаются.

## 17 агентов

**PM [PM]** -- 4 стиля управления:

| Агент | Стиль |
|-------|-------|
| Startup PM | Скорость, ship fast, режь scope |
| Delivery PM | Предсказуемость, milestones |
| Enterprise PM | Документация, compliance |
| Product Strategist PM | Ценность для пользователя |

**Executors [EXE]** -- реализация:

| Агент | Принцип |
|-------|---------|
| Backend Engineer | No production code without a failing test first |
| Frontend Engineer | The user doesn't care about your architecture |
| Product Designer | Design it before you build it |
| Growth Marketer | Every channel is a hypothesis |
| Content Strategist | Content without strategy is just noise |
| DevOps Engineer | If it's not automated, it's broken |

**Thinkers [THK]** -- исследования:

| Агент | Принцип |
|-------|---------|
| Market Researcher | Data first, opinions second |
| Competitive Analyst | Know your enemy. Build what they can't copy |
| Business Analyst | If you can't model it, you don't understand it |
| UX Researcher | Talk to users, not about users |
| Financial Modeler | A spreadsheet is a hypothesis. Test it |

**Critics [CRT]** -- проверка:

| Агент | Принцип |
|-------|---------|
| Security Reviewer | Trust nothing. Verify everything |
| QA Strategist | No completion claims without verification evidence |

Каждый агент -- файл `.md` с YAML frontmatter: роль, debate style, model policy, strengths, weaknesses, activation rules.

## Команды сессии

```
/help     -- все команды
/team     -- текущая команда
/agents   -- все 17 агентов
/cost     -- стоимость сессии
/history  -- задачи в этой сессии
/commit   -- review -> debate -> commit -> update graph
/quit     -- выход (Ctrl+D)
```

Tab -- автокомплит команд и @агентов. Alt+Enter -- многострочный ввод.

## CLI команды

```bash
matoi                          # интерактивная сессия
matoi run "задача"             # one-shot pipeline
matoi cost                     # стоимость по сессиям и моделям

matoi roster list              # таблица агентов
matoi roster show startup-pm   # карточка с pixel-art аватаром

matoi team create              # собрать команду
matoi team show / list         # посмотреть команды

matoi memory show              # MemPalace status
matoi memory search "query"    # семантический поиск по памяти

matoi viz graph                # граф зависимостей в браузере
matoi viz city                 # 3D-город кода (CodeCharta)

matoi task plan "задача" -t demo  # dry run
```

## Cost routing

Разные модели для разных стадий -- не "дорого на всё":

| Стадия | Модель | Цена (in/out per 1M) |
|--------|--------|---------------------|
| Activation, Brief, Conflict Detection | Haiku | $1 / $5 |
| Expert Pass, Debate | Sonnet | $3 / $15 |
| Synthesis | Opus | $15 / $75 |

Типичная задача с 3 агентами без дебатов: $0.30-0.80.

## Интеграции

| Инструмент | Что делает |
|-----------|-----------|
| **Anthropic API** | Streaming LLM calls, cost routing |
| **MemPalace** | Память: семантический поиск, knowledge graph, auto-save |
| **code-review-graph** | AI-навигация по коду: 28 MCP tools, auto-update |
| **CodeCharta** | 3D-визуализация архитектуры кода |
| **prompt_toolkit** | TUI: autocomplete, history, status bar |

## Структура проекта

```
src/matoi/
  cli/           -- Typer + Rich + prompt_toolkit
  core/          -- Pydantic models (Agent, Team, Task, Cost, Config)
  orchestrator/  -- Pipeline, ConflictDetector, DebateEngine
  agents/        -- Registry, Activation, Runtime
  storage/       -- MemPalace wrapper, Artifacts, Costs
  gateway/       -- Anthropic SDK, ModelRouter, Pricing

agents/          -- 17 agent .md files (YAML frontmatter)
assets/avatars/  -- pixel-art PNG + Braille .txt
```

## Требования

- Python 3.11+
- Anthropic API key
- Опционально: code-review-graph, CodeCharta (Java 17+), chafa
