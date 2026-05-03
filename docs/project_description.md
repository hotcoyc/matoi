Идея:
- есть каталог агентов в Markdown
- каждый агент уникален по роли, стилю, способностям, ограничениям, инструментам и model policy
- пользователь выбирает до 5 агентов в команду
- особенно важны разные PM-агенты, которые могут по-разному управлять командой и рекомендовать состав
- агенты должны не просто отвечать, а взаимодействовать, спорить, критиковать решения и синтезировать итог
- система должна быть cost-aware: разные модели для разных шагов и ролей
- продукт должен работать в CLI
- референс по агентам: https://github.com/nacerallahchemssy/agency-agents
- основа исполнения: Claude Code / subagents / orchestration

Важно:
- не делать бессмысленный multi-agent theater
- debate только там, где есть реальный конфликт
- не все агенты активны всегда
- результатом должны быть артефакты: brief, plan, decision, tasks, conflicts, debate notes
- нужен formal orchestration pipeline

Спроектируй:
1. product vision
2. MVP scope
3. system architecture
4. agent registry schema
5. team composition logic
6. orchestration flow
7. conflict detection
8. debate protocol
9. synthesis
10. model routing and budget control
11. CLI commands
12. file structure
13. data models
14. failure modes
15. roadmap