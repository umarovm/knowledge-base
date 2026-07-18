---
date: 2026-07-16
project: projects/hermes
tags: [bot, инструменты]
status: processed
related:
  - "[[projects/hermes/2026-07-16-hermes-agent]]"
summary: "OmniRoute — verified: self-hosted AI-gateway (16k★, MIT), Subscription→API→Cheap→Free fallback. Предварительное условие для дешёвого Hermes agent, не самостоятельная задача сама по себе."
---

# Open router / OmniRoute — проверено (16.07.2026)

https://github.com/diegosouzapw/OmniRoute

Не сомнительный скрипт, а зрелый проект: 16k+ звёзд, MIT license, 21000+ тестов, активно поддерживается. Поднимает локальный OpenAI-совместимый endpoint (`localhost:20128/v1`) с 4-уровневым fallback: Subscription → API → Cheap → Free — то есть сначала использует уже оплаченную подписку (Claude Code/Codex), потом дешёвые модели, и только потом бесплатные провайдеры.

Похожие репозитории (не проверены детально, OmniRoute выбран как основной кандидат):
- github.com/tashfeenahmed/freellmapi
- https://github.com/ojuschugh1/sqz

## Статус и назначение

Счёт за API сейчас не поджимает — ценность не в текущей экономии, а в том, что это условие для запуска Hermes agent почти бесплатно (см. [[projects/hermes/2026-07-16-hermes-agent]]). Без реального проекта с объёмным потреблением токенов сам по себе OmniRoute не нужен.

Следующий шаг: поднять на VPS перед настройкой Hermes.
