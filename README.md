# ha-fin-dash

Home Assistant integration for [fin-dash](https://github.com/kapalulz/fin-dash) (a private
personal finance dashboard): free money, today's allowance, budget limits, 30-day forecast,
mortgage and the budget game — as sensors you can put on any card or use in automations.

Интеграция Home Assistant для fin-dash: «Свободно», «Сегодня можно», все полоски лимитов,
прогноз, ипотека и игра — как сенсоры. Ниже по-русски.

> Этот репозиторий публичный, но в нём только код. Адрес fin-dash и токены вводятся в
> Home Assistant и хранятся только там. Финансовые числа видят все, у кого есть доступ к
> вашему Home Assistant (в том числе настенные планшеты) — решайте, что выносить на экран.

## Что появится

Устройство **fin-dash** и сущности с постоянными id (не зависят от языка интерфейса):

| Сущность | Что | Атрибуты |
|---|---|---|
| `sensor.fin_dash_free` | Свободно: дебит − кредит − обязательные до конца месяца | `mandatory_left` |
| `sensor.fin_dash_can_spend_today` | Сегодня можно потратить | `days_left` |
| `sensor.fin_dash_debit`, `_credit`, `_cushion`, `_mandatory_left` | Плитки дашборда | |
| `sensor.fin_dash_pocket_spent` / `_pocket_pct` | Карманные: потрачено / % от плана | `monthly`, `left` |
| `sensor.fin_dash_month_elapsed` | Сколько % месяца прошло (сравнивать с полосками) | |
| `sensor.fin_dash_limit_food`, `_eating_out`, `_shopping`, `_home`, `_car`, `_fun` | Полоска лимита, % (может быть > 100) | `name`, `spent`, `limit`, `left`, `status` (ok / warn / full / none), `carry` |
| `sensor.fin_dash_forecast_min` | Минимум на счетах за 30 дней | `min_date`, `end`, `next_income_date`, `next_income` |
| `sensor.fin_dash_next_income_date` | Ближайшая зарплата (дата) | `amount` |
| `sensor.fin_dash_next_payment` | Ближайший платёж | `date`, `what`, `type` |
| `sensor.fin_dash_subscriptions_monthly`, `_sinking_monthly` | Подписки в месяц, годовые платежи в месяц | |
| `sensor.fin_dash_mortgage_balance`, `_prepay_monthly` | Ипотека | `payment`, `months_saved`, `remaining_months` |
| `sensor.fin_dash_warnings` | Число предупреждений консультанта | `items` (тексты) |
| `sensor.fin_dash_level`, `_streak`, `_piggy`, `_quests_done`, `_achievements`, `_dragon_hp` | Игра | `title`, `xp`, `level_pct`, `best`, `quests`, `total`, `hp`, `max_hp` |
| `binary_sensor.fin_dash_forecast_low` | Прогноз уходит в минус | `min`, `min_date` |
| `binary_sensor.fin_dash_limit_full` | Какой-то лимит исчерпан | `limits` |

Если в fin-dash нет ипотеки или полоски, соответствующий сенсор просто «недоступен».

## Установка

### 1. fin-dash

В `.env` fin-dash задайте токен и перезапустите сервис:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # → HA_TOKEN=...
systemctl --user restart fin-dash
```

Нужна версия fin-dash с эндпоинтом `GET /api/ha` (ветка `claude/fixes-and-features` и новее).

### 2. Как Home Assistant достучится до fin-dash — выберите один вариант

**а) Через Cloudflare Access (рекомендуется: защита не ослабляется)**

1. Cloudflare Zero Trust → **Access → Service credentials → Service Tokens → Create Service Token**
   (имя, например, `home-assistant`). Сохраните **Client ID** и **Client Secret** — секрет
   показывается один раз.
2. **Access → Applications** → приложение fin-dash → **Policies → Add a policy**:
   Action = **Service Auth**, Include → **Service Token** = `home-assistant`.
3. В Home Assistant адрес: `https://<ваш домен fin-dash>`, плюс оба поля Cloudflare.

**б) Напрямую по локальной сети** (HA на виртуалке того же сервера)

fin-dash по умолчанию слушает только `127.0.0.1`, виртуалке его не видно. Пусть слушает
адрес хоста во внутренней сети виртуалок (например, `--host 192.168.122.1` в
`deploy/fin-dash.service`). Остальные страницы fin-dash всё равно требуют входа через
Cloudflare; без него открыт только `/api/ha`, и только с `HA_TOKEN`. В Home Assistant адрес
вида `http://192.168.122.1:8097`, поля Cloudflare пустые.

### 3. Home Assistant

1. **HACS → ⋮ → Custom repositories** → `https://github.com/kapalulz/ha-fin-dash`,
   категория **Integration** → **Add**. Найдите **fin-dash** в HACS → **Download**.
2. Перезапустите Home Assistant.
3. **Settings → Devices & services → Add integration → fin-dash**: адрес, `HA_TOKEN`,
   при варианте «а» — Client ID и Client Secret.
4. Частота опроса: на карточке интеграции **Configure** (по умолчанию раз в 15 минут).

Если токен поменялся, Home Assistant сам предложит ввести его заново (Repairs / уведомление).

## Карточки

Готовый пример целого вида — [`examples/dashboard.yaml`](examples/dashboard.yaml):

1. **Свободно** — `tile`
2. **Сегодня можно** — `tile`
3. **Карманные** — `gauge` (зелёный → жёлтый с 80% → красный со 100%)
4. **Все полоски лимитов** — сетка `gauge`, стандартные карточки
5. **Те же полоски горизонтально** — `custom:bar-card` (HACS → Frontend → bar-card)
6. **Прогноз и платежи** — `entities`
7. **Игра**: титул, уровень, серия, копилка, задания, дракон — `markdown` с шаблоном

Вставить одну карточку: Дашборд → ✎ → **+ Add card** → **Manual** → вставить блок карточки.

Минимальные варианты:

```yaml
type: tile
entity: sensor.fin_dash_free
name: Свободно
color: green
vertical: true
```

```yaml
type: tile
entity: sensor.fin_dash_can_spend_today
name: Сегодня можно
color: blue
vertical: true
```

Полоски сравнивайте с `sensor.fin_dash_month_elapsed`: если лимит потрачен на 70%, а месяца
прошло 50%, вы идёте быстрее плана (в fin-dash это состояние `warn`).

## Автоматизации

Уведомление, если прогноз уходит в минус:

```yaml
alias: fin-dash — прогноз в минус
triggers:
  - trigger: state
    entity_id: binary_sensor.fin_dash_forecast_low
    to: "on"
actions:
  - action: notify.notify
    data:
      title: Деньги на счетах уйдут в минус
      message: >-
        К {{ state_attr('binary_sensor.fin_dash_forecast_low', 'min_date') }} будет
        {{ state_attr('binary_sensor.fin_dash_forecast_low', 'min') }}.
```

## Разработка

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements_test.txt
.venv/bin/pytest
```

Тесты поднимают настоящий Home Assistant (`pytest-homeassistant-custom-component`) против
записанного ответа `/api/ha` с вымышленными числами (`tests/fixture_api_ha.json`).
Форма ответа задаётся в fin-dash функцией `calc.ha_payload` — меняйте их вместе.
