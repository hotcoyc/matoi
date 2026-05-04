# Используемые проекты

Сторонние open-source проекты, интегрированные в Matoi.

---

## [MemPalace](https://github.com/mempalace/mempalace) -- память агентов

**Что:** Иерархическая система памяти для AI-агентов. ChromaDB + SQLite, семантический поиск (96.6% recall), knowledge graph с темпоральными тройками.

**Как используем:**
- Память между сессиями -- артефакты pipeline индексируются автоматически
- 433 drawers проекта загружены (код, docs, agents)
- 29 MCP-инструментов для Claude Code
- Auto-save hooks (Stop, PreCompact)
- Knowledge graph для связей между решениями
- Python API: `MemoryStack`, `search_memories()`, `KnowledgeGraph`

**Лицензия:** MIT | **Stars:** ~51K

---

## [code-review-graph](https://github.com/tirth8205/code-review-graph) -- навигация AI по коду

**Что:** Граф знаний кодовой базы через Tree-sitter. Строит карту: файлы, функции, классы, зависимости, вызовы.

**Как используем:**
- 210 nodes, 1317 edges нашего проекта
- 28 MCP-инструментов для Claude Code (query_graph, detect_changes, get_impact_radius, semantic_search)
- Auto-update через git pre-commit hook и PostToolUse hook
- HTML-визуализация: `matoi viz graph`
- Экономия токенов 6.8-49x vs чтение файлов целиком

**Лицензия:** MIT | **Stars:** ~15K

---

## [CodeCharta](https://github.com/MaibornWolff/codecharta) -- 3D визуализация

**Что:** Визуализация кода как 3D-город. Файлы = здания (высота = сложность, площадь = строки кода), папки = районы.

**Как используем:**
- `matoi viz city` -- генерирует `.cc.json.gz` и открывает viewer
- `matoi viz build` -- пересборка при онбординге
- Визуальный обзор архитектуры для новых участников

**Требует:** Java 17+, npm | **Лицензия:** BSD-3 | **Stars:** ~411

---

## [Superpowers](https://github.com/obra/superpowers) -- поведенческие паттерны агентов

**Что:** Agentic skills framework с Iron Laws, self-review checklists, escalation rules.

**Как используем:**
- Вдохновение для поведенческих описаний 17 агентов Matoi
- Протоколы из Superpowers адаптированы:
  - TDD discipline (Backend Engineer)
  - "No fixes without root cause" (Systematic Debugger -> QA)
  - Distrustful verification (Spec Compliance -> QA Strategist)
  - "Design before code" (Brainstormer -> Product Designer)
  - Anti-sycophancy (Code Review Recipient -> all Critics)

**Лицензия:** MIT | **Stars:** ~165K

---

## [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) -- LLM gateway

**Что:** Официальный SDK для Claude API.

**Как используем:**
- `client.messages.create()` -- non-streaming calls (conflict detection, activation)
- `client.messages.stream()` -- streaming calls (brief, expert pass, synthesis)
- Cost tracking через `message.usage.input_tokens/output_tokens`
- Error handling: retry на rate limits (429), connection errors, server errors (5xx), overloaded (529)

---

## [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) -- TUI

**Что:** Библиотека для интерактивных CLI с автокомплитом, историей, keybindings.

**Как используем:**
- Интерактивная REPL-сессия `matoi`
- Цветной промпт `[project/PM] >` (зелёный/жёлтый)
- Tab-автокомплит: `/commands` и `@agents` (fuzzy)
- Persistent history `~/.matoi/history`
- Bottom status bar: PM, team, tokens, cost
- Keybindings: Ctrl+C, Ctrl+D, Ctrl+L, Alt+Enter

---

## [Rich](https://github.com/Textualize/rich) -- terminal rendering

**Что:** Библиотека для красивого вывода в терминал.

**Как используем:**
- Rich Markdown: live rendering ответов агентов (заголовки, списки, код)
- Rich Live: обновление markdown при streaming
- Rich Table: таблицы агентов, cost breakdown, team list
- Rich Panel: карточки агентов, аватары
- Rich Console: цветной вывод, rule-разделители

---

## [Pillow](https://github.com/python-pillow/Pillow) -- pixel-art аватары

**Что:** Библиотека обработки изображений.

**Как используем:**
- Конвертация pixel-art PNG (128x128) в Braille Unicode для терминала
- Автоматический ресайз до 30 символов ширины
- 17 аватаров агентов
