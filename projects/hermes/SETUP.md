---
type: living
project: projects/hermes
tags: [bot, deploy, инструменты]
status: processed
related:
  - "[[projects/hermes/2026-07-16-hermes-agent]]"
  - "[[projects/hermes/2026-07-16-omnirouter-llm-api]]"
summary: "Living-файл проекта Hermes: полная инструкция установки (VPS → OmniRoute → Hermes → задачи по фазам) + текущий статус. Шапка = состояние, лог внизу."
---

# Hermes Agent — SETUP (шапка = текущее состояние)

**Статус:** фаза 0 — ничего не развёрнуто. Следующее действие: арендовать VPS (шаг 1).

| Фаза | Что | Статус |
|---|---|---|
| 1 | VPS арендован и захарднен | ☐ |
| 2 | OmniRoute поднят, провайдеры подключены, fallback работает | ☐ |
| 3 | Hermes установлен, Telegram-гейтвей, systemd | ☐ |
| 4 | Задача 1: скан вакансий (2 недели обкатки) | ☐ |
| 5 | Задача 2: отчёт о расходах | ☐ |
| 6 | Задача 3: фриланс-воронка + UZ-networking | ☐ |

**Ключевые решения:**
- Новый отдельный VPS — на текущем крутятся боты с секретами (приватные ключи кошельков), Hermes к ним не подпускаем.
- Подписка Claude Pro в Hermes НЕ используется — лимиты нужны для Cowork/Claude Code. Стек: DeepSeek API (основной мозг) + Gemini/OpenRouter free (вспомогательные задачи).
- Hermes не имеет доступа к knowledge-base (решение 16.07, см. заметку).
- Задачи внедряются по одной; business ideas research вычеркнут (решение 17.07).

---

## Архитектура

```
Telegram (только мой user ID)
        │
   Hermes agent (VPS, systemd, docker-backend)
        │  config.yaml: provider: custom → base_url
        ▼
   OmniRoute (localhost:20128/v1, self-hosted gateway)
        │  fallback: API → Cheap → Free
        ▼
   DeepSeek API ──► Gemini API (free tier) ──► OpenRouter (:free модели)
```

Память Hermes (MEMORY.md / USER.md) живёт на VPS, в KB не пишет.
В KB попадают только готовые артефакты (репорты), и только через меня вручную.

---

## Шаг 1. VPS (~€4–6/мес)

Требования Hermes: 2 GB RAM, ~1 GB диска. С запасом под OmniRoute + Docker-песочницу бери **4 GB RAM**.

**Рекомендация: Hetzner Cloud CX22** (2 vCPU / 4 GB / 40 GB NVMe, ~€4/мес с VAT), локация Falkenstein или Nuremberg — до Варшавы ~20 мс. Альтернативы: Netcup (дешевле, менее удобная панель), Contabo (больше ресурсов за те же деньги, но овербукинг). ОС: **Ubuntu 24.04 LTS**.

Базовый харднинг сразу после создания:

```bash
adduser hermes && usermod -aG sudo hermes        # не работать под root
# ssh-ключ вместо пароля; в /etc/ssh/sshd_config:
#   PasswordAuthentication no, PermitRootLogin no
sudo apt update && sudo apt install -y git curl xz-utils ufw fail2ban unattended-upgrades
sudo ufw allow OpenSSH && sudo ufw enable         # наружу порты не открываем:
                                                  # OmniRoute слушает только localhost,
                                                  # Telegram — исходящие соединения
sudo dpkg-reconfigure -plow unattended-upgrades
# Docker для песочницы Hermes:
curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker hermes
```

## Шаг 2. OmniRoute

Репозиторий: https://github.com/diegosouzapw/OmniRoute (MIT, 16k+★). Ставим в Docker:

```bash
docker run -d --name omniroute --restart unless-stopped \
  -p 127.0.0.1:20128:20128 -v ~/omniroute-data:/data \
  ghcr.io/diegosouzapw/omniroute:latest
```

(точный image/команду сверить с README — есть также npm-вариант `npx omniroute`).
Дашборд: `http://localhost:20128/dashboard` (с ноутбука — через ssh-туннель:
`ssh -L 20128:localhost:20128 hermes@vps`). Настройка провайдеров — в дашборде, YAML не нужен.

**Подключить провайдеры (мои аккаунты):**

| Уровень | Провайдер | Роль |
|---|---|---|
| API | DeepSeek API (platform.deepseek.com) | основной мозг: V4 / V4 Flash |
| Cheap | Gemini API — платный ключ не обязателен | gemini-flash на vision/web_extract |
| Free | Gemini free tier, OpenRouter `:free` модели | вспомогательные задачи, эксперименты |

Fallback-цепочка OmniRoute: **API → Cheap → Free** (subscription-уровень пропускаем — Claude Pro не подключаем; если когда-нибудь появится ChatGPT Plus + Codex CLI, его можно добавить верхним уровнем через OAuth).

**Почему free-модели НЕ основной мозг, а только fallback:** free-провайдеры на OpenRouter нестабильны в tool-calling (разные квантизации, роутинг между ~20 инстансами одной модели) — для агентного цикла это ломающий фактор. Цены DeepSeek (июль 2026): V4 Flash $0.09/$0.18 за 1M токенов, V4 Pro $0.435/$0.87 — при таких ценах «экономить» free-моделями на основном цикле бессмысленно. Free — для дешёвых вспомогательных задач и как аварийный нижний уровень.

## Шаг 3. Hermes

Доки: https://hermes-agent.nousresearch.com/docs/ · Репо: https://github.com/NousResearch/hermes-agent

```bash
# под пользователем hermes; браузерная автоматизация пока не нужна → --skip-browser
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser
source ~/.bashrc
hermes setup        # мастер: модель, терминал-бэкенд, гейтвей, инструменты
hermes doctor       # проверка
```

Ключевые настройки (`~/.hermes/config.yaml`):

```yaml
model:
  provider: "custom"
  base_url: "http://localhost:20128/v1"   # OmniRoute
  default: "deepseek-v4"                  # основной диалог + curator
  auxiliary:
    compression:      { model: "deepseek-v4-flash" }   # сжатие контекста
    title_generation: { model: ":free" }                # мусорная задача → free
    web_extract:      { model: "deepseek-v4-flash" }
    vision:           { model: "gemini-flash" }
    curator:          { model: "deepseek-v4" }          # НЕ экономить: курирует навыки
    kanban_decomposer: { model: "deepseek-v4-flash" }
    goal_judge:       { model: "deepseek-v4" }
```

Дальше:
- `hermes config set terminal.backend docker` — команды выполняются в песочнице, не на хосте.
- `hermes gateway setup` → Telegram (самый отполированный гейтвей, токен не нужен — даёт готовую ссылку на бота). Обязательно: **allowlist только моего user ID** в config.yaml.
- systemd-юнит, чтобы жил 24/7:

```ini
# /etc/systemd/system/hermes.service
[Unit]
Description=Hermes Agent
After=network-online.target docker.service
[Service]
User=hermes
ExecStart=/home/hermes/.local/bin/hermes gateway run
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
```

`sudo systemctl enable --now hermes` (имя команды запуска гейтвея сверить с `hermes --help`).

## Шаг 4. Задачи — по фазам, по одной за раз

**Фаза 1 (сразу): скан вакансий.** Cron-задача: скрипт собирает новые посты из источников (tg-каналы/борды по критериям из job-search/), LLM-фильтр по моим критериям раннего remote-теста, дайджест в Telegram раз в день. Сбор — чистый скрипт; LLM (V4 Flash) только на фильтрацию уже собранного. Обкатка 2 недели: считаю precision дайджеста (сколько постов реально релевантны).

**Фаза 2: расходы.** WalletApp → выгрузка → анализ → еженедельный репорт в Telegram. Готовый репорт руками кладу в `finance/`.

**Фаза 3: фриланс-воронка (20→10→5→3→1 до 1.10) + UZ-networking.** Живёт в памяти Hermes; еженедельный дайджест переношу в `job-search/APPLICATIONS.md`. Один хозяин данных — Hermes, KB хранит только снапшоты.

**Без LLM вообще (cron `-no-agent`, ноль токенов), когда-нибудь потом:** крипто-алерты по уровням цен, healthcheck моих ботов на другом VPS (curl + пуш при падении).

**Вычеркнуто:** business ideas research (см. заметку hermes-agent).

## Шаг 5. Skills — как оформлять задачи

Workflow из гайда (проверен практикой, не выдумка):

1. Записать голосом, как я сам делаю процесс от и до (через LLMWikiBot — идеально).
2. Отдать запись coding-агенту → черновик скилла.
3. Встроить evals — эталонные примеры правильного результата (для скана вакансий: 10 постов с ручной разметкой релевантно/нет).
4. Гонять в тесте, править скилл и evals руками.
5. Только стабильный скилл отдавать в 24/7.

Полезные встроенные команды: `/background` (фоновая задача), `/goal` (долгосрочная цель с проверкой goal_judge), `/kanban` (мультиагентная доска), cron + вебхуки. Самообучающийся цикл (memory/skill-триггеры + curator) включён по умолчанию — куратору оставить deepseek-v4.

## Бюджет

| Статья | €/мес |
|---|---|
| VPS Hetzner CX22 | ~4 |
| Токены: фазы 1–3 на V4/V4 Flash (aux на free) | ~1–2 |
| **Итого** | **~5–6** |

Оценка токенов: дайджест вакансий ~50–100k токенов/день на Flash ≈ $0.3–0.6/мес; недельные репорты — копейки. Порог тревоги: если счёт DeepSeek > $5/мес — смотреть, какая задача жрёт (дашборд OmniRoute показывает разбивку).

## Безопасность (чеклист)

- [ ] Отдельный VPS, никаких ключей от кошельков/других ботов на нём
- [ ] Telegram allowlist: только мой user ID
- [ ] terminal.backend = docker
- [ ] OmniRoute только на 127.0.0.1, наружу ничего кроме SSH
- [ ] API-ключи DeepSeek/Gemini/OpenRouter — с лимитами расходов в кабинетах
- [ ] Никакого доступа Hermes к knowledge-base и iCloud

---

## Лог (append-only)

- 2026-07-17 — Проект создан (перенос из ideas/инструменты). Решения: новый VPS (изоляция секретов), без Claude Pro (стек DeepSeek+Gemini+OpenRouter), business research вычеркнут, задачи по одной начиная со скана вакансий. Написана инструкция.
