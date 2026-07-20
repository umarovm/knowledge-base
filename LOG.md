---
type: log
summary: "Append-only журнал операций над базой: одна строка на разбор inbox, weekly review, фиксацию сессии. Читать через tail, целиком не перечитывать."
---

# LOG — журнал операций над базой

Формат строки: `- [YYYY-MM-DD] тип | итог одной фразой`.
Типы: `ingest` (разбор inbox) · `review` (разбор проекта) · `session` (фиксация решений из сессии) · `fix` (правки структуры/скриптов/CLAUDE.md).
Новые строки — в конец. Последние события: `tail -5 LOG.md`.

## Лог

- [2026-07-19] review | Разобраны finance, ideas, projects, work, job-search (итоги — в логе WEEKLY_REVIEW.md).
- [2026-07-20] fix | Внедрены идеи из LLM Wiki (Karpathy): создан LOG.md, семантический lint в WEEKLY_REVIEW, проверка противоречий при разборе inbox, поле origin для выводов Claude.
- [2026-07-20] inbox | Разобрана 1 заметка (автоматизация разработки с AI-агентами) → разморозка projects/hermes, слита в лог SETUP.md, отдельная заметка не создана.
- [2026-07-20] session | Hermes: выбор фреймворка (Hermes vs OpenClaw), механика ролей и моделей (Codex OAuth/DeepSeek/free-каскад Kimi K2), дизайн кодинг-лупа (loop engineering), SETUP.md переписан начисто с исправлением порядка фаз.
- [2026-07-21] session | Hermes: архитектура пересмотрена на Main (основа агента, free-каскад, обрабатывает всё по умолчанию) + coding-project (изолированный платный контур: orchestration+goal_judge/review/skills-агент — GPT-5.6 Sol через Codex OAuth, coding — Kimi Code→GPT-5.6 Terra→Sol, DeepSeek V4 понижен до фолбэка). MiMoCode добавлен в free-каскад, Kiro/Chipotle Pepper AI/The Old LLM не подключаем (ToS/нестабильность). SETUP.md обновлён (роли, config.yaml, лог).
