# Personal Projects
Проекты над которыми я работаю/работал вне Revolut. 

# ETH Trading Bot (TradingView → Lighter → SQLite → Telegram)

GitHub: https://github.com/umarovm/auto_lighter_bot (публичный)

Python/FastAPI-бэкенд, торгует ETH на perp и spot одновременно через два изолированных аккаунта биржи Lighter. В проде на VPS 1-3 месяца.

- Вебхуки TradingView → исполнение ордеров через Lighter API → запись сигналов/сделок в SQLite → уведомления и отчёты через два независимых Telegram-бота (маршрутизация по топикам)
- Полная изоляция состояния по аккаунту: отдельные credentials, circuit breaker, история сделок
- Риск-менеджмент: stop-loss + position sizing (50% от баланса), spot — только лонг без плеча
- Автоматизация на APScheduler: очистка логов, обновление кэша рынков, месячный CSV-отчёт
- Продакшн-хардening: constant-time проверка webhook-секрета, rate limiting, параметризованные SQL-запросы, деплой через systemd + nginx
- Тесты: pytest + smoke-тесты подключения к бирже
- Результат: депозит $400 → $500 (+25%) за 1-3 месяца на реальном капитале

Resume bullet: *Designed and deployed a production FastAPI trading system ingesting TradingView webhook signals to execute automated crypto trades across two isolated exchange accounts (perp/spot) via the Lighter API, with built-in risk management, Telegram-based monitoring, and production security hardening (rate limiting, constant-time auth, parameterized queries) — grew live capital 25% over 1-3 months.*

# xstocks-bot (TradingView → Jupiter Swap API → tokenized stocks on Solana → Telegram)

GitHub: https://github.com/umarovm/automated_xstocks (публичный)

Node.js/TypeScript-бэкенд, торгует токенизированными акциями (xStocks) на Solana через Jupiter Swap API v2. В проде <1 месяца, на реальном капитале — уже торгует и зарабатывает; основное ограничение — прайс-импакт из-за низкой ликвидности (Meta ~1.37%).

- Fastify webhook-сервер, поддержка нескольких кошельков ("аккаунтов"), диспетчер маршрутизирует каждый алерт на один свободный аккаунт (не broadcast)
- Стейт-машина на позицию: IDLE → OPEN(TICKER) через BUY, докупка через DIP (до 3 раз), полный выход через SELL; состояние меняется только после подтверждения свопа on-chain
- Риск-параметры: 50% USDC на BUY, 10% на каждый DIP, лимит price impact, dust guard на минимальный размер свопа, dry-run режим для тестирования без реальных свопов
- `better-sqlite3` — учёт позиций/сделок/PnL истории, месячные CSV-отчёты
- Продакшн-хардening: приватные ключи только в `.env` (chmod 600, не логируются и не уходят в Telegram), timing-safe проверка webhook-секрета, HTTPS обязателен
- Деплой: VPS, systemd + Caddy (авто-HTTPS)
- Тесты: vitest suite (без сети), отдельные скрипты для верификации токен-маппинга и ручного smoke-теста свопа

Resume bullet: *Built a TypeScript/Node.js trading system executing tokenized-equity trades on Solana via the Jupiter Swap API, driven by TradingView webhook signals across multiple wallet accounts with independent state machines, on-chain-confirmed position tracking, and configurable risk controls (position sizing, price-impact limits, dry-run mode).*

# Job Search Automation Bot (Telegram → Claude API → RenderCV → Notion)

GitHub: https://github.com/umarovm/job_application_automation_bot (публичный)

Python-бот, автоматизирующий отклики на вакансии: анализ JD против базового CV (Claude Haiku — match %, сильные стороны, пробелы, вердикт), генерация cover letter и адаптированного CV (Claude Sonnet), ATS-friendly PDF через RenderCV/Typst, трекинг откликов в Notion, автоматические follow-up напоминания через APScheduler (14 дней без движения).

- Model cascading: Haiku на быстрый/дешёвый анализ, Sonnet на качественную генерацию
- Prompt caching на базовом CV-контексте — резкое снижение стоимости токенов
- Data funneling: компактный JobSnapshot вместо полного JD во второй запрос → ~80% экономии токенов
- Tweak-цикл: регенерация документов по инструкции («сделай тон агрессивнее, подчеркни Python»)
- Безопасность: бот ограничен одним Telegram user ID
- Практическое назначение: рабочий инструмент для спринта откликов (ноябрь 2026+)

**Ключевая ценность для CV/интервью:** это LLM-операции в чистом виде — оптимизация стоимости/качества пайплайна (каскадирование, кэширование, фаннелинг). Самый релевантный проект для AI Operations ролей — сильнее трейдинг-ботов.

Resume bullet: *Built an LLM-powered job application automation system (Python, Telegram) using model cascading (Claude Haiku → Sonnet), prompt caching, and structured data funneling to cut token costs by ~80%, with automated ATS-friendly PDF generation (RenderCV/Typst) and Notion-based pipeline tracking with scheduled follow-up reminders.*

# Telegram Voice Agent Bot (Whisper API)

GitHub: https://github.com/umarovm/tg_voice_bot (публичный)

Мультипользовательский Telegram-бот на Python, транскрибирует голосовые/аудио через OpenAI Whisper API.

- Каждый пользователь — свой OpenAI API key, запросы разных пользователей обрабатываются параллельно (asyncio, отдельная очередь на юзера)
- Автосплит файлов >25 МБ на чанки, склейка результата
- Non-blocking архитектура: AsyncOpenAI + executor для pydub
- Allowlist по Telegram ID, секреты вне репозитория (.env, users.json в .gitignore)

Resume bullet: *Built a multi-user Telegram bot (Python) transcribing voice/audio via the OpenAI Whisper API, with per-user API keys, parallel async request handling, and automatic chunking for files exceeding API size limits.*

---

# DataCamp Data Engineer Associate — учебные проекты (SQL/Python)

Ниже — 4 репозитория с сертификационного трека DataCamp Data Engineer Associate. Это учебные/экзаменационные кейсы (заданный датасет, заданные вопросы), а не самостоятельно спроектированные системы — по весу для CV/резюме они ощутимо ниже трейдинг-ботов и Job Search бота. Ценность: подтверждают руки в SQL и pandas-пайплайнах (закрывает пробел, выявленный на Asana-интервью), но не стоит презентовать их как "built a system" наравне с ботами.

**SQL London Transport Analysis**
GitHub: https://github.com/umarovm/sql-london-transport-analysis (публичный)
SQL-запросы (агрегация, фильтрация, сортировка) по датасету поездок TfL — самые популярные виды транспорта, сезонность Emirates Airline (канатная дорога), года с минимальным использованием метро/DLR.

**Bank Marketing Campaign Data Cleaning**
GitHub: https://github.com/umarovm/cleaning_bank_marketing_campaign_data (публичный)
Pandas/Jupyter: чистка и разбор сырого CSV банковской маркетинговой кампании в три нормализованные таблицы (client/campaign/economics), готовые к загрузке в PostgreSQL.

**Walmart Retail Data Pipeline**
GitHub: https://github.com/umarovm/building_retail_data_pipeline (публичный)
Pandas: merge данных о продажах (PostgreSQL-таблица + parquet), трансформация и агрегация по месяцам для анализа спроса вокруг праздников.

**Data Engineer Associate Exam — Virtual Reality Fitness**
GitHub: https://github.com/umarovm/data-engineer-associate-exam-virtual-reality-fitness (публичный)
Итоговый экзаменационный кейс сертификации: SQL-запросы к многотабличной схеме (users/devices/games/events) для очистки и подготовки данных к отчётности перед промо-кампанией.

