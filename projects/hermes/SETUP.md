---
type: living
project: projects/hermes
tags: [bot, deploy, инструменты]
status: processed
related:
  - "[[projects/hermes/2026-07-16-hermes-agent]]"
  - "[[projects/hermes/2026-07-16-omnirouter-llm-api]]"
summary: "Living-файл проекта Hermes: детальная инструкция для первого раза (Mac → Hetzner VPS → Hermes → Telegram; OmniRoute — этапом Б) + текущий статус. Шапка = состояние, лог внизу."
---

# Hermes Agent — SETUP (шапка = текущее состояние)

**Статус:** фаза 0 — ничего не развёрнуто. Следующее действие: SSH-ключ на Mac + аренда VPS (шаги 1–2).

| Фаза | Что | Статус |
|---|---|---|
| 1 | SSH-ключ на Mac, VPS арендован, харднинг сделан | ☐ |
| 2 | Hermes установлен, DeepSeek напрямую, первый чат в CLI работает | ☐ |
| 3 | Telegram-гейтвей + allowlist + systemd (работает 24/7) | ☐ |
| 4 | Задача 1: скан вакансий (2 недели обкатки) | ☐ |
| 5 | OmniRoute поверх (fallback + free-тиры) — только когда всё стабильно | ☐ |
| 6 | Задача 2: отчёт о расходах | ☐ |
| 7 | Задача 3: фриланс-воронка + UZ-networking + маппинг узбекских компаний/вилок/позиций | ☐ |

**Ключевые решения:**
- Новый отдельный VPS — на текущем боты с секретами (ключи кошельков), Hermes к ним не подпускаем.
- Claude Pro в Hermes НЕ используется. Основной мозг — DeepSeek V4 **через OpenRouter** (один аккаунт на все модели; OpenRouter — нативный провайдер Hermes). Обязательно зафиксировать провайдера DeepSeek в настройках OpenRouter (см. 4.1), иначе лотерея квантизаций ломает tool-calling.
- OmniRoute — НЕ на старте, а этапом Б. Правило из доков Hermes: «не добавляй routing/fallback, пока базовый чат не работает стабильно».
- Hermes не имеет доступа к knowledge-base (16.07). Business ideas research вычеркнут (17.07). Задачи — по одной.

---

## 0. Как ты будешь со всем этим работать (главное, прочитай первым)

VPS — это просто удалённый Linux-компьютер без экрана. Ты подключаешься к нему из **Terminal.app на Mac по SSH** — но только для установки и обслуживания. Повседневное общение с Hermes идёт **через Telegram с телефона/Mac**, как с обычным ботом. Терминал после настройки будешь открывать раз в пару недель.

Три интерфейса, каждый для своего:

| Что | Как открыть | Когда используешь |
|---|---|---|
| Терминал VPS | `ssh hermes@IP` из Terminal.app | Установка, обновления, логи. Редко |
| Hermes CLI/TUI | внутри SSH: команда `hermes --tui` | Настройка и отладка агента. Первая неделя |
| **Telegram-бот** | обычный чат в Telegram | **Вся повседневная работа. Основной способ** |
| Дашборд OmniRoute (этап Б) | браузер на Mac через SSH-туннель (ниже) | Настройка провайдеров, статистика расходов |

Веб-интерфейсы на VPS (дашборд OmniRoute) наружу в интернет не открываем — вместо этого **SSH-туннель**: команда на Mac пробрасывает порт VPS на твой localhost, и ты открываешь его в Safari/Chrome как будто он локальный. Пример ниже в шаге про OmniRoute.

## 1. Подготовка на Mac: SSH-ключ (5 минут)

SSH-ключ = пара файлов: приватный (остаётся на Mac, никому не показывать) + публичный (кладётся на сервер). Вход по ключу вместо пароля — стандарт.

```bash
# В Terminal.app на Mac. Если ключ уже есть (ls ~/.ssh/*.pub что-то показывает) — пропусти.
ssh-keygen -t ed25519 -C "mvoramu@gmail.com"
# Enter на все вопросы (путь по умолчанию, passphrase можно пустую)

cat ~/.ssh/id_ed25519.pub   # ← это публичный ключ, скопируй вывод целиком
```

## 2. Аренда VPS: Hetzner Cloud (~15 минут)

Требования Hermes: 2 GB RAM / ~1 GB диска. Берём 4 GB — с запасом под Docker-песочницу и OmniRoute.

1. Регистрация: https://console.hetzner.com (потребуют карту или PayPal, спишут €0 для верификации).
2. **New Project** → назови `hermes`.
3. **Add Server**:
   - Location: **Falkenstein** или **Nuremberg** (до Варшавы ~20 мс);
   - Image: **Ubuntu 24.04**;
   - Type: **Shared vCPU → CX22** (2 vCPU / 4 GB / 40 GB, ~€4/мес);
   - SSH keys → **Add SSH key** → вставь публичный ключ из шага 1;
   - Остальное по умолчанию → **Create & Buy now**.
4. Через ~30 секунд сервер готов, скопируй его **IP-адрес** из консоли.

Проверка входа с Mac: `ssh root@IP` → на вопрос про fingerprint ответь `yes` → ты внутри (приглашение `root@...`). Выход — `exit`.

## 3. Харднинг сервера (~20 минут, один раз)

Всё выполняется в SSH-сессии под root. Копируй блоками.

```bash
# 3.1 Обновить систему
apt update && apt upgrade -y

# 3.2 Создать рабочего пользователя (под root не работаем)
adduser hermes            # придумай пароль, остальные вопросы — Enter
usermod -aG sudo hermes
mkdir -p /home/hermes/.ssh
cp ~/.ssh/authorized_keys /home/hermes/.ssh/   # твой ключ теперь работает и для hermes
chown -R hermes:hermes /home/hermes/.ssh && chmod 700 /home/hermes/.ssh

# 3.3 Запретить вход по паролю и под root
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh

# 3.4 Файрвол: наружу только SSH
apt install -y ufw fail2ban unattended-upgrades
ufw allow OpenSSH && ufw --force enable
dpkg-reconfigure -plow unattended-upgrades   # выбери Yes (автообновления безопасности)

# 3.5 Docker (песочница для команд Hermes)
curl -fsSL https://get.docker.com | sh
usermod -aG docker hermes

# 3.6 Зависимости для установщика Hermes
apt install -y git curl xz-utils
```

⚠️ **Прежде чем закрыть root-сессию**, проверь в новой вкладке Terminal, что `ssh hermes@IP` работает. Дальше всегда входи как `hermes@IP`.

## 4. Установка Hermes — этап А, без OmniRoute (~30 минут)

Философия из официального квикстарта: сначала один чистый работающий чат, только потом гейтвеи, cron и роутинг.

### 4.1 Ключ OpenRouter + фикс провайдера

https://openrouter.ai → **Keys** → создать ключ (`sk-or-...`) → пополнить баланс на $10 (заодно поднимает лимиты на `:free`-модели). Цены DeepSeek через OpenRouter: V4 Flash $0.09/$0.18, V4 Pro $0.435/$0.87 за 1M токенов (+~5% комиссия на пополнение).

⚠️ **Критично для агента:** по умолчанию OpenRouter раскидывает запросы к DeepSeek между десятками хостеров в разных квантизациях — у части из них нестабилен tool-calling, а на этом агентный цикл ломается. Поэтому в аккаунте OpenRouter: **Settings → провайдерские настройки** — ограничь DeepSeek-модели официальным провайдером DeepSeek (или внеси ненадёжных в Ignored Providers). Один раз, спасает недели странных глюков.

### 4.2 Установка

```bash
# на VPS под пользователем hermes
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser
source ~/.bashrc
hermes doctor    # всё зелёное = ок
```

`--skip-browser` — пропускаем браузерную автоматизацию (не нужна для наших задач, экономит место; включить можно потом).

### 4.3 Мастер настройки

```bash
hermes setup
```

Это интерактивный TUI-мастер (стрелки + Enter). Проходим так:

- Режим: **Full Setup** (не Nous Portal — это их платная подписка, не Blank Slate).
- Провайдер: **OpenRouter** → вставь ключ `sk-or-...`. Модель: `deepseek/deepseek-v4` (слаг сверь на openrouter.ai/deepseek; контекст ≥64K — V4 проходит).
- Terminal backend: **Docker** (изоляция: команды агента выполняются в контейнере, не на хосте).
- Messaging gateway: пока **пропусти** — подключим после проверки чата.
- Инструменты (web search и т.д.): включи **web search**, остальное по вкусу; всё меняется позже через `hermes tools`.

Секреты лягут в `~/.hermes/.env`, настройки — в `~/.hermes/config.yaml`.

### 4.4 Первый чат — проверка

```bash
hermes --tui
```

Проверь последовательно: (1) баннер показывает твою модель; (2) обычный вопрос — отвечает; (3) «What's my disk usage? Show top 5 directories» — агент запускает команду и показывает результат; (4) выйди и `hermes -c` — сессия возобновляется. Если что-то сломалось: `hermes doctor` → `hermes model` → снова чат. Пока это не работает — дальше не идти.

### 4.5 Дешёвая маршрутизация вспомогательных задач

Фоновые подзадачи (сжатие контекста, названия сессий) переводим на V4 Flash — он в ~5 раз дешевле. В `~/.hermes/config.yaml` (редактор: `nano ~/.hermes/config.yaml`, сохранить Ctrl+O, выйти Ctrl+X):

```yaml
model:
  provider: "openrouter"
  default: "deepseek/deepseek-v4"          # диалог, curator, goal_judge — качество
  auxiliary:
    compression:      { model: "deepseek/deepseek-v4-flash" }
    title_generation: { model: "deepseek/deepseek-v4-flash" }
    web_extract:      { model: "deepseek/deepseek-v4-flash" }
    kanban_decomposer: { model: "deepseek/deepseek-v4-flash" }
    # curator НЕ удешевляем: он курирует библиотеку навыков, ошибки дорогие
```

Точные имена моделей сверь со списком в `hermes model`.

## 5. Telegram + 24/7 (этап А, финал)

### 5.1 Гейтвей

```bash
hermes gateway setup
```

Выбери **Telegram** — даст ссылку на предконфигурированного бота, свой токен не нужен. Открой ссылку, нажми Start.

**Обязательно** ограничь доступ своим Telegram user ID (узнать: напиши боту @userinfobot). В `config.yaml` найди секцию telegram → `allowed_user_ids` (точное имя поля покажет `hermes config get`); проверь статус: `hermes gateway status`.

### 5.2 systemd — чтобы Hermes жил после закрытия терминала

Без этого Hermes умирает вместе с SSH-сессией. Создаём сервис:

```bash
sudo nano /etc/systemd/system/hermes.service
```

```ini
[Unit]
Description=Hermes Agent Gateway
After=network-online.target docker.service
Wants=network-online.target

[Service]
User=hermes
WorkingDirectory=/home/hermes
ExecStart=/home/hermes/.local/bin/hermes gateway
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

(если `hermes gateway` не команда запуска — сверь с `hermes gateway --help`, возможно `hermes gateway run`)

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes
systemctl status hermes          # active (running) = готово
journalctl -u hermes -f          # живые логи (Ctrl+C — выход)
```

**С этого момента терминал больше не нужен для общения** — пишешь боту в Telegram. Полезные команды в чате: `/help`, `/background <задача>`, `/goal`, `/model`.

### 5.3 Шпаргалка обслуживания (SSH, раз в 1–2 недели)

```bash
ssh hermes@IP
hermes update                 # обновить Hermes
sudo apt update && sudo apt upgrade -y
systemctl restart hermes      # после обновлений
journalctl -u hermes --since today   # что происходило
df -h / && free -h            # диск и память
```

## 6. Задача 1: скан вакансий (фаза 4)

Через Telegram, без терминала. Скажи боту создать cron-задачу: источники (tg-каналы/борды из job-search/), критерии раннего remote-теста, время дайджеста. Устройство: сбор постов — скрипт, LLM (V4 Flash) — только фильтрация собранного, дайджест — одно сообщение в день.

Правильный workflow создания (из гайда): надиктуй голосом, как ты сам ищешь и отсеиваешь вакансии (LLMWikiBot идеален) → отдай текст Hermes'у как основу скилла → добавь evals: 10 реальных постов с твоей разметкой релевантно/нет → гоняй тестово, правь руками → только потом в ежедневный cron. Две недели считай precision; следующая задача — после стабильности.

## 7. OmniRoute — этап Б (фаза 5, не раньше)

Зачем: free-тиры (Gemini, OpenRouter `:free` — суммарно ~1.6B бесплатных токенов/мес по всем провайдерам), auto-fallback при недоступности DeepSeek, дашборд расходов, сжатие токенов (RTK+Caveman, 15–95%).

```bash
# на VPS (Node.js уже стоит после установщика Hermes)
npm install -g omniroute
mkdir -p ~/.omniroute
nano ~/.omniroute/.env
```

```env
JWT_SECRET=длинная-случайная-строка      # сгенерируй: openssl rand -hex 32
INITIAL_PASSWORD=пароль-для-дашборда
PORT=20128
```

Запуск — команда `omniroute` (слушает только localhost). systemd-юнит по аналогии с hermes.service (`ExecStart=/usr/bin/env omniroute`, User=hermes).

**Дашборд с Mac через SSH-туннель:**

```bash
# на Mac; держи окно открытым, пока работаешь с дашбордом
ssh -L 20128:localhost:20128 hermes@IP
# теперь в браузере на Mac: http://localhost:20128/dashboard
```

В дашборде: добавь провайдеров (OpenRouter-ключ, Gemini API-ключ с ai.google.dev) → собери **combo** со стратегией `priority`: DeepSeek V4 (через OpenRouter) → Gemini Flash → `:free` модели (или используй готовый `auto/cheap`). Затем переключи Hermes:

```yaml
# ~/.hermes/config.yaml
model:
  provider: "custom"
  base_url: "http://localhost:20128/v1"
  api_key: "ключ-созданный-в-дашборде-omniroute"
  default: "auto/cheap"      # или имя твоего combo
```

`systemctl restart hermes` и проверь чат. Если что-то глючит — верни `provider: "openrouter"`, это твой стабильный откат.

⚠️ Free-модели — только нижний уровень fallback и вспомогательные задачи, НЕ основной мозг: на OpenRouter одна модель раздаётся ~20 провайдерами в разных квантизациях, tool-calling у них нестабилен, а агентный цикл на этом ломается.

## 8. Бюджет

| Статья | /мес |
|---|---|
| VPS Hetzner CX22 | ~€4 |
| OpenRouter: DeepSeek V4/Flash (задачи 1–3, aux на Flash) | ~$0.5–2 |
| **Итого** | **~€5–6** |

Порог тревоги: расход >$5/мес → смотреть Activity на openrouter.ai (или дашборд OmniRoute), какая задача жрёт.

## 9. Безопасность (чеклист)

- [ ] Отдельный VPS, никаких ключей кошельков/других ботов на нём
- [ ] Вход только по SSH-ключу, root-вход запрещён, ufw включен
- [ ] Telegram allowlist: только мой user ID
- [ ] terminal.backend = docker
- [ ] OmniRoute только на 127.0.0.1, доступ — SSH-туннель
- [ ] Баланс OpenRouter без автопополнения (top-up руками)
- [ ] Никакого доступа Hermes к knowledge-base и iCloud

## 10. Troubleshooting (типовые грабли новичка)

| Симптом | Причина → фикс |
|---|---|
| `hermes: command not found` | `source ~/.bashrc`; или PATH без `~/.local/bin` |
| Пустые/битые ответы в чате | провайдер/ключ → `hermes model` заново |
| Бот в Telegram молчит | `hermes gateway status`; `journalctl -u hermes -f`; allowlist? |
| После перезагрузки VPS всё умерло | `systemctl enable hermes` забыт |
| SSH-туннель «connection refused» | omniroute не запущен на VPS: `systemctl status omniroute` |
| Всё сломалось, непонятно где | по порядку: `hermes doctor` → `hermes model` → `hermes sessions list` → `hermes gateway status` |

Доки: https://hermes-agent.nousresearch.com/docs/ · видео-мастеркласс есть на странице Quickstart.

---

## Лог (append-only)

- 2026-07-17 — Проект создан (перенос из ideas/инструменты). Решения: новый VPS (изоляция секретов), без Claude Pro, business research вычеркнут, задачи по одной со скана вакансий.
- 2026-07-17 — Инструкция переписана детально для первого раза. Архитектурное изменение: этап А — без OmniRoute (меньше движущихся частей); OmniRoute перенесён в фазу 5. Добавлено: SSH-ключи с Mac, пошаговый Hetzner, харднинг, systemd, SSH-туннель для дашборда, troubleshooting.
- 2026-07-17 — Решение: DeepSeek идёт через OpenRouter (один аккаунт), а не через прямой DeepSeek API. Условие: зафиксировать официального провайдера DeepSeek в настройках OpenRouter (анти-квантизация).
- 2026-07-17 — Решение: маппинг узбекских компаний/вилок/позиций — не отдельная задача и не реванш вычеркнутого «business research» (16.07), а часть задачи 3 (фриланс-воронка + UZ-networking), фаза 7. Пересекается с job-search TODO «карта узбекского рынка с вилками» (август) — Hermes закрывает этот пункт, когда дойдёт очередь до фазы 7.
