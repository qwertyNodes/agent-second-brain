# Entry Classification

## Work Domains → Categories

Based on John's work context (see [about.md](about.md)):

### FiveBBC Operations
Заказы, рефиллы, дропы, клиенты, услуги, каталог, поддержка

**Keywords:** FiveBBC, панель, SMM, услуга, каталог, заказ, рефилл, дроп, клиент, оптовик, Стас, Дима, поддержка, тикет

**→ Category:** task (p1-p3) → Todoist

### SEO & Content Marketing
Аудит, ключевые слова, статьи, money pages, DataForSEO, трафик

**Keywords:** SEO, аудит, SERP, ключевое слово, КС, DataForSEO, статья, money page, контент, трафик, органика, Article Writer, пайплайн

**→ Category:** task или project → Todoist / thoughts/

### AI & Tech
Агенты, Claude Code, MCP, пайплайны, автоматизация, инструменты

**Keywords:** Claude, агент, MCP, пайплайн, скилл, автоматизация, API, интеграция, бот, Second Brain

**→ Category:** learning или project → thoughts/

### Crypto & R&D
Арбитраж, боты, биржи, DEX, Web3 — ТОЛЬКО после автоматизации SMM

**Keywords:** крипто, арбитраж, биржа, DEX, CEX, Web3, стейкинг, бот-трейдер

**→ Category:** idea или project → thoughts/ (p4, не срочно)

### Book «Проснись!»
Книга, исходники, инвентаризация, структура томов, черновик

**Keywords:** книга, Проснись, том, глава, исходник, инвентаризация, сознание, внимание, тень, медитация, практика

**→ Category:** task (p3) или reflection → Todoist / thoughts/

### Infrastructure
Сервер, Docker, SSH, VPS, деплой, DNS, домен

**Keywords:** VPS, Contabo, Docker, SSH, сервер, деплой, DNS, nginx, домен, SSL

**→ Category:** task (p2-p3) → Todoist

### Personal Growth
Осознанность, практика, рефлексия, тень, инсайты

**Keywords:** понял, осознал, заметил, практика, внимание, тень, рефлексия, медитация, энергия, сон

**→ Category:** reflection → thoughts/reflections/

### Свободные инсайты и идеи
Инсайты и идеи на любую тему, не привязанные к конкретному домену.

**Keywords (инсайты):** инсайт, осенило, понял что, заметил что, интересно что, связь между
**Keywords (идеи):** идея, а что если, можно было бы, было бы круто, стоит попробовать, задумка

**Инсайт / наблюдение → Category:** reflection → thoughts/reflections/
**Идея / задумка → Category:** idea → thoughts/ideas/

При неясности домена → классифицируй в ближайший по смыслу. Если ни один не подходит → `domain: Personal Growth`.

---

## Decision Tree

```
Entry text contains...
│
├─ Клиент/заказ/рефилл/дроп? ───────────────────> TASK (p1-p2)
│  (клиент, оптовик, рефилл, заказ, дроп, Стас, Дима)
│
├─ Операционное/срочное? ────────────────────────> TASK (p2-p3)
│  (нужно сделать, не забыть, проверить, добавить услугу)
│
├─ SEO/контент с дедлайном? ─────────────────────> TASK (p2-p3)
│  (статья, money page, аудит, опубликовать)
│
├─ SEO/контент без дедлайна? ────────────────────> PROJECT
│  (стратегия контента, план статей, исследование КС)
│
├─ AI/tech обучение? ────────────────────────────> LEARNING
│  (узнал, модель, агент, интеграция, Claude Code)
│
├─ Крипто/R&D идея? ────────────────────────────> IDEA (p4)
│  (арбитраж, бот, биржа, Web3)
│
├─ Книга — конкретное действие? ─────────────────> TASK (p3)
│  (написать главу, инвентаризация, структура тома)
│
├─ Книга — мысль/инсайт? ───────────────────────> REFLECTION
│  (идея для книги, тезис, наблюдение)
│
├─ Стратегическое мышление? ─────────────────────> PROJECT
│  (стратегия, план, долгосрочно, масштабирование)
│
├─ Личный инсайт/осознание? ────────────────────> REFLECTION
│  (понял, осознал, заметил, практика)
│
├─ Инсайт на любую тему? ───────────────────────> REFLECTION
│  (осенило, связь между, интересно что)
│
├─ Идея на любую тему? ─────────────────────────> IDEA
│  (идея, можно было бы, было бы круто, задумка)
│
├─ Контент-идея для соцсетей? ──────────────────> IDEA
│  (пост, тезис, контент)
│
└─ Не подходит ни один домен? ──────────────────> Ближайший по смыслу
   (domain: Personal Growth, если совсем неясно)
```

---

## Business Context Detection

Entry mentions FiveBBC operations?

```
├─ + клиент ждёт / срочно? → TASK (p1-p2) + label
├─ + статус ("рефилл сделан", "услуга добавлена")? → TASK + done
├─ + Стас/Дима? → TASK + assign context
└─ просто упоминание? → Add context only
```

### Operations Status Keywords

| Keywords | Интерпретация |
|----------|---------------|
| "рефилл сделан", "услуга добавлена", "заказ выполнен" | Позитивный исход |
| "дроп", "жалоба", "не работает" | Требует внимания |
| "тестируем", "добавляем", "настраиваем" | В процессе |
| "ждём провайдера", "на стороне API" | Ожидание |

---

## Apply Decision Filters

Перед сохранением спроси:
- Это масштабируется?
- Это можно автоматизировать?
- Это усиливает SEO или трафик FiveBBC?
- Это приближает к пассивному доходу ($100K/мес цель)?

Если да на 2+ вопроса → повысить приоритет.

---

## Photo Entries

For `[photo]` entries:

1. Analyze image content via vision
2. Determine domain:
   - Скриншот панели / заказа → FiveBBC Operations
   - Схема / диаграмма → AI & Tech или SEO
   - Текст / статья → Learning
   - Скриншот биржи / графика → Crypto & R&D
3. Add description to daily file

---

## Output Locations

| Category | Destination | Priority |
|----------|-------------|----------|
| task (клиент/операции) | Todoist | p1-p2 |
| task (SEO/контент) | Todoist | p2-p3 |
| task (книга) | Todoist | p3 |
| task (инфраструктура) | Todoist | p2-p3 |
| idea | thoughts/ideas/ | — |
| reflection | thoughts/reflections/ | — |
| project | thoughts/projects/ | — |
| learning | thoughts/learnings/ | — |

---

## File Naming

```
thoughts/{category}/{YYYY-MM-DD}-short-title.md
```

Examples:
```
thoughts/ideas/2026-03-01-crypto-arbitrage-bot.md
thoughts/ideas/2026-03-01-app-for-lucid-dreaming.md
thoughts/reflections/2026-03-01-attention-and-gravity-connection.md
thoughts/reflections/2026-03-01-why-people-resist-change.md
thoughts/projects/2026-03-01-seo-audit-phase2.md
thoughts/learnings/2026-03-01-claude-code-agents.md
thoughts/reflections/2026-03-01-morning-practice-shift.md
```

---

## Thought Structure

Use preferred format:

```markdown
---
date: {YYYY-MM-DD}
type: {category}
domain: {FiveBBC Ops|SEO & Content|AI & Tech|Crypto & R&D|Book|Infrastructure|Personal Growth}
description: >-
  Retrieval filter ~150 символов — добавляет контекст СВЕРХ заголовка
tags: [tag1, tag2]
source: daily/{YYYY-MM-DD}.md
related: []
---

## Context
[Что привело к мысли]

## Insight
[Ключевая идея]

## Implication
[Что это значит для FiveBBC / книги / стратегии дохода / жизни в целом]

## Next Action
[Конкретный шаг — или «нет, сохранить для позднего возврата»]
```

> Для свободных инсайтов и идей допустимо: Next Action = «нет, сохранить для позднего возврата». Не нужно искусственно привязывать к текущим проектам.

---

## Anti-Patterns (ИЗБЕГАТЬ)

При создании мыслей НЕ делать:
- Абстрактные рассуждения без Next Action
- Теория без применения к FiveBBC / книге / доходу
- Повторы без синтеза (кластеризуй похожие!)
- Хаотичные списки без приоритетов
- Задачи типа "подумать о..." (конкретизируй!)
- Крипто-задачи с высоким приоритетом (Фаза 2, не сейчас!)
- Ответ «не могу классифицировать» — всегда выбирай ближайший домен

---

## MOC Updates

After creating thought file, add link to:
```
MOC/MOC-{category}s.md
```

Group by domain when relevant:
```markdown
## SEO & Content
- [[2026-03-01-seo-audit-phase2]] - Фаза 2 аудита

## AI & Tech
- [[2026-03-01-claude-code-agents]] - Агентная система

## Crypto & R&D
- [[2026-03-01-crypto-arbitrage-bot]] - Арбитражный бот (Фаза 2)

## Book & Personal Growth
- [[2026-03-01-morning-practice-shift]] - Сдвиг в утренней практике
- [[2026-03-01-attention-and-gravity-connection]] - Связь внимания и гравитации
```
