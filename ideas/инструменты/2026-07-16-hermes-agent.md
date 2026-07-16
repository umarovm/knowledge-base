---
date: 2026-07-16
project: ideas/инструменты
tags: [инструменты]
status: processed
related:
  - "[[ideas/инструменты/2026-07-16-omnirouter-llm-api]]"
  - "[[job-search/2026-07-16-автоматизация-поиска-работы]]"
summary: "Hermes agent на VPS через OmniRoute (verified): руки для внешних задач (скан вакансий, тайм-практика OM-кейсов, трекинг фриланс-воронки/networking). Без доступа к knowledge-base — это остаётся отдельным контуром (second brain)."
---

# Hermes agent — utility разобран (16.07.2026)

https://teletype.in/@alphamokakke/hermes_agent_full_guide

## Техническая проверка (сделана)

Схема Hermes → OmniRoute рабочая, не гипотетическая:
- Hermes нативно поддерживает `provider: "custom", base_url: "..."` в config.yaml для основной и вспомогательных моделей; auth к основной модели — через OAuth к существующей сессии Claude Code/Codex.
- OmniRoute — зрелый self-hosted AI-gateway (16k+ звёзд, MIT, 21000+ тестов), поднимает OpenAI-совместимый endpoint с 4-уровневым fallback: Subscription → API → Cheap → Free.
- Стыковка: Hermes указывает на `localhost:20128/v1` от OmniRoute → трафик сначала жрёт уже оплаченную подписку, потом дешёвые модели, в конце — бесплатные провайдеры. Реально почти бесплатно при уже имеющейся подписке Claude Code/Codex.
- Cron-задачи в Hermes с флагом `-no-agent` вообще не трогают LLM — чистый скрипт + пуш в мессенджер, нулевой токен-косту.

## Принципиальное ограничение (решено 16.07.2026)

Hermes НЕ получает доступ к knowledge-base. KB — second brain, живёт отдельно и работается только через Claude/Cowork. Hermes — отдельный контур ("руки"): работает с внешним миром, у себя же и хранит свою рабочую память (MEMORY.md/USER.md или локальная БД на VPS), в KB ничего не читает и не пишет.

## Финальный список задач для Hermes

- **Скан вакансий** под критерии раннего remote-теста (см. job-search/) — ежедневный дайджест новых постов в Telegram.
- **Трекинг фриланс-воронки** (20→10→5→3→1 до 1 октября) и **UZ-networking контактов** — ведётся в собственной памяти Hermes, не в KB.
- Анализ моих расходов (pull from WalletApp -> Analyze -> Send report). Затем я готовый репорт добавляю в KB. 
- Business ideas research (online SaaS and online/offline product for Uzbekistan market)

## Следующий шаг

Сначала поднять OmniRoute на VPS (self-hosted gateway) — это разблокирует остальное. Затем настроить Hermes config.yaml на этот endpoint и включить первую задачу (скан вакансий — самая простая и самая приоритетная по PLAN.md трек 1).
