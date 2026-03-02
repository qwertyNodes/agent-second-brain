# Архитектура памяти Agent Second Brain

> Как работает агент — просто и наглядно. Документация для разработки.

---

## Что такое этот проект?

**Agent Second Brain** — персональный AI-агент для управления знаниями и задачами:

1. Принимает голосовые/текстовые заметки через Telegram
2. Автоматически классифицирует их и создаёт задачи в Todoist
3. Сохраняет знания в Obsidian-хранилище (vault/)
4. Генерирует HTML-отчёт и отправляет обратно в Telegram

---

## Главная схема

```
Ты говоришь в Telegram
        │
        ▼
Deepgram транскрибирует голос
        │
        ▼
Claude Code запускает 3-фазный pipeline
        │
   ┌────┴────────────────────────────────────┐
   │                                         │
[CAPTURE]          [EXECUTE]             [REFLECT]
   │                   │                     │
Читает daily.md    Создаёт задачи       Генерирует отчёт
Классифицирует  →  в Todoist        →   Обновляет MEMORY.md
записи             Сохраняет идеи       Передаёт контекст
                   Обновляет CRM
   │                   │                     │
   └─────── capture.json ─── execute.json ───┘
                                             │
                                      HTML → Telegram
```

---

## Структура хранилища (vault/)

```
vault/
├── MEMORY.md              ← горячая память (загружается ВСЕГДА, < 4KB)
├── daily/                 ← YYYY-MM-DD.md, сырые записи (эпизодическая память)
├── thoughts/
│   ├── ideas/             ← идеи
│   ├── learnings/         ← знания и выводы
│   ├── reflections/       ← рефлексии
│   └── projects/          ← проектные мысли
├── goals/
│   ├── 0-vision-3y.md     ← 3-летнее видение
│   ├── 1-yearly-YYYY.md   ← годовые цели
│   ├── 2-monthly.md       ← месячные приоритеты
│   └── 3-weekly.md        ← ONE Big Thing этой недели
├── business/
│   ├── _index.md          ← входная точка, статистика
│   └── crm/               ← карточки клиентов
├── MOC/                   ← Maps of Content (индексы)
├── templates/             ← шаблоны файлов
└── .claude/
    ├── CLAUDE.md          ← инструкции для агента
    ├── skills/            ← навыки (agent-memory, dbrain-processor...)
    ├── agents/            ← агенты (weekly-digest, goal-aligner...)
    └── rules/             ← правила форматирования
```

---

## Система памяти: три слоя

```
┌──────────────────────────────────────────────────────┐
│  СЛОЙ 1 — ГОРЯЧИЙ (< 4 KB, загружается ВСЕГДА)      │
│  vault/MEMORY.md                                     │
│  • Ключевые бизнес-решения                          │
│  • Текущие приоритеты                               │
│  • Паттерны и предпочтения агента                   │
└──────────────────────────────────────────────────────┘
                         │
                         ▼ (поиск по мере необходимости)
┌──────────────────────────────────────────────────────┐
│  СЛОЙ 2 — ХРАНИЛИЩЕ (тысячи файлов, тирированный)   │
│  Каждый файл: YAML-метаданные с relevance + tier     │
│                                                      │
│  daily/          ← эпизодическая память             │
│  thoughts/       ← знания и идеи                    │
│  business/crm/   ← контакты                         │
│  goals/          ← цели                             │
└──────────────────────────────────────────────────────┘
                         │
                         ▼ (старые данные)
┌──────────────────────────────────────────────────────┐
│  СЛОЙ 3 — АРХИВ (.archive/)                          │
│  Завершённые задачи, старые отчёты                  │
└──────────────────────────────────────────────────────┘
```

---

## Механизм забывания (Ebbinghaus Decay)

Каждый файл имеет YAML-заголовок:

```yaml
---
relevance: 0.85      # насколько "живой" (0.0 - 1.0)
tier: active         # уровень доступности
last_accessed: 2026-02-28
---
```

### Пять уровней (тиров)

```
CORE    ─── вечный (цены, идентичность, безопасность)
            Никогда не деградирует. Только вручную.

ACTIVE  ─── 0-7 дней  │ relevance: 0.9 - 1.0
            В каждом поиске агента

WARM    ─── 8-21 день  │ relevance: 0.6 - 0.9
            В обычном поиске

COLD    ─── 22-60 дней │ relevance: 0.2 - 0.6
            Только при глубоком поиске

ARCHIVE ─── 60+ дней   │ relevance: 0.1 - 0.2
            Только в creative режиме (случайная выборка)
```

### Формула релевантности

```
relevance = 1.0 - (дней_без_доступа × 0.015)
минимум:  0.1   ← файл никогда не исчезает
```

**Примеры:**
- 10 дней → `1.0 - 0.15 = 0.85` → WARM
- 30 дней → `1.0 - 0.45 = 0.55` → COLD
- 70 дней → `1.0 - 1.05 = 0.10` → ARCHIVE

### Конфигурация (.memory-config.json)

```json
{
  "tiers": {"active": 7, "warm": 21, "cold": 60},
  "decay_rate": 0.015,
  "relevance_floor": 0.1,
  "use_git_dates": true,
  "skip_patterns": ["_index.md"]
}
```

### Команды memory-engine.py

```bash
python vault/.claude/skills/agent-memory/scripts/memory-engine.py decay
# Пересчитать все тиры (запускать ежедневно через cron)

python vault/.claude/skills/agent-memory/scripts/memory-engine.py touch <file>
# Файл прочитан → вернуть в ACTIVE (сбросить счётчик)

python vault/.claude/skills/agent-memory/scripts/memory-engine.py creative 5
# 5 случайных файлов из COLD/ARCHIVE (мозговой штурм)

python vault/.claude/skills/agent-memory/scripts/memory-engine.py stats
# Статистика: сколько файлов в каждом тире

python vault/.claude/skills/agent-memory/scripts/memory-engine.py scan
# Проверить покрытие YAML по всему vault
```

---

## Три фазы обработки

### Фаза 1: CAPTURE (vault/.claude/skills/dbrain-processor/phases/capture.md)

Читает `daily/YYYY-MM-DD.md`, классифицирует каждую запись.

**Классификация записей:**

| Класс | Куда | Ключевые слова |
|-------|------|----------------|
| `task` | Todoist | "нужно", "надо", "дедлайн", "позвонить" |
| `idea` | thoughts/ideas/ | "а что если", "можно было бы" |
| `learning` | thoughts/learnings/ | "узнал", "оказывается" |
| `reflection` | thoughts/reflections/ | "понял", "заметил" |
| `crm_update` | business/crm/ | упоминание клиента + статус |
| `skip` | нигде | уже обработано |

**Вывод:** `.session/capture.json`

---

### Фаза 2: EXECUTE (vault/.claude/skills/dbrain-processor/phases/execute.md)

Берёт `capture.json`, выполняет действия.

**Действия:**
1. Создать задачи в Todoist через `mcp-cli` (3 retry с нарастающей задержкой)
2. Сохранить thoughts в `thoughts/{category}/YYYY-MM-DD-slug.md` с frontmatter
3. Обновить CRM-карточки клиентов в `business/crm/`
4. Построить wiki-links между новыми и существующими файлами
5. Проверить загруженность (workload) на неделю

**Вывод:** `.session/execute.json`

---

### Фаза 3: REFLECT (vault/.claude/skills/dbrain-processor/phases/reflect.md)

Собирает всё → генерирует итог.

**Действия:**
1. Генерация HTML-отчёта → Telegram (только теги `<b>`, `<i>`, `<code>`, `<a>`)
2. Обновление `MEMORY.md` (только новые факты, без дублей)
3. Запись контекста в `vault/.session/handoff.md`
4. Лог в `daily/DATE.md`

**Вывод:** HTML-отчёт в Telegram

---

## Загрузка контекста при старте сессии

Агент загружает в строгом порядке:

```
1. vault/MEMORY.md              ← долгосрочная память (ВСЕГДА, < 4KB)
2. .memory-config.json          ← настройки decay
3. vault/daily/[сегодня].md     ← что происходит сегодня
4. vault/daily/[вчера].md       ← преемственность
5. vault/goals/3-weekly.md      ← ONE Big Thing недели
6. vault/.session/handoff.md    ← контекст прошлой сессии (если есть)
```

Остальные файлы загружаются **по запросу** через тирированный поиск.

---

## Поддержка здоровья хранилища

### Граф знаний (vault/.claude/skills/graph-builder/)

```bash
# Анализ структуры графа
python vault/.claude/skills/graph-builder/scripts/analyze.py

# Добавление wiki-links (--dry-run для preview)
python vault/.claude/skills/graph-builder/scripts/add_links.py --dry-run
python vault/.claude/skills/graph-builder/scripts/add_links.py --apply
```

### Оценка здоровья (vault/.claude/skills/vault-health/)

```
Health Score = 100
  - 30 × (доля сирот)           ← файл без связей = знания теряются
  - 30 × (доля битых ссылок)    ← фрагментация
  - 15 × (если < 3 ссылок/файл) ← цель: 3+ связи
  - 10 × (нет description)       ← 50%+ файлов должны иметь описание

Цели: Score > 80, сироты < 30, битых ссылок < 50
```

```bash
# Починить битые ссылки
python vault/.claude/skills/vault-health/scripts/fix_links.py

# Сгенерировать MOC-индексы
python vault/.claude/skills/vault-health/scripts/generate_moc.py

# Добавить descriptions к файлам без них
python vault/.claude/skills/vault-health/scripts/add_descriptions.py

# Подключить сироты к хабам
python vault/.claude/skills/vault-health/scripts/connect_orphans.py
```

---

## Четыре агента

| Агент | Когда | Что делает |
|-------|-------|------------|
| `weekly-digest` | Каждое воскресенье | Анализ недели, план следующей |
| `goal-aligner` | Еженедельно | Проверка соответствия задач целям |
| `inbox-processor` | `/inbox` команда | GTD-обработка непрочитанных записей |
| `note-organizer` | `/organize` команда | Связывание "сирот", правка frontmatter |

---

## Интеграции

| Сервис | Роль | Метод |
|--------|------|-------|
| Telegram | Ввод и вывод | Bot API (src/) |
| Todoist | Задачи | MCP через mcp-cli |
| Obsidian | Хранилище (vault/) | Прямые файлы .md |
| Deepgram | Транскрипция голоса | API (src/) |
| Claude API | Мозг (Opus 4.6) | Claude Code CLI |

---

## Ключевые принципы

**1. Забывание — это фича**
Важное остаётся горячим (ACTIVE), неиспользуемое уходит в ARCHIVE — но не исчезает. Creative mode случайно поднимает забытые идеи.

**2. Одна фаза — один контекст**
CAPTURE → EXECUTE → REFLECT — каждый шаг отдельный вызов Claude. Нет смешения контекста между этапами.

**3. Один факт — одно место**
CRM-карта клиента: один файл, все остальные ссылаются через wiki-link. Нет дублирования данных.

**4. Процессные задачи**
- Правильно: "Отправить follow-up клиенту X"
- Неправильно: "Закрыть сделку с клиентом X"

**5. Самообслуживание**
Health score, MOC, decay, граф — работает автоматически.

---

## Файлы, важные для понимания

```
vault/.claude/CLAUDE.md                          ← инструкции агента
vault/.claude/skills/agent-memory/SKILL.md       ← система памяти
vault/.claude/skills/agent-memory/scripts/memory-engine.py
vault/.claude/skills/dbrain-processor/SKILL.md   ← pipeline
vault/.claude/skills/dbrain-processor/phases/    ← capture / execute / reflect
vault/.claude/skills/graph-builder/SKILL.md      ← граф знаний
vault/.claude/skills/vault-health/SKILL.md       ← здоровье vault
.memory-config.json                              ← конфиг decay
vault/MEMORY.md                                  ← текущая горячая память
```
