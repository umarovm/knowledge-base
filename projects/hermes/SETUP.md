---
type: living
project: projects/hermes
tags: [bot, deploy, инструменты, automation]
related:
  - "[[projects/hermes/2026-07-16-hermes-agent]]"
  - "[[projects/hermes/2026-07-16-omnirouter-llm-api]]"
summary: "Разморожен (20.07.2026), эксперимент: автоматизация кодинга личных ботов (wikibot, трейдинг-боты — отдельные репо) на изолированном VPS. Порядок установки: сначала OmniRoute (провайдеры, комбо), затем Hermes подключается к нему сразу, без промежуточного прямого OpenRouter. Мультиролевой луп: оркестратор — ChatGPT-подписка (Codex OAuth), coder/reviewer — DeepSeek V4, cleaner/чат — free-каскад (Kimi K2 и др.); стоп-условие /goal, лимит 2 fix-циклов, GitHub Actions — гейт перед мержем."
---

# Hermes Agent — SETUP (шапка = текущее состояние)

**Статус: разморожен, эксперимент (20.07.2026).** Причина разморозки: появилась задача, реально требующая агентного цикла (в отличие от трёх задач 17.07 — фиксированных пайплайнов): автоматизация кодинга личных ботов — агент читает таскборд, кодит, дебажит, пушит в GitHub; GitHub Actions проверяет PR перед мержем в main. Второй мотив: изолировать AI-кодинг от Mac (SSD страдает от нагрузки агентных инструментов вроде Codex).

Формат — эксперимент: сработает — оставляем и развиваем, не понравится — VPS сносится.

**Архитектура одним абзацем.** На отдельном VPS сначала разворачивается OmniRoute (локальный LLM-гейтвей `localhost:20128/v1`: free-тиры, ChatGPT-подписка через Codex OAuth, fallback-комбо), и только потом — Hermes Agent, который подключается к нему сразу же, без промежуточного этапа на прямом OpenRouter. Hermes ведёт мультиролевой кодинг-луп: оркестратор декомпозирует задачу с таскборда, coder пишет код в отдельном git worktree, cleaner прибирает, reviewer проверяет, GitHub Actions — детерминированный гейт, `goal_judge` решает «готово/не готово», мерж в main — только руками. Проекты: wikibot и трейдинг-боты — **отдельные git-репозитории**, каждый со своим клоном, таскбордом и worktree.

## Порядок установки (важно, изменено 20.07)

**Сначала OmniRoute, потом Hermes.** Раньше план был «Hermes на прямом OpenRouter → потом переключить на OmniRoute» — теперь короче: OmniRoute разворачивается первым (раздел 4), провайдеры и комбо собираются сразу, а Hermes (раздел 5) с первого чата уже смотрит на `http://localhost:20128/v1`. Это убирает лишний промежуточный шаг и риск забыть переключить конфиг.

## Роли и модели (финально, 20.07)

| Роль | Основной путь | Фолбэк |
|---|---|---|
| Оркестратор (декомпозиция, kanban, координация) | ChatGPT-подписка через Codex OAuth в OmniRoute (`cx/gpt-5.5`) — из оплаченной квоты, без доп. затрат | DeepSeek V4 — тоже через OmniRoute (2-я ступень `combo-orchestrator`); прямого эквивалента подписки в OpenRouter нет |
| Coder (высокая цена ошибки) | `combo-coder` в OmniRoute; старт — DeepSeek V4, модели уточняем в пилоте | прямой OpenRouter (только если сам OmniRoute упал) |
| Reviewer (высокая цена ошибки) | `combo-reviewer` в OmniRoute; старт — DeepSeek V4, не удешевляем | прямой OpenRouter (то же) |
| Cleaner (линт, форматирование, commit-msg) | `combo-basechat`: free-каскад `if/kimi-k2` (безлимит) → opencode-zen → kilo-gateway → mistral → gemini-flash → groq → cerebras | последняя ступень каскада — DeepSeek V4 Flash (платно) |
| Базовый чат Hermes (Telegram, вне таск-пайплайна) | тот же `combo-basechat` | то же |

Принцип: **основной путь всех ролей — OmniRoute; прямой OpenRouter — фолбэк уровня инфраструктуры** (если процесс OmniRoute недоступен), не замена модели. `kiro` исключён из всех комбо (ToS запрещает агентские обвязки). Kimi K2 — кандидат в coder на эмпирический тест в пилоте, не сразу в прод. Циркуит-брейкер/cooldown у OmniRoute встроены — исчерпавший лимит провайдер пропускается сам.

## Фазы

| Фаза | Что | Статус |
|---|---|---|
| 1 | SSH-ключ на Mac, VPS арендован, харднинг сделан (включая Node.js) | ☐ |
| 2 | **OmniRoute развёрнут первым**: провайдеры подключены (Codex OAuth, OpenRouter, free-тиры), комбо собраны | ☐ |
| 3 | Hermes установлен и сразу подключён к OmniRoute (без промежуточного прямого OpenRouter), первый чат работает | ☐ |
| 4 | Telegram-гейтвей + allowlist + systemd (работает 24/7) | ☐ |
| 5 | Подготовка пилота: репо склонированы, SKILL.md на проект написан, таскборд синхронизирован, PAT создан | ☐ |
| 6 | **Пилот: кодинг-автоматизация на одном проекте, 2 недели обкатки** (цикл из раздела 7) | ☐ |
| 7 | Второй проект подключён (после стабильности пилота) | ☐ |
| 8а | *(бэклог)* Задача: скан вакансий | ☐ |
| 8б | *(бэклог)* Задача: отчёт о расходах | ☐ |
| 8в | *(бэклог)* Задача: фриланс-воронка + UZ-networking + маппинг узбекских компаний/вилок/позиций | ☐ |

## Ключевые решения

- **Фреймворк: Hermes, не OpenClaw** (20.07). Готовый skill-блок `software-development` (review-гейт перед коммитом, автономный PR-цикл, разбор фейлов GitHub Actions), нативный OpenRouter. OpenClaw — общий message-router, кодинг-skills пришлось бы писать с нуля.
- **Новый отдельный VPS** — на текущем боты с секретами (ключи кошельков), Hermes к ним не подпускаем.
- **Claude Pro НЕ используется** — KB-сессии остаются на Claude отдельно, токены не жжём.
- **Порядок установки (20.07): OmniRoute первым, Hermes сразу к нему подключается** — без промежуточного этапа на прямом OpenRouter. DeepSeek внутри OmniRoute всё равно идёт через OpenRouter (один аккаунт), с фиксом официального провайдера в настройках (анти-квантизация, см. 4.3) — иначе лотерея хостеров ломает tool-calling.
- **OmniRoute — общая инфраструктура VPS** (не только для кодинга): free-тиры (~1.6B токенов/мес по каталогу), ChatGPT-подписка, комбо с fallback, дашборд расходов, сжатие токенов. Ставится на VPS (Hermes ходит по localhost), наружу не открывается, дашборд — через SSH-туннель. Для локальных инструментов на Mac (если понадобится) — Remote mode (`omniroute connect`, scoped-токены), не второй инстанс.
- **GitHub Actions — обязательный гейт** перед мержем в main; агент не мержит напрямую, на пилоте мерж только ручной.
- **Репозитории раздельные:** wikibot и трейдинг-боты — отдельные git-репо, свой клон/таскборд/worktree у каждого; fine-grained PAT покрывает только эти два репо.
- **Hermes не имеет доступа к knowledge-base** (16.07, в силе): таскборд синхронизируется как отдельный файл в репо на VPS, а не монтированием KB.
- **Условие остановки лупа обязательно:** `/goal` + `goal_judge`, лимит 2 fix-циклов, потом эскалация в Telegram; дневной cost-cap (см. раздел 7).

## Открыто, решить при установке

- Механизм синхронизации таскборда: каким способом `projects/<имя>/BACKLOG.md` из KB попадает на VPS и как статусы возвращаются обратно.
- Создать fine-grained GitHub PAT (только wikibot + трейдинг-боты).
- Проверить на практике: `delegate_task`-саб-агенты по умолчанию изолированы от файлов родителя — обязательно передавать `workdir` на нужный worktree.
- Named-профили «роль→модель» — пока open feature request (#46880) в репо Hermes; модель задаём явно в каждом `delegate_task`.
- Точные слаги моделей/провайдеров в OmniRoute и наполнение `combo-coder`/`combo-reviewer` — сверить в дашборде при настройке; free-тиры меняются часто, каталог проверять по живой странице `/dashboard/free-tiers`, а не по цифрам из этого файла.
- Поддерживает ли мастер `hermes setup` выбор custom/OpenAI-compatible провайдера напрямую в TUI, или нужно сначала пройти мастер с любым провайдером и потом руками поправить `config.yaml` до первого теста (раздел 5.2) — уточнить на месте.

---

## 0. Как ты будешь со всем этим работать (главное, прочитай первым)

VPS — это просто удалённый Linux-компьютер без экрана. Ты подключаешься к нему из **Terminal.app на Mac по SSH** — но только для установки и обслуживания. Повседневное общение с Hermes идёт **через Telegram с телефона/Mac**, как с обычным ботом. Терминал после настройки будешь открывать раз в пару недель.

| Что | Как открыть | Когда используешь |
|---|---|---|
| Терминал VPS | `ssh hermes@IP` из Terminal.app | Установка, обновления, логи. Редко |
| Hermes CLI/TUI | внутри SSH: команда `hermes --tui` | Настройка и отладка агента. Первая неделя |
| **Telegram-бот** | обычный чат в Telegram | **Вся повседневная работа. Основной способ** |
| Дашборд OmniRoute | браузер на Mac через SSH-туннель (раздел 4) | Настройка провайдеров/комбо, статистика расходов |

Веб-интерфейсы на VPS наружу в интернет не открываем — вместо этого **SSH-туннель**: команда на Mac пробрасывает порт VPS на твой localhost, и ты открываешь его в Safari/Chrome как будто он локальный.

## 1. Подготовка на Mac и сервере (SSH-ключ, VPS, харднинг)

### 1.1 SSH-ключ на Mac (5 минут)

SSH-ключ = пара файлов: приватный (остаётся на Mac, никому не показывать) + публичный (кладётся на сервер). Вход по ключу вместо пароля — стандарт.

```bash
# В Terminal.app на Mac. Если ключ уже есть (ls ~/.ssh/*.pub что-то показывает) — пропусти.
ssh-keygen -t ed25519 -C "mvoramu@gmail.com"
# Enter на все вопросы (путь по умолчанию, passphrase можно пустую)

cat ~/.ssh/id_ed25519.pub   # ← это публичный ключ, скопируй вывод целиком
```

### 1.2 Аренда VPS: Hetzner Cloud (~15 минут)

Требования Hermes: 2 GB RAM / ~1 GB диска. Берём 4 GB — с запасом под Docker-песочницу, OmniRoute и клоны репозиториев.

1. Регистрация: https://console.hetzner.com (потребуют карту или PayPal, спишут €0 для верификации).
2. **New Project** → назови `hermes`.
3. **Add Server**:
   - Location: **Falkenstein** или **Nuremberg** (до Варшавы ~20 мс);
   - Image: **Ubuntu 24.04**;
   - Type: **Shared vCPU → CX22** (2 vCPU / 4 GB / 40 GB, ~€4/мес);
   - SSH keys → **Add SSH key** → вставь публичный ключ из шага 1.1;
   - Остальное по умолчанию → **Create & Buy now**.
4. Через ~30 секунд сервер готов, скопируй его **IP-адрес** из консоли.

Проверка входа с Mac: `ssh root@IP` → на вопрос про fingerprint ответь `yes` → ты внутри (приглашение `root@...`). Выход — `exit`.

### 1.3 Харднинг сервера (~20 минут, один раз)

Всё выполняется в SSH-сессии под root. Копируй блоками.

```bash
# 1.3.1 Обновить систему
apt update && apt upgrade -y

# 1.3.2 Создать рабочего пользователя (под root не работаем)
adduser hermes            # придумай пароль, остальные вопросы — Enter
usermod -aG sudo hermes
mkdir -p /home/hermes/.ssh
cp ~/.ssh/authorized_keys /home/hermes/.ssh/   # твой ключ теперь работает и для hermes
chown -R hermes:hermes /home/hermes/.ssh && chmod 700 /home/hermes/.ssh

# 1.3.3 Запретить вход по паролю и под root
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh

# 1.3.4 Файрвол: наружу только SSH
apt install -y ufw fail2ban unattended-upgrades
ufw allow OpenSSH && ufw --force enable
dpkg-reconfigure -plow unattended-upgrades   # выбери Yes (автообновления безопасности)

# 1.3.5 Docker (песочница для команд Hermes)
curl -fsSL https://get.docker.com | sh
usermod -aG docker hermes

# 1.3.6 Node.js (нужен OmniRoute, ставим первым делом — раньше зависимость закрывал установщик Hermes, теперь порядок обратный)
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs

# 1.3.7 Зависимости для установщика Hermes
apt install -y git curl xz-utils
```

⚠️ **Прежде чем закрыть root-сессию**, проверь в новой вкладке Terminal, что `ssh hermes@IP` работает. Дальше всегда входи как `hermes@IP`.

## 2. OmniRoute — ставим первым (~40 минут)

Зачем первым: оркестратор Hermes работает через ChatGPT-подписку (Codex OAuth), а этот путь существует только внутри OmniRoute — значит, Hermes нечего конфигурировать, пока OmniRoute не поднят и не собраны комбо.

### 2.1 Установка

```bash
# на VPS под пользователем hermes, Node.js уже стоит (шаг 1.3.6)
npm install -g omniroute
mkdir -p ~/.omniroute
nano ~/.omniroute/.env
```

```env
JWT_SECRET=длинная-случайная-строка      # сгенерируй: openssl rand -hex 32
INITIAL_PASSWORD=пароль-для-дашборда
PORT=20128
```

Запуск — команда `omniroute` (слушает только localhost). systemd-юнит:

```ini
# /etc/systemd/system/omniroute.service
[Unit]
Description=OmniRoute Gateway
After=network-online.target
Wants=network-online.target

[Service]
User=hermes
WorkingDirectory=/home/hermes
ExecStart=/usr/bin/env omniroute
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now omniroute
systemctl status omniroute       # active (running) = готово
```

### 2.2 Дашборд с Mac через SSH-туннель

```bash
# на Mac; держи окно открытым, пока работаешь с дашбордом
ssh -L 20128:localhost:20128 hermes@IP
# теперь в браузере на Mac: http://localhost:20128/dashboard
```

Закрыл SSH-сессию — туннель закрылся; дашборд снова доступен только после новой команды. Для удобства — алиас в `~/.zshrc` на Mac: `alias omni-tunnel='ssh -L 20128:localhost:20128 hermes@IP'`.

### 2.3 Ключ OpenRouter + фикс провайдера

https://openrouter.ai → **Keys** → создать ключ (`sk-or-...`) → пополнить баланс на $10 (заодно поднимает лимиты на `:free`-модели). Цены DeepSeek через OpenRouter: V4 Flash $0.09/$0.18, V4 Pro $0.435/$0.87 за 1M токенов (+~5% комиссия на пополнение).

⚠️ **Критично для агента:** по умолчанию OpenRouter раскидывает запросы к DeepSeek между десятками хостеров в разных квантизациях — у части из них нестабилен tool-calling, а на этом агентный цикл ломается. В аккаунте OpenRouter: **Settings → провайдерские настройки** — ограничь DeepSeek-модели официальным провайдером DeepSeek (или внеси ненадёжных в Ignored Providers). Один раз, спасает недели странных глюков.

### 2.4 Подключить провайдеров (Dashboard → Providers)

- **OpenRouter** — ключ `sk-or-...` из 2.3 (даёт DeepSeek V4/Flash).
- **Codex (ChatGPT-подписка)** — Providers → Codex → добавить подключение → OAuth-логин своим ChatGPT Plus/Pro аккаунтом (порт 1455). Даёт `cx/gpt-5.5` и т.п. из оплаченной квоты подписки, без доп. API-затрат.
- **Free-провайдеры** (для cleaner/базового чата; ключ не всегда нужен): `kimi` (`if/kimi-k2`, безлимитно — есть в готовых комбо `free-forever`/`openclaw-free`), `opencode-zen`, `kilo-gateway`, `mistral`, `gemini` (Flash-семейство), `groq`, `cerebras`. **Не подключай `kiro`** — ToS запрещает доступ через агентские обвязки. Актуальность лимитов сверяй по живой странице `/dashboard/free-tiers`.

### 2.5 Собрать combo под роли

Стратегия всех комбо — `priority` (осушить ступень → перейти к следующей):

```yaml
# псевдо-конфиг; точный синтаксис — в дашборде OmniRoute при создании combo
combo-orchestrator:
  - codex/cx-gpt-5.5               # ChatGPT-подписка, приоритет 1
  - openrouter/deepseek-v4         # фолбэк, если квота Codex исчерпана

combo-coder:                        # модели уточняем в пилоте; ориентир — надёжный tool-calling
  - openrouter/deepseek-v4

combo-reviewer:                     # не удешевляем
  - openrouter/deepseek-v4

combo-basechat:                     # cleaner-задачи + обычный чат Hermes
  - if/kimi-k2                      # безлимитно бесплатно
  - opencode-zen
  - kilo-gateway
  - mistral
  - gemini-flash
  - groq
  - cerebras
  - openrouter/deepseek-v4-flash   # платный фолбэк, когда все free исчерпаны
```

К моменту установки Hermes (раздел 3) все четыре комбо должны существовать и быть проверены в дашборде (Test connection на каждом провайдере) — Hermes сразу пойдёт в них, тестировать на живом агенте нечего.

## 3. Установка Hermes — сразу к OmniRoute (~30 минут)

Раньше здесь был отдельный «этап А» на прямом OpenRouter с последующим переключением. Теперь короче: OmniRoute уже поднят (раздел 2), Hermes настраивается на него с первого чата.

### 3.1 Установка

```bash
# на VPS под пользователем hermes
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser
source ~/.bashrc
hermes doctor    # всё зелёное = ок
```

`--skip-browser` — пропускаем браузерную автоматизацию (не нужна для наших задач, экономит место; включить можно потом).

### 3.2 Мастер настройки — указать OmniRoute

```bash
hermes setup
```

Интерактивный TUI-мастер (стрелки + Enter):

- Режим: **Full Setup** (не Nous Portal — платная подписка Nous, не Blank Slate).
- Провайдер: если мастер предлагает **Custom / OpenAI-compatible** — выбери его, укажи `base_url: http://localhost:20128/v1`, API-ключ — тот, что создashь в дашборде OmniRoute (Dashboard → API Keys), модель по умолчанию — `combo-basechat`. Если такого пункта в TUI нет — пройди мастер с любым провайдером-заглушкой и сразу поправь `~/.hermes/config.yaml` вручную (см. 3.4) до первого теста чата.
- Terminal backend: **Docker** (изоляция: команды агента выполняются в контейнере, не на хосте).
- Messaging gateway: пока **пропусти** — подключим в разделе 4.
- Инструменты (web search и т.д.): включи **web search**, остальное по вкусу; всё меняется позже через `hermes tools`.

Секреты лягут в `~/.hermes/.env`, настройки — в `~/.hermes/config.yaml`.

### 3.3 Первый чат — проверка

```bash
hermes --tui
```

Проверь последовательно: (1) баннер показывает модель из `combo-basechat`; (2) обычный вопрос — отвечает; (3) «What's my disk usage? Show top 5 directories» — агент запускает команду и показывает результат; (4) выйди и `hermes -c` — сессия возобновляется. Если что-то сломалось: `hermes doctor` → `hermes model` → снова чат. Пока это не работает — дальше не идти.

Если чат не поднимается через OmniRoute и непонятно почему — временный диагностический шаг: переключи `provider` на `openrouter` / `deepseek/deepseek-v4` напрямую (без OmniRoute), проверь, что дело не в самом Hermes, потом возвращайся к отладке OmniRoute. Это диагностика, не постоянная схема.

### 3.4 Полный конфиг ролей

`~/.hermes/config.yaml` (редактор: `nano ~/.hermes/config.yaml`, сохранить Ctrl+O, выйти Ctrl+X):

```yaml
model:
  provider: "custom"
  base_url: "http://localhost:20128/v1"
  api_key: "ключ-созданный-в-дашборде-omniroute"
  default: "combo-basechat"          # обычный чат Hermes в Telegram
  auxiliary:
    kanban_decomposer: { model: "combo-orchestrator" }   # декомпозиция таска на подзадачи
    compression:       { model: "combo-basechat" }
    title_generation:  { model: "combo-basechat" }
    web_extract:       { model: "combo-basechat" }
    # curator НЕ удешевляем: он курирует библиотеку навыков, ошибки дорогие
```

Для `delegate_task` модель передаётся явно на каждый вызов (named-профили — пока только feature request #46880), обязательно с `workdir` на нужный git worktree:

- coder → `model: "combo-coder"`
- reviewer → `model: "combo-reviewer"`
- cleaner → `model: "combo-basechat"`

**Откат:** если сам OmniRoute недоступен (процесс упал) — переключить `provider`/`base_url` на прямой OpenRouter (`provider: "openrouter"`, `default: "deepseek/deepseek-v4"`) для coder/cleaner/reviewer — это фолбэк уровня инфраструктуры. У оркестратора прямого отката в OpenRouter нет (подписка ChatGPT существует только внутри OmniRoute) — его фолбэк на DeepSeek V4 уже встроен второй ступенью `combo-orchestrator`, чинить нужно сам OmniRoute, а не конфиг Hermes.

## 4. Telegram + 24/7

### 4.1 Гейтвей

```bash
hermes gateway setup
```

Выбери **Telegram** — даст ссылку на предконфигурированного бота, свой токен не нужен. Открой ссылку, нажми Start.

**Обязательно** ограничь доступ своим Telegram user ID (узнать: напиши боту @userinfobot). В `config.yaml` найди секцию telegram → `allowed_user_ids` (точное имя поля покажет `hermes config get`); проверь статус: `hermes gateway status`.

### 4.2 systemd — чтобы Hermes жил после закрытия терминала

Без этого Hermes умирает вместе с SSH-сессией. Создаём сервис:

```bash
sudo nano /etc/systemd/system/hermes.service
```

```ini
[Unit]
Description=Hermes Agent Gateway
After=network-online.target docker.service omniroute.service
Wants=network-online.target
Requires=omniroute.service

[Service]
User=hermes
WorkingDirectory=/home/hermes
ExecStart=/home/hermes/.local/bin/hermes gateway
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

(если `hermes gateway` не команда запуска — сверь с `hermes gateway --help`, возможно `hermes gateway run`; `Requires=omniroute.service` — Hermes стартует только после того, как OmniRoute поднялся, раз он теперь от него зависит с первого чата)

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes
systemctl status hermes          # active (running) = готово
journalctl -u hermes -f          # живые логи (Ctrl+C — выход)
```

**С этого момента терминал больше не нужен для общения** — пишешь боту в Telegram. Полезные команды в чате: `/help`, `/background <задача>`, `/goal`, `/model`.

### 4.3 Шпаргалка обслуживания (SSH, раз в 1–2 недели)

```bash
ssh hermes@IP
hermes update                 # обновить Hermes
omniroute update 2>/dev/null || npm update -g omniroute   # обновить OmniRoute
sudo apt update && sudo apt upgrade -y
systemctl restart omniroute && systemctl restart hermes   # порядок важен — Hermes зависит от OmniRoute
journalctl -u hermes --since today   # что происходило
journalctl -u omniroute --since today
df -h / && free -h            # диск и память
```

## 5. Дизайн воркфлоу: автоматизация кодинга (loop engineering)

По мотивам loop engineering (Addy Osmani, LangChain, тред sairahul1: «не промптишь агента — строишь систему, которая промптит его сама»). Обязательные части лупа: триггер, память, разделение автор/проверяющий, условие остановки — без последнего луп крутится вечно и жрёт бюджет, пока ты спишь.

**Репозитории.** wikibot и трейдинг-боты — отдельные git-репозитории, каждый клонируется на VPS отдельно (`~/repos/wikibot`, `~/repos/trading-bots`), у каждого свой таскборд (`projects/<имя>/BACKLOG.md` из KB, механизм синхронизации — открытый вопрос в шапке) и свой скоуп в fine-grained PAT. Пилот — сначала один проект; второй подключаем через 2 недели после стабильности.

**Триггер (heartbeat).** Ежедневный cron (утро) — оркестратор читает таскборд текущего проекта + вчерашние фейлы GitHub Actions, берёт следующую готовую задачу. Плюс `/background <задача>` из Telegram для разовых запросов вне расписания.

**Память.** Таскборд (что сделано / в работе / зафейлилось и почему) — не полагаемся на память агента между запусками; вся история — в файле и git-логе.

**Skills — написать до старта пилота.** По `SKILL.md` на каждый репозиторий: структура, как гонять тесты, деплой, конвенции, «почему не делаем так-то». Способ: надиктовать голосом → отдать Hermes как основу скилла. Без этого агент каждый цикл заново выясняет контекст с нуля.

**Изоляция (worktrees).** Каждая задача — свой `git worktree` на фиче-ветке внутри репозитория своего проекта; параллельные задачи не сталкиваются файлами.

**Цикл на одну задачу:**

1. Оркестратор берёт задачу с борда → ставит `/goal` («PR открыт, Actions зелёный, reviewer одобрил») → kanban_decomposer бьёт на подзадачи.
2. Открывается worktree на фиче-ветке в репозитории проекта.
3. Coder реализует → Cleaner прибирает/пишет commit message → пуш, PR.
4. Reviewer (skill `requesting-code-review`) проверяет; если нужны правки — до **2 циклов fix**, не больше.
5. GitHub Actions — детерминированный гейт (тесты/линт).
6. `goal_judge` (отдельная модель, не та, что писала код) решает «готово или нет»:
   - готово → статус в таскборде, PR ждёт ручного мержа (на пилоте — без авто-мержа);
   - не готово после лимита попыток → эскалация в Telegram, луп для этой задачи останавливается — не крутится вхолостую.

**Cost-cap.** Дневной потолок расходов — если луп застрял в ретраях, он не должен незаметно съесть бюджет за ночь. Следить в дашборде OmniRoute.

**Самообучение.** Отдельный «hill-climbing»-луп не строим — у Hermes встроен Curator (сам сохраняет и улучшает skills из опыта); в конце каждой недели пилота просматривать, что он насохранял.

## 6. Бэклог-задачи (фазы 8а–8в, после пилота)

**Скан вакансий.** Через Telegram, без терминала: cron-задача — источники (tg-каналы/борды из job-search/), критерии раннего remote-теста, время дайджеста. Сбор постов — скрипт, LLM (Flash/free) — только фильтрация, дайджест — одно сообщение в день. Workflow создания: надиктовать голосом, как сам ищешь и отсеиваешь вакансии → отдать Hermes как основу скилла → evals из 10 реальных постов с разметкой → тест → потом в cron. Две недели считать precision.

**Отчёт о расходах** и **фриланс-воронка + UZ-networking** — по той же схеме, по одной задаче за раз, только после стабильности предыдущей.

## 7. Бюджет

| Статья | /мес |
|---|---|
| VPS Hetzner CX22 | ~€4 |
| OpenRouter: DeepSeek V4 (coder/reviewer в пилоте) + V4 Flash (фолбэки) | ~$1–5 |
| ChatGPT-подписка (оркестратор) | уже оплачена, доп. затрат нет |
| Free-каскад (cleaner, базовый чат) | $0 |
| **Итого доп. затрат** | **~€5–9** |

Порог тревоги: расход >$5/мес на OpenRouter → смотреть дашборд OmniRoute / Activity на openrouter.ai, какая роль жрёт. Плюс дневной cost-cap из раздела 5.

## 8. Безопасность (чеклист)

- ☐ Отдельный VPS, никаких ключей кошельков/других ботов на нём
- ☐ Вход только по SSH-ключу, root-вход запрещён, ufw включен
- ☐ Telegram allowlist: только мой user ID
- ☐ terminal.backend = docker
- ☐ OmniRoute только на 127.0.0.1, доступ — SSH-туннель
- ☐ Баланс OpenRouter без автопополнения (top-up руками)
- ☐ Никакого доступа Hermes к knowledge-base и iCloud (таскборд — отдельный синхронизируемый файл)
- ☐ GitHub-доступ — fine-grained PAT, скоуп только на репо wikibot/трейдинг-боты (не на весь аккаунт), без прав на другие приватные репо
- ☐ Docker-контейнер агента не монтирует и не видит хостовые секреты — в его `.env` только GitHub PAT + ключи OpenRouter/OmniRoute, никаких wallet-ключей и .env других ботов
- ☐ OmniRoute MITM/TPROXY (перехват TLS через кастомный root CA) — не включать по умолчанию; если понадобится для конкретного инструмента — ограничить только им
- ☐ Мерж в main — только руками (на пилоте), агент максимум открывает PR
- ☐ `hermes.service` стартует после `omniroute.service` (`Requires=`/`After=` в systemd) — Hermes теперь зависит от OmniRoute с первого запуска

## 9. Troubleshooting (типовые грабли новичка)

| Симптом | Причина → фикс |
|---|---|
| `hermes: command not found` | `source ~/.bashrc`; или PATH без `~/.local/bin` |
| `omniroute: command not found` | Node.js не установлен до `npm install -g omniroute` — проверь `node -v` |
| Пустые/битые ответы в чате | провайдер/ключ → `hermes model` заново; проверь, что OmniRoute вообще отвечает (`systemctl status omniroute`) |
| Бот в Telegram молчит | `hermes gateway status`; `journalctl -u hermes -f`; allowlist? |
| После перезагрузки VPS всё умерло | `systemctl enable hermes` и `systemctl enable omniroute` — оба забыты? |
| SSH-туннель «connection refused» | omniroute не запущен: `systemctl status omniroute` |
| Hermes не стартует вообще | проверь, поднялся ли `omniroute.service` первым — Hermes теперь от него зависит (`Requires=`) |
| Агент «не видит» файлы репозитория | `delegate_task` без `workdir` — саб-агент изолирован от файлов родителя |
| Луп жрёт токены без результата | проверь `/goal`-условие и лимит fix-циклов; смотри расходы в дашборде OmniRoute |
| Всё сломалось, непонятно где | по порядку: `systemctl status omniroute` → `hermes doctor` → `hermes model` → `hermes sessions list` → `hermes gateway status` |

Доки: https://hermes-agent.nousresearch.com/docs/ (видео-мастеркласс — на странице Quickstart) · https://github.com/diegosouzapw/OmniRoute (доки в /docs).

---

## Лог (append-only)

- 2026-07-17 — Проект создан (перенос из ideas/инструменты). Решения: новый VPS (изоляция секретов), без Claude Pro, business research вычеркнут, задачи по одной со скана вакансий.
- 2026-07-17 — Инструкция переписана детально для первого раза. Архитектурное изменение: этап А — без OmniRoute (меньше движущихся частей); OmniRoute перенесён в фазу 5. Добавлено: SSH-ключи с Mac, пошаговый Hetzner, харднинг, systemd, SSH-туннель для дашборда, troubleshooting.
- 2026-07-17 — Решение: DeepSeek идёт через OpenRouter (один аккаунт), а не через прямой DeepSeek API. Условие: зафиксировать официального провайдера DeepSeek в настройках OpenRouter (анти-квантизация).
- 2026-07-17 — Решение: маппинг узбекских компаний/вилок/позиций — не отдельная задача и не реванш вычеркнутого «business research» (16.07), а часть задачи 3 (фриланс-воронка + UZ-networking), фаза 7. Пересекается с job-search TODO «карта узбекского рынка с вилками» (август) — Hermes закрывает этот пункт, когда дойдёт очередь до фазы 7.
- 2026-07-17 — **Проект заморожен.** Разбор трёх задач показал: все они — фиксированные пайплайны (fetch → LLM-фильтр/анализ → пуш), не нуждаются в agentic-цикле; проще и дешевле как скрипты на существующем VPS тем же стеком, что ETH-бот/xstocks-бот/job search bot/voice bot. Ad hoc-режим (`/background` с телефона) сам по себе не признан достаточным поводом держать отдельный VPS + Hermes framework. Решение: не разворачивать, пока не появится задача, которая явно требует именно автономного агента, а не скрипта. Карта узбекского рынка с вилками (job-search TODO, август) теперь без привязки к Hermes — делать иначе (руками или простым скриптом).
- 2026-07-20 — **Проект разморожен, эксперимент.** Новая задача (из inbox-заметки) — автоматизация кодинга/дебага личных ботов (wikibot, трейдинг-боты): агент читает таскборд из Knowledge Base, кодит, дебажит, пушит в GitHub; GitHub Actions проверяет PR перед мержем в main. В отличие от трёх задач 17.07 (фиксированные пайплайны), это реально требует agentic-цикла — критерий разморозки выполнен. Второй мотив: изолировать AI-кодинг от Mac (SSD страдает от нагрузки агентных инструментов вроде Codex). Формат — эксперимент: сработает — оставляем, не понравится — VPS сносим. Модели: без Claude Pro (KB-сессии остаются на Claude отдельно); DeepSeek через OpenRouter — основной мозг; OmniRoute — free-тиры, экономия токенов приоритетна (дороже, чем прежние fixed-pipeline задачи). Открыто: выбор фреймворка (Hermes/OpenClaw), механика ролей менеджер(GPT)/исполнители(DeepSeek+Flash), способ подключения таскборда KB. Старые задачи (скан вакансий, отчёт о расходах, фриланс-воронка) остаются бэклогом.
- 2026-07-20 — **Фреймворк выбран: Hermes** (не OpenClaw). Сравнение: у Hermes готовый skill-блок `software-development` (review-гейт перед коммитом, автономный branch→код→commit→push→PR цикл, разбор фейлов GitHub Actions) и нативный OpenRouter — совпадает со стеком; OpenClaw — более общий message-router для мультиканального личного ассистента (WhatsApp/Telegram/Discord/20 каналов), под кодинг-ревью пришлось бы писать skills с нуля, хотя комьюнити крупнее (15k+ звёзд vs Hermes моложе, релиз 02.2026). Заодно подтверждено: OmniRoute (github.com/diegosouzapw/OmniRoute) — используем не только для кодинг-агента, а как общую инфраструктуру free-tier токенов под будущие задачи на этом VPS (бэклог: скан вакансий, расходы). Решение по безопасности: GitHub-доступ агента — fine-grained PAT только на репо wikibot/трейдинг-боты (не на весь аккаунт); Docker-контейнер агента не должен видеть хостовые секреты (только GitHub PAT + OpenRouter/OmniRoute ключи в его `.env`); MITM/TPROXY-функцию OmniRoute (кастомный root CA для перехвата TLS) по умолчанию не включать. Чек-лист безопасности (раздел 9) и открытые вопросы (шапка) обновлены соответственно.
- 2026-07-20 — **Механика ролей финализирована.** Оркестратор (декомпозиция/kanban/координация) — ChatGPT-подписка через Codex OAuth в OmniRoute (`cx/gpt-5.5`, тянет уже оплаченную квоту без доп. затрат), фолбэк DeepSeek V4. Coder/reviewer (высокая цена ошибки) — DeepSeek V4 через OpenRouter напрямую, без free-подмены; Kimi K2 — кандидат на тест в пилоте, не сразу в прод. Cleaner и базовый чат Hermes (низкая цена ошибки) — общий free-каскад OmniRoute `priority`: `if/kimi-k2` (безлимитно, комбо `free-forever`/`openclaw-free`) → opencode-zen → kilo-gateway → mistral → gemini-flash → groq → cerebras → DeepSeek V4 Flash (платный фолбэк). `kiro` исключён из всех комбо — ToS прямо запрещает доступ через агентские обвязки вроде Hermes. Место установки OmniRoute — VPS, не Mac; если понадобится покрыть free-tier роутингом локальные инструменты на Mac — через Remote mode OmniRoute (scoped-токены), не отдельным инстансом.
- 2026-07-20 — **Дизайн воркфлоу (loop engineering) добавлен, маршрутизация уточнена.** Триггер (ежедневный cron + `/background`), память (таскборд), skills на каждый репозиторий (написать до пилота), git worktree на задачу, цикл из 6 шагов с `/goal`/`goal_judge` как условием остановки (лимит 2 циклов fix, дальше — эскалация в Telegram, не бесконечный ретрай), дневной cost-cap, самообучение — не строим отдельно, у Hermes уже встроено (Curator). Уточнения: (1) wikibot и трейдинг-боты — **отдельные git-репозитории**, каждый со своим клоном/таскбордом/worktree на VPS, fine-grained PAT покрывает оба; (2) маршрутизация моделей скорректирована — coder/cleaner/reviewer тоже идут через OmniRoute, с прямым OpenRouter как фолбэком уровня инфраструктуры, кроме оркестратора (фолбэк тоже через OmniRoute — ChatGPT-подписке нет прямого эквивалента в OpenRouter); конкретные модели для `combo-coder`/`combo-reviewer` — выбрать позже при тестировании, стартовая точка — DeepSeek V4.
- 2026-07-20 — Файл переписан начисто (устранение противоречий, накопившихся за день правок): сводная таблица ролей/моделей в шапке, консолидированные «Ключевые решения», исправлен порядок фаз (OmniRoute — до кодинг-пилота).
- 2026-07-20 — **Порядок установки изменён: OmniRoute первым, Hermes сразу подключается к нему.** Раньше план был «Hermes на прямом OpenRouter (этап А) → переключить на OmniRoute (этап Б)»; теперь этот промежуточный шаг убран целиком — OmniRoute (провайдеры, комбо) разворачивается первым в новом разделе 2, Hermes ставится в разделе 3 и с первого теста чата уже смотрит на `http://localhost:20128/v1` с полным набором комбо (`combo-orchestrator/coder/reviewer/basechat`). Добавлено: шаг установки Node.js в харднинг (1.3.6, раньше эту зависимость закрывал установщик Hermes — при обратном порядке её пришлось вынести раньше), systemd-юнит `omniroute.service`, зависимость `hermes.service` от него (`Requires=`/`After=`), обновлённая шпаргалка обслуживания (порядок рестарта: сначала omniroute, потом hermes) и новые пункты в чек-листе безопасности и troubleshooting. Все разделы файла перенумерованы под новый порядок (0, 1 — подготовка, 2 — OmniRoute, 3 — Hermes, 4 — Telegram/systemd, 5 — дизайн воркфлоу, 6 — бэклог, 7 — бюджет, 8 — безопасность, 9 — troubleshooting).
