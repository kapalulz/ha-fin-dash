# Findash → Home Assistant

Интеграция `findash` и шесть карточек для дашборда Home Assistant: **Мои деньги**,
**Куда идут деньги**, **Сегодня**, **Лимиты**, **Прогноз**, **Игра**. Данные считает сервер
Findash; Home Assistant только читает итоги одним запросом раз в 5 минут. Каждую карточку
можно настроить: убрать любой блок, выбрать нужные полоски и плитки и их порядок.

Финальная версия публикуется в репозитории
[kapalulz/ha-fin-dash](https://github.com/kapalulz/ha-fin-dash) — оттуда её ставит HACS.
В нём только код интеграции и карточек: адрес Findash и токены вводятся в Home Assistant.

## 1. Сервер Findash

Сгенерировать токен и добавить его в `.env` Findash, затем перезапустить сервис:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'   # → FIN_HA_TOKEN=...
systemctl --user restart fin-dash
```

Endpoint: `GET /api/home-assistant/money-flow`, заголовок `Authorization: Bearer <токен>`.
Без токена он выключен (503), с неверным — 401. Токен открывает только эту сводку: ни
остальное API, ни изменение данных. Опрос не запускает синхронизацию с банками.

Адрес должен быть доступен **с машины Home Assistant** (`localhost` внутри HA — это сам HA):

- **Через Cloudflare Access** (рекомендуется): Zero Trust → Access → Service credentials →
  **Service Tokens** → Create. В приложении Findash добавить политику **Service Auth**,
  разрешающую этот токен. В интеграции — публичный HTTPS-адрес и оба поля Cloudflare.
  Не отключайте Access для всего сайта.
- **По частной сети**: Findash слушает `127.0.0.1:8097`; нужен HTTPS reverse proxy или туннель,
  доступный HA по LAN/VPN. HTTP допустим только для проверки — токен идёт открыто.

## 2. Установка

**Через HACS** (рекомендуется): HACS → ⋮ → **Custom repositories** →
`https://github.com/kapalulz/ha-fin-dash`, тип **Integration** → **Add** → найти **Findash** →
**Download** → перезапустить Home Assistant.

**Вручную**: скопировать `custom_components/findash` в `/config/custom_components/findash`
и перезапустить Home Assistant.

Затем **Настройки → Устройства и службы → Добавить интеграцию → Findash**: адрес Findash
(без пути), значение `FIN_HA_TOKEN`, при Cloudflare — Client ID и Client Secret.
Соединение проверяется до сохранения; при смене токена HA сам предложит ввести его заново.

**Карточки подключаются автоматически** — интеграция сама загружает `findash-cards.js` на всех
дашбордах (ресурсы добавлять не нужно). Если раньше вы добавляли ресурсы
`/local/findash-money-flow-card.js` или `/local/findash-overview-card.js` — удалите их
(**Настройки → Панели управления → ⋮ → Ресурсы**) и файлы из `/config/www/`.
После обновления интеграции достаточно перезапустить HA и обновить страницу.

## 3. Сенсоры

Устройство **Findash**, сенсоры (Entity ID может отличаться — карточки находят их сами по
атрибуту `findash_metric`):

| Сенсор | Состояние | Атрибуты |
|---|---|---|
| Money flow | остаток текущего месяца (`flow.now.rest`) | `flow` (план и этот месяц), `month`, `generated_at` |
| Debit, Credit, Cushion, Free | плитки сайта | у Free — `mandatory_left` |
| Today | «сегодня можно» | `data`: дни до конца месяца, доля прошедшего месяца, карманные, копилка |
| Limits | сколько лимитов исчерпано | `data`: все полоски (имя, потрачено, лимит, %, ok/warn/full/none, перенос) |
| Forecast | минимум на счетах за 30 дней | `data`: точки по дням, дата минимума, зарплата, ближайший платёж |
| Game | уровень | `data`: титул, опыт, серия, копилка, задания, достижения, дракон ипотеки |

Если сервер старее интеграции, новые сенсоры будут «недоступны», остальные работают.
При сбое связи все сенсоры становятся unavailable.

## 4. Карточки

**Edit dashboard → Add card** → в списке «Findash — Overview / Money flow / Today / Limits /
Forecast / Game». Всё настраивается в **визуальном редакторе**: галочки «Показывать» для каждого
блока, для «Лимитов» и «Моих денег» — галочки для каждой полоски и плитки. То же в YAML:

### Общие параметры (все карточки)

| Параметр | Значение |
|---|---|
| `entity` | сенсор; пусто — найдётся сам (нужно, только если интеграций несколько) |
| `title` | свой заголовок |
| `language` | `ru` / `en`; по умолчанию язык HA |
| `show_title` | `false` — без заголовка |

Любой блок убирается параметром `show_<блок>: false`. Размер — вкладка **Layout** (вид Sections).
Нажатие на карточку открывает сведения о сенсоре.

### `custom:findash-overview-card` — Мои деньги

| Параметр | |
|---|---|
| `tiles` | какие плитки и в каком порядке: `[free, debit]`; по умолчанию все четыре |
| `columns` | `auto` (2 на телефоне, в ряд на широком), `1`–`4` |
| `show_units` | валюта под числом |
| `debit` / `credit` / `cushion` / `free` | свой сенсор для плитки |

### `custom:findash-money-flow-card` — Куда идут деньги

`view: plan | now` — что открыто сначала. Блоки: `tabs` (переключатель), `month`, `totals`
(доход и платежи), `bar` (цветная полоса), `parts` (строки), `rest` (итог), `forecast`
(на конец месяца), `footer` (время расчёта).

### `custom:findash-today-card` — Сегодня

Блоки: `allowance` («можно потратить сегодня»), `days` (дней до конца месяца), `pocket`
(полоска карманных), `month_mark` (отметка «сколько месяца прошло»), `piggy` (копилка).

### `custom:findash-limits-card` — Лимиты

| Параметр | |
|---|---|
| `limits` | какие полоски и в каком порядке: `[food, eating_out, pocket]`. Id: `pocket`, `food`, `eating_out`, `shopping`, `home`, `car`, `fun` |
| `only_problems` | `true` — только жёлтые и красные (пусто → «Все лимиты в норме») |
| `columns` | `auto` (две колонки на широком), `1`, `2` |

Блоки: `values` (суммы и %), `bars`, `month_mark`, `carry` (перенос), `stop` («Хватит в этом месяце»).

### `custom:findash-forecast-card` — Прогноз

`days: 7 | 14 | 30`. Блоки: `summary` (минимум и дата), `warning` (если уходит в минус),
`chart`, `income` (зарплата), `payment` (ближайший платёж).

### `custom:findash-game-card` — Игра

Блоки: `hero` (портрет, титул, опыт), `stats` (серия, рекорд, копилка), `quests`, `boss`
(дракон ипотеки), `achievements`; `show_locked: true` — показать и ещё не полученные.
Карточка в тёмном «фэнтези» стиле, как на сайте, независимо от темы HA.

### Примеры

```yaml
# только «Свободно» крупно
type: custom:findash-overview-card
tiles: [free]
show_title: false
```

```yaml
# три нужные полоски, без процентов и переноса
type: custom:findash-limits-card
title: Еда и кафе
limits: [food, eating_out, pocket]
show_values: false
show_carry: false
```

```yaml
# прогноз на неделю, одна строка с минимумом
type: custom:findash-forecast-card
days: 7
show_chart: false
show_income: false
show_payment: false
```

```yaml
# только задания на сегодня
type: custom:findash-game-card
show_hero: false
show_stats: false
show_boss: false
show_achievements: false
```

## Ограничения

USD, как в Findash. Тексты лимитов, заданий, титул и имя дракона приходят с сервера на языке,
выбранном на сайте. Атрибуты сенсоров видят все пользователи вашего HA, и Recorder может
сохранять их в историю по вашим настройкам — решайте, что выносить на настенные экраны.

## Проверка

- Сервер (в Findash): `tests/test_home_assistant.py` — контракт, токен, совпадение с сайтом.
- Интеграция в настоящем Home Assistant: `tests/test_integration.py` — настройка, сенсоры,
  ошибки, повторный ввод токена, совместимость со старым сервером, автозагрузка карточек.
  Отдельный venv: `pip install -r requirements_test.txt`, затем `pytest` в этой папке.
- Карточки в Chromium: `tests/check_card.py`, `check_overview_card.py`, `check_cards.py`
  (темы, телефон и десктоп, ошибки датчика, безопасный заголовок, скрытие блоков, выбор
  полосок и плиток, редактор).
