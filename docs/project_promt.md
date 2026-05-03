Ты — senior staff-level AI product architect, multi-agent systems designer и technical founder advisor. Твоя задача — спроектировать CLI-платформу для сборки и оркестрации команды из ИИ-агентов, которые совместно работают над задачами пользователя.

## 1. Общая идея проекта

Я хочу создать CLI-платформу, в которой пользователь сам собирает себе команду из ИИ-агентов под конкретную задачу или проект.

На платформе будет каталог специалистов в формате Markdown. Каждый специалист — это отдельный ИИ-агент с уникальной ролью, специализацией, сильными и слабыми сторонами, стилем мышления, ограничениями, инструментами и модельной политикой.

Примеры ролей:
- project manager
- product manager
- startup PM
- delivery PM
- frontend engineer
- backend engineer
- backend architect
- product designer
- UX researcher
- QA strategist
- security reviewer
- performance reviewer
- tech lead
- product strategist

Пользователь выбирает себе команду, например из 5 ИИ-агентов.

Главная фишка платформы:
агенты не просто по очереди отвечают, а **взаимодействуют друг с другом**, обсуждают задачу, спорят, предлагают разные варианты решения, критикуют слабые места, выявляют риски и затем приходят к более сильному совместному решению.

Каждому агенту может соответствовать своя ИИ-модель или модельная политика. Это нужно для оптимизации стоимости:
- простые шаги выполняются дешёвыми моделями
- более сложные шаги — средними
- критически важные решения, синтез, архитектурные развилки — дорогими и более сильными моделями

Также на платформе будет несколько разных project-manager агентов с различными стилями и компетенциями.
Например:
- startup PM
- delivery PM
- enterprise PM
- product strategist PM

Если пользователь выбирает PM-агента, этот PM может:
- интерпретировать задачу
- предложить состав команды
- рекомендовать, каких специалистов стоит взять
- аргументировать, почему именно этот состав оптимален
- управлять взаимодействием между агентами
- синтезировать финальное решение

Платформа должна быть реализована **в CLI**, а не в веб-интерфейсе.
Она должна быть ориентирована на terminal-first UX и на использование в реальном рабочем процессе.

В качестве референса по идее агентов можно использовать проект:
https://github.com/nacerallahchemssy/agency-agents

Но моя система должна быть не просто библиотекой агентных описаний, а полноценной **операционной системой ИИ-команды**, где есть:
- registry агентов
- team composition
- orchestration
- debate
- synthesis
- artifacts
- cost-aware execution
- CLI experience

## 2. Продуктовое видение

Эта платформа — не “ещё один чат с ИИ”, а система, где пользователь получает ощущение, что он собрал себе настоящую мини-команду:
- PM управляет
- дизайнер думает о UX
- фронтендер предлагает UI-реализацию
- бэкендер думает о данных и API
- QA указывает на риски
- security reviewer ловит уязвимости
- architect спорит со всеми, если решение не масштабируется

Цель — создать ощущение реальной командной работы, но при этом не допустить хаоса, избыточной стоимости и пустых обсуждений.

Важно:
агенты должны спорить и обсуждать задачу не ради шоу, а ради улучшения качества решения.

## 3. Проблема, которую решает продукт

Обычный single-agent AI часто:
- даёт слишком линейный ответ
- не показывает альтернативы
- не создаёт полезное напряжение между разными точками зрения
- не имитирует кросс-функциональное обсуждение
- не умеет естественно распределять мышление по ролям
- либо слишком дорогой, если всё делать одной мощной моделью

Я хочу решить это за счёт:
- композиции ролей
- формального протокола взаимодействия
- экономически оптимального выбора моделей
- оркестрации через CLI
- сохранения полезных артефактов, а не только текста разговора

## 4. Ключевые принципы системы

Система должна строиться на следующих принципах:

### 4.1. Пользователь собирает команду
Пользователь может:
- выбрать агентов вручную
- выбрать PM, который предложит состав команды
- использовать заранее подготовленные team presets

### 4.2. Агенты специализированы
Каждый агент имеет:
- чёткую роль
- специализацию
- системный промпт
- responsibilities
- strengths
- weaknesses
- activation rules
- debate style
- model policy
- allowed tools
- permissions
- collaboration preferences

### 4.3. Не все агенты вызываются всегда
Если агент выбран в команду, это не означает, что он обязательно участвует в каждом шаге.
Нужна selective activation logic.

### 4.4. Debate — это режим, а не хаос
Агенты не должны всегда читать весь контекст и бесконечно спорить.
Нужен управляемый протокол:
- intake
- brief
- independent expert pass
- conflict detection
- debate only on relevant disagreements
- synthesis
- artifacts

### 4.5. Всё должно быть cost-aware
Система должна уметь:
- использовать дешёвые модели для простых задач
- эскалировать на сильные модели только там, где это действительно нужно
- ограничивать количество debate rounds
- ограничивать число premium calls
- считать стоимость выполнения сессии

### 4.6. Основной результат — артефакты
На выходе должны создаваться артефакты:
- brief.md
- plan.md
- decision.md
- debate.md
- conflicts.json
- tasks.json
- agent-opinions/*.md
- architecture.md
- qa-checklist.md

## 5. Что именно должна делать система

Платформа должна позволять:

### 5.1. Управлять каталогом агентов
Агенты хранятся как Markdown-файлы с YAML frontmatter.
Один агент = один markdown-файл.

### 5.2. Собирать команды
Пользователь может:
- создать команду
- добавить или удалить агентов
- назначить PM
- сохранять пресеты команд

### 5.3. Запускать задачи
Пользователь запускает задачу из CLI, например:
- разработать MVP
- спроектировать архитектуру
- решить продуктовый вопрос
- обсудить компромисс
- выполнить реализацию
- подготовить roadmap

### 5.4. Получать совместное решение
Система должна:
1. понять задачу
2. определить активных агентов
3. дать PM возможность составить brief
4. провести независимый expert pass
5. обнаружить конфликты
6. провести структурированный debate
7. синтезировать итоговое решение
8. сформировать артефакты
9. показать пользователю финальный результат и стоимость

## 6. Желаемая архитектура продукта

Я хочу, чтобы система была разбита на следующие слои:

1. CLI Layer
2. Application Layer
3. Orchestration Layer
4. Agent Runtime Layer
5. Storage Layer
6. Model Gateway Layer

### 6.1. CLI Layer
Команды терминала:
- agency init
- agency agents list
- agency agents show
- agency team create
- agency team add
- agency team remove
- agency team recommend
- agency task run
- agency task plan
- agency task exec
- agency session list
- agency artifacts list
- agency cost

#### 6.1.1. Визуальные персонажи агентов в CLI

При выборе PM (и других ключевых агентов) в терминале отрисовываются ASCII/Braille-арт портреты персонажей — узнаваемые, с характером. Каждый PM визуально отличается и сопровождается:
- ASCII/Braille-арт аватаром (формат Unicode Braille dots, ~10-15 строк высотой)
- Фразой-девизом, отражающей стиль управления
- Ключевыми характеристиками (risk tolerance, focus, preferred team size)

Это не декоративная фича — визуальная идентичность помогает пользователю интуитивно понять разницу между PM-агентами и осознанно выбирать стиль управления командой.

Реализация:
- Исходные изображения персонажей конвертируются в Braille Unicode art
- Библиотеки: drawille (Braille dots), ascii-magic или img2unicode (конвертация), Rich (панели, цвет, layout)
- Персонажи хранятся как предрассчитанные текстовые файлы в `assets/avatars/`
- Интерактивный выбор: навигация стрелками, Enter для выбора
- Поддержка fallback на простой текстовый список для узких терминалов

### 6.2. Orchestration Layer
Оркестратор должен:
- выбирать активных агентов
- управлять порядком исполнения
- решать, где нужен debate
- ограничивать число раундов
- контролировать бюджет
- запускать synthesis

### 6.3. Agent Runtime Layer
Должен быть слой, который:
- строит контекст для агента
- подставляет правильный prompt template
- выбирает модель по policy
- вызывает нужный runtime
- получает usage/cost metadata

### 6.4. Storage Layer
Нужно хранить:
- registry
- team configs
- sessions
- artifacts
- usage/cost logs
- transcripts

### 6.5. Model Gateway Layer
Нужна абстракция над модельными провайдерами:
- cheap
- balanced
- premium
  с возможностью маршрутизации по типу шага, а не только по агенту.

## 7. Протокол взаимодействия агентов

Я хочу, чтобы базовый pipeline был таким:

### Этап 1. Intake
Система получает raw user request.

### Этап 2. PM Brief
PM-агент формулирует:
- цель
- ограничения
- deliverables
- открытые вопросы
- execution proposal

### Этап 3. Independent Expert Pass
Каждый активный агент независимо отвечает:
- как он понимает задачу
- что предлагает
- какие видит риски
- от чего зависит его решение
- с чем потенциально не согласен

Важно:
на этом шаге агенты не должны слепо копировать мнения друг друга.

### Этап 4. Conflict Detection
Система выявляет реальные расхождения:
- разные tech stack choices
- разные product tradeoffs
- разные architectural assumptions
- разные UX priorities
- разные scope decisions

### Этап 5. Debate
Если конфликт есть, в debate идут только релевантные агенты.
Дебат должен быть структурированным:
- claim
- critique
- alternative
- tradeoff
- recommendation

### Этап 6. Synthesis
PM или synthesizer-agent формирует:
- финальное решение
- rationale
- rejected alternatives
- риски
- план следующих шагов

### Этап 7. Artifacts
Система сохраняет все важные результаты в файлы.

## 8. Роли агентов

Я хочу, чтобы в системе были разные типы агентов:

### 8.1. Coordinators
- startup PM
- delivery PM
- enterprise PM
- tech lead

### 8.2. Executors
- frontend engineer
- backend engineer
- product designer
- QA strategist

### 8.3. Thinkers
- backend architect
- product strategist
- UX researcher

### 8.4. Critics
- security reviewer
- performance reviewer
- accessibility reviewer
- cost optimizer

Важно:
агенты должны отличаться не декоративно, а операционно.
То есть различия должны быть в:
- decision style
- risk tolerance
- scope behavior
- preferred artifacts
- escalation threshold
- collaboration style
- model policy
- tool access

## 9. PM-агенты как ключевая дифференциация

Особенно важно, чтобы несколько project-manager агентов реально отличались друг от друга.

Например:

### Startup PM
- фокус на скорости
- любит урезать scope
- предпочитает ship fast
- терпим к риску
- выбирает минимальную рабочую команду

### Delivery PM
- фокус на предсказуемости
- любит чёткую декомпозицию
- следит за блокерами
- думает о сроках и последовательности

### Enterprise PM
- фокус на надёжности, процессах и контроле рисков
- требует документацию
- не любит смелые решения без обоснования

### Product Strategist PM
- фокус на ценности для пользователя
- может спорить с инженерами ради UX и market fit

PM должен уметь:
- предлагать состав команды
- аргументировать выбор ролей
- модерировать debate
- синтезировать решение

## 10. Ограничения и риски

Проект не должен превратиться в:
- бесконечную болтовню агентов
- дорогое театрализованное шоу
- хаотичную peer-to-peer сеть без контроля
- систему, где все агенты всегда получают весь контекст
- симуляцию “умной команды”, которая не производит реальных артефактов

Поэтому нужны:
- deterministic orchestration
- explicit stop conditions
- budget limits
- selective context injection
- structured outputs
- activation rules
- conflict-triggered debate instead of always-on debate

## 11. Техническая реализация

Платформа должна быть реализована как terminal-first CLI продукт.
В качестве технологической базы предпочтительно:
- Python для MVP
- Markdown + YAML frontmatter для registry
- JSON/YAML для team configs
- SQLite/JSON для хранения сессий и метрик
- Claude Code как runtime foundation
- возможность использовать subagents
- cost tracking
- artifact-centric execution

## 12. Ожидаемый результат от тебя

Мне нужен не поверхностный комментарий, а deep technical and product design output.

Когда отвечаешь, делай это как senior systems/product architect.

Я хочу, чтобы ты помог спроектировать этот продукт на уровне:
- product architecture
- system design
- agent protocol
- data models
- registry schema
- team composition logic
- conflict detection logic
- debate engine
- synthesis engine
- CLI UX
- file/folder structure
- config formats
- cost control strategy
- roadmap
- MVP scope
- risk analysis

## 13. Формат ответа

Отвечай структурированно, глубоко и practically useful.

Используй такую структуру:

1. Vision summary
2. Core product thesis
3. MVP scope
4. System architecture
5. Domain model
6. Agent registry design
7. Team composition logic
8. Orchestration pipeline
9. Debate protocol
10. Model routing strategy
11. Cost-control strategy
12. CLI design
13. File structure
14. Data schemas
15. Artifact strategy
16. Failure modes and safeguards
17. Roadmap from MVP to v2
18. Recommended implementation steps
19. Risks and anti-patterns
20. Final architectural recommendation

Если нужно, добавляй:
- таблицы
- YAML examples
- markdown schemas
- pseudocode
- class design
- CLI examples
- state transitions
- decision frameworks

## 14. Важные требования к качеству ответа

Твой ответ должен:
- быть прагматичным
- быть детализированным
- быть ориентированным на реализацию
- избегать воды и банальностей
- не сводить всё к абстрактному “сделай мультиагентную систему”
- помогать реально строить продукт
- учитывать стоимость исполнения
- учитывать UX в CLI
- учитывать, что debate должен быть полезным, а не декоративным
- учитывать, что агентная система должна производить артефакты
- учитывать, что PM-агенты — важная часть differentiation

## 15. Дополнительная задача

Где уместно, предлагай:
- как лучше ограничить хаос
- как уменьшить стоимость
- как сделать агентов реально различающимися
- как формализовать командную работу
- как не превратить продукт в бессмысленный multi-agent theater
- как измерять успех платформы по метрикам

В конце дай честную оценку:
- насколько идея жизнеспособна
- где её главные риски
- что нужно сделать в первую очередь
- какой MVP будет самым правильным