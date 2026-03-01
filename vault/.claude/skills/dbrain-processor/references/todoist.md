# Todoist Integration

## Task Links Format

ВАЖНО: Todoist изменил формат ссылок. Используй НОВЫЙ формат:

✅ Правильно: `https://app.todoist.com/app/task/{task_id}`
❌ Устарело: `https://todoist.com/showTask?id={task_id}`
❌ Устарело: `https://todoist.com/app/task/{task_id}`

Если MCP tool вернул task с `url` полем — используй его напрямую.
Если нужно построить ссылку из task_id — используй формат выше.

---

## Todoist через mcp-cli

**ВСЕГДА используй mcp-cli. НЕ используй MCP tools напрямую.**

### Reading Tasks

```bash
# Обзор всех проектов
mcp-cli call todoist get-overview '{}'

# Поиск по тексту, проекту, секции
mcp-cli call todoist find-tasks '{"searchText": "keyword"}'

# Задачи по дате
mcp-cli call todoist find-tasks-by-date '{"startDate": "today", "daysCount": 7}'
```

### Writing Tasks

```bash
# Создать задачу
mcp-cli call todoist add-tasks '{"tasks": [{"content": "Task", "dueString": "tomorrow", "priority": 2}]}'

# Завершить задачу
mcp-cli call todoist complete-tasks '{"ids": ["task_id"]}'

# Обновить задачу
mcp-cli call todoist update-tasks '{"tasks": [{"id": "task_id", "content": "New title"}]}'
```

---

## Pre-Creation Checklist

### 1. Check Workload (REQUIRED)

```bash
mcp-cli call todoist find-tasks-by-date '{"startDate": "today", "daysCount": 7, "limit": 50}'
```

Build workload map:
```
Mon: 2 tasks
Tue: 4 tasks  ← overloaded
Wed: 1 task
Thu: 3 tasks  ← at limit
Fri: 2 tasks
Sat: 0 tasks
Sun: 0 tasks
```

### 2. Check Duplicates (REQUIRED)

```bash
mcp-cli call todoist find-tasks '{"searchText": "key words from new task"}'
```

If similar exists → mark as duplicate, don't create.

---

## Priority by Domain

Based on John's work context (see [about.md](about.md)):

| Domain | Default Priority | Override |
|--------|-----------------|----------|
| FiveBBC клиенты (оптовики) | p1-p2 | — |
| FiveBBC операции (срочные) | p2 | — |
| FiveBBC операции (обычные) | p3 | — |
| SEO / Контент (с дедлайном) | p2-p3 | — |
| Infrastructure (VPS, Docker, SSH) | p2-p3 | блокирует работу → p1 |
| Книга «Проснись!» | p3 | дедлайн → p2 |
| Personal Growth (практика, рефлексия) | p3 | — |
| Крипто-бот / R&D | p4 | автоматизация → p3 |
| AI & Tech (инструменты) | p4 | автоматизация → p3 |
| New:{домен} / #unclassified | p4 | пользователь повысил → любой |

### Priority Keywords

| Keywords in text | Priority |
|-----------------|----------|
| срочно, критично, клиент ждёт, рефилл | p1 |
| важно, приоритет, до конца недели, дроп | p2 |
| нужно, надо, не забыть, добавить услугу | p3 |
| стратегия, R&D, бот, крипто, эксперимент | p4 |

### Apply Decision Filters for Priority Boost

If entry matches 2+ filters → boost priority by 1 level:
- Это масштабируется?
- Это можно автоматизировать?
- Это усиливает SEO или трафик FiveBBC?
- Это приближает к пассивному доходу ($100K/мес цель)?

---

## Date Mapping

| Context | dueString |
|---------|-----------|
| Клиент ждёт / рефилл | today / tomorrow |
| Срочные операции | today / tomorrow |
| На этой неделе | friday |
| На следующей неделе | next monday |
| Стратегия / R&D / книга | in 7 days |
| Не указано | in 3 days |

### Russian → dueString

| Russian | dueString |
|---------|-----------|
| сегодня | today |
| завтра | tomorrow |
| послезавтра | in 2 days |
| в понедельник | monday |
| в пятницу | friday |
| на этой неделе | friday |
| на следующей неделе | next monday |
| через неделю | in 7 days |
| 15 января | January 15 |

---

## Task Creation

```bash
mcp-cli call todoist add-tasks '{"tasks": [{"content": "Task title", "dueString": "friday", "priority": 4}]}'
```

С projectId:
```bash
mcp-cli call todoist add-tasks '{"tasks": [{"content": "Task title", "dueString": "friday", "priority": 4, "projectId": "..."}]}'
```

### Task Title Style

John предпочитает: прямота, ясность, конкретика

✅ Good:
- "Прогнать SEO-аудит на странице /buy-instagram-followers"
- "Добавить новую услугу TikTok views в каталог"
- "Написать money page для YouTube subscribers"
- "Проверить рефилл для оптового клиента"
- "1 час: инвентаризация исходников книги"

❌ Bad:
- "Подумать о SEO"
- "Что-то с услугами"
- "Разобраться с книгой"

### Workload Balancing

If target day has 3+ tasks:
1. Find next day with < 3 tasks
2. Use that day instead
3. Mention in report: "сдвинуто на {day} (перегрузка)"

---

## Project Detection

Based on John's work domains (synced with classification.md):

| Keywords | Project |
|----------|---------|
| FiveBBC, панель, услуга, каталог, клиент, рефилл, дроп, заказ | FiveBBC Ops |
| SEO, аудит, DataForSEO, ключевое слово, SERP, статья, money page | SEO & Content |
| книга, Проснись, том, глава, исходник, инвентаризация | Book |
| бот, крипто, арбитраж, биржа, DEX, Web3 | Crypto (R&D) |
| агент, Claude Code, MCP, пайплайн, скилл | AI & Tech |
| VPS, Docker, SSH, сервер, деплой, nginx, DNS | Infrastructure |
| Стас, Дима, команда, процесс | Team & Ops |
| практика, внимание, медитация, сон, энергия, тень | Personal Growth |

### Fallback (synced with classification.md Fallback Classification)

Если задача не попадает ни в один проект:
1. Есть смысловое пересечение → ближайший проект + label `unclassified`
2. Абсолютно новая тема → Inbox (no projectId) + label `new-domain`
3. В отчёте указать: «Тема не классифицирована, задача в Inbox — проверь»

If unclear → use Inbox (no projectId).

---

## Client Labels

При создании задач связанных с оптовыми клиентами, добавляй label.

### Format
`client:{kebab-case-name}`

### Примеры
- client:wholesale-buyer
- client:reseller-panel

### Использование
```bash
mcp-cli call todoist add-tasks '{"tasks": [{"content": "Рефилл подписчиков для оптовика", "labels": ["client:wholesale-buyer", "urgent"]}]}'
```

### Фильтр в Todoist
`@client:wholesale-buyer` — все задачи по клиенту

---

## Anti-Patterns (НЕ СОЗДАВАТЬ)

Based on John's preferences:

- ❌ "Подумать о..." → конкретизируй действие
- ❌ "Разобраться с..." → что именно сделать?
- ❌ Абстрактные задачи без Next Action
- ❌ Дубликаты существующих задач
- ❌ Задачи без дат
- ❌ Инсайты и свободные идеи → они идут в vault (thoughts/), НЕ в Todoist (см. classification.md)
- ❌ Записи с тегами `#revisit`, `#new-domain` → это мысли, не задачи

---

## Error Handling

CRITICAL: Никогда не предлагай "добавить вручную".

If `add-tasks` fails:
1. Include EXACT error message in report
2. Continue with next entry
3. Don't mark as processed
4. User will see error and can debug

WRONG output:
  "Не удалось добавить (MCP недоступен). Добавь вручную: Task title"

CORRECT output:
  "Ошибка создания задачи: [exact error from MCP tool]"

---

## Recurring Tasks for Process Goals

When creating process commitments → use dueString with recurring pattern.

### Recurring Patterns

| Process Description | dueString |
|---------------------|-----------|
| каждое утро | every day |
| каждый день | every day |
| каждый рабочий день | every weekday |
| 3 раза в неделю | every monday, wednesday, friday |
| раз в неделю | every week |
| каждый понедельник | every monday |
| каждую пятницу | every friday |

### Example: Creating Process Goal Tasks

```bash
mcp-cli call todoist add-tasks '{"tasks": [
  {"content": "15 мин практика внимания", "dueString": "every day", "priority": 3, "labels": ["process-goal"]},
  {"content": "Проверка заказов FiveBBC (≤30 мин)", "dueString": "every day", "priority": 2, "labels": ["process-goal"]},
  {"content": "1 час: работа над книгой", "dueString": "every weekday", "priority": 3, "labels": ["process-goal"]}
]}'
```

### Label for Process Goals

Use label `process-goal` for recurring tasks created from Process Commitments.
This allows easy filtering and cleanup.

### When to Create Recurring

Create recurring tasks when:
- Generating weekly digest (new week planning)
- User explicitly asks for process goal setup
- Transforming outcome goal to process (if user confirms)

### Cleanup Stale Recurring

In weekly digest, check:
```bash
mcp-cli call todoist find-tasks '{"labels": ["process-goal"]}'
```
If task from previous week → warn user to complete or delete
