# Obsidian + Claude Code: система памяти и знаний

Гайд по интеграции Obsidian vault с Claude Code для построения персистентной памяти проекта.

---

## Зачем это нужно

Claude Code имеет встроенную память (`~/.claude/projects/.../memory/`), но она ограничена: плоские `.md`-файлы, нет графа связей, нет визуализации. Obsidian vault решает эти проблемы:

- **Граф связей** — `[[wikilinks]]` между заметками создают knowledge graph
- **Визуализация** — graph view, canvas, backlinks
- **Теги и поиск** — мгновенный полнотекстовый поиск по всему vault
- **Плагины** — Dataview, Templater, Calendar и 1500+ других
- **Всё в Markdown** — Claude Code нативно читает и пишет `.md`

---

## Метод 1: Прямой доступ (zero setup)

Claude Code запускается из директории vault. Vault — это просто папка с `.md`-файлами.

### Настройка

```bash
cd ~/ObsidianVault && claude
```

Создать `CLAUDE.md` в корне vault:

```markdown
## Vault Conventions
- Все заметки используют [[wikilinks]] для перекрёстных ссылок
- YAML frontmatter обязателен
- Не удалять и не переименовывать существующие заметки без подтверждения

## Memory
- brain/Index.md — накопленные паттерны и решения
- brain/Decisions.md — архитектурные решения
- brain/Patterns.md — выявленные паттерны
- brain/Mistakes.md — ошибки, которых стоит избегать
```

### Структура vault

```
vault/
├── CLAUDE.md           # инструкции для Claude Code
├── brain/              # память агента
│   ├── Index.md
│   ├── Decisions.md
│   ├── Patterns.md
│   └── Mistakes.md
├── projects/           # проекты
│   └── ai-agency-platform/
├── daily-notes/        # ежедневные заметки
└── inbox/              # входящие
```

**Плюсы:** нулевая сложность, работает сразу, бесплатно
**Минусы:** нет структурированного поиска, только ручное чтение файлов по путям

---

## Метод 2: MCP-сервер для Obsidian

MCP-сервер даёт Claude Code набор инструментов (tools) для работы с vault: поиск, чтение, запись, теги. Работает из любой директории.

### Вариант A: `obsidian-mcp` (рекомендуемый)

Работает напрямую с файлами. Obsidian не обязан быть запущен.

**Установка:**

```bash
# Требуется Node.js 20+
```

Добавить в `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp", "/Users/ak/ObsidianVault"]
    }
  }
}
```

Перезапустить Claude Code.

**Доступные инструменты:**
- `read-note`, `create-note`, `edit-note`, `delete-note`, `move-note`
- `search-vault` — полнотекстовый поиск
- `add-tags`, `remove-tags`, `rename-tag`
- `create-directory`, `list-available-vaults`

### Вариант B: Filesystem MCP (от Anthropic)

Минимальный MCP — стандартный файловый сервер:

```json
{
  "mcpServers": {
    "vault": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/ak/ObsidianVault"]
    }
  }
}
```

### Вариант C: `mcp-obsidian` (через REST API)

Требует запущенный Obsidian с плагином **Local REST API**.

1. В Obsidian: Settings -> Community Plugins -> установить "Local REST API"
2. Включить плагин, запомнить API-ключ и порт (обычно 27124)
3. Конфигурация:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "@mseep/obsidian-mcp-server"],
      "env": {
        "OBSIDIAN_API_KEY": "ваш-ключ",
        "OBSIDIAN_API_PORT": "27124"
      }
    }
  }
}
```

> **Важно:** Python-based MCP-серверы имеют известный баг `BrokenPipeError` в Claude Code CLI. Используйте Node.js-реализации.

**Плюсы MCP:** структурированный поиск, работает из любой директории, несколько vault
**Минусы:** зависимость от Node.js/npx, read/write доступ — делать бэкап vault

---

## Метод 3: Автоматическая память через хуки Claude Code

Claude Code hooks извлекают инсайты из каждой сессии и сохраняют в vault. Память растёт автоматически.

### Архитектура

```
Сессия завершается
  → Hook "Stop" срабатывает
    → Python-скрипт анализирует транскрипт
      → Claude API (Haiku) извлекает паттерны/ошибки/решения
        → Markdown-заметки в vault
          → CLAUDE.md ссылается на Index.md
            → Следующая сессия читает накопленные знания
```

### Настройка

1. Создать структуру:

```bash
mkdir -p ~/ObsidianVault/claude-memory/{Patterns,Mistakes,Decisions,Context,Sessions}
```

2. Настроить хуки в `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/memory_extractor.py"
          }
        ]
      }
    ]
  }
}
```

3. Создать скрипт `~/.claude/hooks/memory_extractor.py`:
   - Получает JSON через stdin (session_id, project directory)
   - Отправляет транскрипт в Claude API (Haiku — ~$0.01/сессия)
   - Создаёт `.md`-файлы с YAML frontmatter
   - Обновляет `Index.md`

4. Экспортировать API-ключ:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

5. Добавить в проектный `CLAUDE.md`:

```markdown
## Project Memory
- ~/ObsidianVault/claude-memory/Index.md — накопленные паттерны
- ~/ObsidianVault/claude-memory/Context/ — контекст проектов
- ~/ObsidianVault/claude-memory/Decisions/ — архитектурные решения
- ~/ObsidianVault/claude-memory/Mistakes/ — известные ошибки
```

**Плюсы:** полностью автоматическая, растёт с каждой сессией, дёшево (~$0.01/сессия)
**Минусы:** требует API key, сложная первоначальная настройка (~1-2 часа), нужна периодическая чистка

---

## Метод 4: Готовые шаблоны vault

### Obsidian Mind (`breferrari/obsidian-mind`)

Наиболее полное готовое решение: vault-шаблон с 5 хуками, 18 slash-командами и 9 подагентами.

```bash
npm install -g shardmind
mkdir my-vault && cd my-vault
shardmind install github:breferrari/obsidian-mind
```

**Что включено:**
- `CLAUDE.md` — полный мануал для агента
- Папка `brain/` — цели, решения, паттерны, ошибки, воспоминания
- 5 lifecycle hooks: SessionStart, UserPromptSubmit, PostToolUse, PreCompact, Stop
- 18 команд: `/om-standup`, `/om-dump`, `/om-wrap-up`, `/om-weekly`
- 9 подагентов: brag-spotter, vault-librarian, cross-linker
- Мульти-агентная совместимость (Claude Code, Codex CLI, Gemini CLI)

### claude-code-memory-setup (`lucasrosati/claude-code-memory-setup`)

Фокус на экономии токенов. Заявляется снижение расхода в 71.5 раз.

**Три слоя:**
1. **Obsidian Zettelkasten** — атомарные заметки с wikilinks
2. **Graphify** — AST-парсинг кодовой базы → `graph.json` (332 узла из 126 файлов = 172 КБ)
3. **Chat Import Pipeline** — автоимпорт разговоров с Claude в vault

```bash
pip install graphifyy && graphify install
graphify . --obsidian --obsidian-dir ~/vault/graphify/project-name
```

---

## Метод 5: Obsidian-плагины с Claude Code

### Claudian (`YishenTu/claudian`)

Obsidian-плагин, встраивающий Claude Code прямо в sidebar. Vault = рабочая директория агента.

### Agent Client

Плагин для запуска Claude Code, Codex и Gemini CLI внутри Obsidian (требует Obsidian 1.12+).

---

## Сравнительная таблица

| Метод | Сложность | Время | Автоматизация | Лучше всего для |
|-------|-----------|-------|---------------|-----------------|
| Прямой доступ | Минимальная | 5 мин | Нет | Быстрый старт |
| MCP-сервер | Низкая | 10-15 мин | Частичная | Поиск по vault из любого проекта |
| Хуки + memory extractor | Высокая | 1-2 часа | Полная | Долгосрочная работа |
| Obsidian Mind (шаблон) | Средняя | 30 мин | Полная | Комплексное решение "из коробки" |
| Плагины в Obsidian | Низкая | 10 мин | Нет | Работа внутри Obsidian |

---

## Рекомендация для AI Agency Platform

### Поэтапный план

**Фаза 1 — сейчас (5 минут):**
- Создать vault (или использовать существующий)
- Добавить `CLAUDE.md` с инструкциями
- Запускать `claude` из директории vault когда нужна работа с памятью

**Фаза 2 — при активной разработке (15 минут):**
- Подключить `obsidian-mcp` как MCP-сервер
- Claude Code получает доступ к vault из любой рабочей директории

**Фаза 3 — при регулярной работе (1-2 часа):**
- Настроить хуки для автоматического извлечения инсайтов
- Или попробовать Obsidian Mind как готовый шаблон

### Ключевое понимание

Vault **не нужно** загружать целиком в контекст. Claude Code открывает только нужные файлы, а `CLAUDE.md` служит "картой" к знаниям. Это принципиально отличается от RAG — здесь агент сам решает, что прочитать.

---

## Ссылки

- [obsidian-mcp (StevenStavrakis)](https://github.com/StevenStavrakis/obsidian-mcp)
- [mcp-obsidian (MarkusPfundstein)](https://github.com/MarkusPfundstein/mcp-obsidian)
- [Obsidian Mind](https://github.com/breferrari/obsidian-mind)
- [claude-code-memory-setup](https://github.com/lucasrosati/claude-code-memory-setup)
- [Claudian plugin](https://github.com/YishenTu/claudian)
- [claude-knowledge-graph](https://github.com/NAMYUNWOO/claude-knowledge-graph)
- [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers)
