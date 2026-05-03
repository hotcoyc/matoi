# GitHub Projects

## 1. [Superpowers](https://github.com/obra/superpowers)
**"An agentic skills framework & software development methodology that works."**

Комплексная система для coding-агентов, которая направляет их через структурированные рабочие процессы разработки вместо прямого погружения в код. Объединяет компонуемые навыки с автоматическим запуском лучших практик (TDD, систематическая отладка, совместное планирование) для автономной работы агентов над сложными проектами с поддержанием качества кода.

## 2. [Anthropic Skills](https://github.com/anthropics/skills/tree/main/skills)
**Коллекция навыков и инструментов для Claude от Anthropic**

Курируемый набор из 17+ специализированных модулей расширяющих возможности Claude: интеграция с API, обработка документов (PDF, DOCX, PPTX, XLSX), инструменты дизайна (canvas, frontend, theme factory), утилиты (MCP builder, web artifacts builder, skill creator). Модульная и переиспользуемая архитектура.

## 3. [claude-mem](https://github.com/thedotmack/claude-mem)
**"Persistent memory compression system for Claude Code"**

Плагин для Claude Code, автоматически захватывающий все действия во время сессий, сжимающий их с помощью AI и внедряющий релевантный контекст в будущие сессии. Записывает наблюдения, генерирует семантические сводки и извлекает нужный контекст через интеллектуальный поиск.

## 4. [gstack](https://github.com/garrytan/gstack)
**"Use Garry Tan's exact Claude Code setup: 23 opinionated tools that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA"**

Open-source "фабрика ПО", превращающая Claude Code в виртуальную инженерную команду через специализированных AI-агентов. Оркестрирует полный цикл разработки — от стратегического планирования и дизайна до имплементации, ревью, тестирования и деплоя — через slash-команды и Markdown-коллаборацию.

## 5. [GitNexus](https://github.com/abhigyanpatwari/GitNexus)
**"The Zero-Server Code Intelligence Engine"**

Клиентский движок knowledge graph, работающий целиком в браузере или через CLI. Индексирует кодовые базы в интерактивные графы знаний, отслеживающие зависимости, цепочки вызовов и потоки выполнения. Интеграция с AI-агентами (Claude Code, Cursor) через MCP для архитектурного анализа, планирования рефакторинга и impact-анализа.

## 6. [cpr-compress-preserve-resume](https://github.com/EliaAlberti/cpr-compress-preserve-resume/tree/main)
**"Persistent memory for Claude Code. Save, search, and restore conversation context across sessions."**

Три кастомных навыка (/preserve, /compress, /resume), обеспечивающих сохранение контекста между сессиями Claude Code. Позволяют сохранять ключевые выводы в CLAUDE.md, захватывать полные логи сессий для поиска и восстанавливать предыдущий контекст при начале новых разговоров.

## 7. [claude-knowledge-graph](https://github.com/NAMYUNWOO/claude-knowledge-graph)
**"Auto-capture Claude Code Q&A -> Qwen 3.5 tagging/summarization -> Obsidian knowledge graph"**

Инструмент автоматического захвата диалогов из Claude Code с обработкой через локальную LLM (Qwen 3.5 4B) для генерации тегированных и суммаризованных заметок в Obsidian vault. Создает связанный граф знаний с концептуальными связями, семантическим поиском и профилированием разработчика. Все данные обрабатываются локально.

## 8. [gitVis3D](https://github.com/kofujimura/gitVis3D)
**"3D Visualization of Git Repository"**

Инструмент визуализации истории коммитов git-репозитория в виде анимированных 3D-графов, отображающих связи вкладов и обновлений как узлы и ребра, появляющиеся последовательно во времени. Получает данные коммитов через GitHub API и хранит графы в Neo4j.

## 9. [code-review-graph](https://github.com/tirth8205/code-review-graph)
**"Persistent code knowledge graph for Claude Code"** (~15K stars)

Локальный граф знаний кодовой базы для Claude Code. Строит persistent карту проекта через Tree-sitter: файлы, функции, классы, зависимости, цепочки вызовов. Отслеживает изменения инкрементально — при каждом изменении обновляется только затронутая часть графа. Агент читает только то, что реально нужно — доказанная экономия токенов в 6.8x на ревью и до 49x на ежедневных задачах (с 739K до 15K токенов). Интеграция через MCP — Claude Code получает инструменты для навигации по графу вместо чтения файлов целиком.

**Роль в платформе:** навигация AI-агентов по кодовой базе проекта, экономия токенов при анализе кода, структурированный контекст для Engineering-агентов (Backend/Frontend Engineer, DevOps) и Critics (Security Reviewer, QA Strategist).

## 10. [CodeCharta](https://github.com/MaibornWolff/codecharta)
**"Interactive visualization of code as a 3D city"** (~411 stars)

Визуализация архитектуры ПО в виде интерактивного 3D-города: файлы = здания (высота = сложность, цвет = покрытие тестами, площадь = строки кода), папки = районы. Поддерживает сравнение двух карт для визуализации дельты изменений. Импорт метрик из SonarQube, токклаков (tokei, cloc), git log, SVN. Экспорт в JSON и 3D-модель (можно напечатать на 3D-принтере).

**Роль в платформе:** визуальный обзор архитектуры проекта для Design & Product и Strategy & Business агентов, отслеживание эволюции кодовой базы, выявление hotspots (сложные/часто меняющиеся файлы) для QA Strategist и Backend Architect.

## 11. [Repomix](https://github.com/yamadashy/repomix)
**"Pack your entire repository into a single, AI-friendly file"** (~23K stars)

CLI-инструмент, упаковывающий весь репозиторий в один структурированный файл, оптимизированный для LLM. Smart token compression с сохранением структуры проекта — дерево файлов, содержимое с разделителями, метаданные. Поддержка форматов вывода: XML, Markdown, Plain text. Встроенная фильтрация по .gitignore, настраиваемые include/exclude паттерны, подсчёт токенов. Есть веб-интерфейс, Chrome-расширение и MCP-сервер.

**Роль в платформе:** быстрая передача полного контекста проекта AI-агентам при первичном анализе — Research-агенты (Market Researcher, Competitive Analyst) и Strategy-агенты (CEO/Visionary, Business Analyst) получают snapshot всего проекта одним файлом для понимания текущего состояния. PM-агенты используют для формирования brief с учётом реальной кодовой базы.
