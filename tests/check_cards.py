"""Browser checks of findash-cards.js (Today, Limits, Forecast, Game) with fictional numbers.
Run directly: python tests/check_cards.py (needs `pip install playwright` and a Chromium)
Screenshots go to /tmp/findash-cards-*.png."""

# ruff: noqa: E501
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
DATA = {
    "today": {"can_spend": 12.4, "days_left": 16, "elapsed": 0.516,
              "pocket": {"monthly": 150, "spent": 96, "left": 54}, "piggy": 41.5},
    "limits": [
        {"id": "pocket", "name": "Карманные", "spent": 96, "limit": 150, "pct": 0.64, "state": "warn", "carry": 0},
        {"id": "food", "name": "Продукты", "spent": 321, "limit": 640, "pct": 0.502, "state": "ok", "carry": 40},
        {"id": "eating_out", "name": "Кафе и рестораны", "spent": 130, "limit": 120, "pct": 1.083, "state": "full", "carry": -15},
        {"id": "shopping", "name": "Шопинг", "spent": 20, "limit": 0, "pct": 0, "state": "none", "carry": 0},
    ],
    "forecast": {"start": 3200, "end": 5100, "low": False, "min": {"date": "2026-10-29", "balance": 2900},
                 "points": [3200 - i * 20 + (2100 if i >= 14 else 0) for i in range(31)], "first_date": "2026-10-16",
                 "next_income": {"date": "2026-10-30", "amount": 2100},
                 "next_payment": {"date": "2026-11-01", "what": "Ипотека", "amount": 1500, "type": "mortgage"}},
    "game": {"level": 24, "title": "Рыцарь бюджета", "xp": 15000, "level_xp": 300, "level_need": 675, "streak": 12,
             "best_streak": 30, "piggy": 41.5,
             "quests": [{"name": "Уложиться в 5 на карманные", "done": True, "xp": 70},
                        {"name": "Обойти таверны стороной", "done": False, "xp": 25}],
             "achievements": [{"name": "Первый поход", "rarity": "common", "earned": True},
                              {"name": "Железная воля", "rarity": "epic", "earned": True},
                              {"name": "Аскет", "rarity": "rare", "earned": False}],
             "boss": {"name": "Дракон ипотеки", "hp": 209694, "max_hp": 240000, "pct": 0.874, "hits": 2}},
}  # fmt: skip
THEMES = {
    "light": "body{background:#f4f5f6;--primary-text-color:#20242a;--secondary-text-color:#69717d;--primary-color:#346d99;--divider-color:#dce0e5;--secondary-background-color:#eef0f3}ha-card{background:#fff;border-radius:16px}",
    "dark": "body{background:#151b24;--primary-text-color:#e9edf4;--secondary-text-color:#9ca8b8;--primary-color:#63b6a4;--divider-color:#3c4858;--secondary-background-color:#2a3442;--error-color:#f28b82}ha-card{background:#202937;border-radius:16px}",
}
CARDS = ["today", "limits", "forecast", "game"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    errors = []
    for theme, width in (("light", 390), ("dark", 1000)):
        page = browser.new_page(viewport={"width": width, "height": 900})
        errors.clear()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content(
            f"<style>{THEMES[theme]} body{{margin:12px;display:grid;gap:12px}}</style>"
        )
        page.add_script_tag(path=str(root / "custom_components/findash/frontend/findash-cards.js"))
        page.evaluate(
            """([data, cards]) => {
              window.ha = {language: 'ru', states: {}};
              for (const key of cards) ha.states['sensor.findash_' + key] = {state: '1', attributes: {findash_metric: key, data: data[key]}};
              window.made = {};
              for (const key of cards) {
                const card = document.createElement(`findash-${key}-card`);
                card.setConfig({}); card.hass = ha;
                card.addEventListener('hass-more-info', e => window.tapped = e.detail.entityId);
                document.body.append(card); made[key] = card;
              }
            }""",
            [DATA, CARDS],
        )
        text = page.evaluate("Object.values(made).map(c => c.shadowRoot.textContent).join('|')")
        for needle in ("Можно потратить сегодня", "Хватит в этом месяце", "перенос +40", "Минимум на счетах",
                       "Ипотека", "Рыцарь бюджета", "Дракон ипотеки", "Достижения · 2 / 3"):  # fmt: skip
            assert needle in text, needle
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
            "horizontal scroll"
        )
        page.screenshot(path=f"/tmp/findash-cards-{theme}.png", full_page=True)
        assert not errors, errors
    # taps, missing / ambiguous / unavailable sensors, a negative forecast, XSS-safe text, editor
    page.evaluate("made.today.shadowRoot.querySelector('button').click()")
    assert page.evaluate("tapped === 'sensor.findash_today'")
    page.evaluate(
        "made.forecast.hass = {...ha, states: {...ha.states, 'sensor.findash_forecast': {state: '1', attributes: {findash_metric: 'forecast', data: {...ha.states['sensor.findash_forecast'].attributes.data, low: true, min: {date: '2026-10-29', balance: -150}}}}}}"
    )
    assert "Уйдёт в минус" in page.evaluate("made.forecast.shadowRoot.textContent")
    page.evaluate(
        "made.game.hass = {...ha, states: {...ha.states, 'sensor.findash_game': {state: 'unavailable', attributes: {findash_metric: 'game'}}}}"
    )
    assert "Findash недоступен" in page.evaluate("made.game.shadowRoot.textContent")
    page.evaluate(
        "made.limits.hass = {...ha, states: {...ha.states, 'sensor.other': ha.states['sensor.findash_limits']}}"
    )
    assert "Несколько датчиков" in page.evaluate("made.limits.shadowRoot.textContent")
    page.evaluate("made.today.setConfig({entity: 'sensor.missing'}); made.today.hass = ha")
    assert "Датчик не найден: sensor.missing" in page.evaluate("made.today.shadowRoot.textContent")
    page.evaluate(
        "made.today.setConfig({language: 'en', title: '<img src=x onerror=alert(1)>'}); made.today.hass = ha"
    )
    assert page.evaluate("made.today.shadowRoot.querySelectorAll('img').length === 0")
    assert "You can spend today" in page.evaluate("made.today.shadowRoot.textContent")

    # flexible: every block can go, lists choose what and in which order
    def text(key):
        return page.evaluate(f"made.{key}.shadowRoot.textContent")

    page.evaluate(
        "made.today.setConfig({show_pocket: false, show_piggy: false, show_title: false}); made.today.hass = ha"
    )
    assert "Карманные" not in text("today") and "В копилке" not in text("today")
    assert "Можно потратить сегодня" in text("today") and not page.evaluate(
        "made.today.shadowRoot.querySelector('h2')"
    )
    page.evaluate(
        "made.limits.setConfig({limits: ['eating_out', 'food'], show_carry: false}); made.limits.hass = ha"
    )
    names = page.evaluate(
        "[...made.limits.shadowRoot.querySelectorAll('.lim .row > span')].map(e => e.firstChild.textContent)"
    )
    assert names == ["Кафе и рестораны", "Продукты"], names
    assert "перенос" not in text("limits")
    page.evaluate(
        "made.limits.setConfig({only_problems: true, show_bars: false}); made.limits.hass = ha"
    )
    assert page.evaluate(
        "made.limits.shadowRoot.querySelectorAll('.lim').length === 2 && !made.limits.shadowRoot.querySelector('.track')"
    )
    page.evaluate(
        "made.forecast.setConfig({days: 7, show_chart: false, show_payment: false}); made.forecast.hass = ha"
    )
    assert "Прогноз · 7 дн." in text("forecast") and "Ближайший платёж" not in text("forecast")
    assert page.evaluate("!made.forecast.shadowRoot.querySelector('svg')")
    page.evaluate(
        "made.game.setConfig({show_quests: false, show_boss: false, show_locked: true}); made.game.hass = ha"
    )
    assert (
        "Задания" not in text("game") and "ипотеки" not in text("game") and "Аскет" in text("game")
    )
    page.evaluate("""() => {
      const card = document.createElement('findash-overview-card');
      card.setConfig({tiles: ['free', 'debit']});
      for (const key of ['debit', 'credit', 'cushion', 'free']) ha.states['sensor.findash_' + key] = {state: '100', attributes: {findash_metric: key, unit_of_measurement: 'USD'}};
      card.hass = {...ha}; document.body.append(card); made.overview = card;
    }""")
    labels = page.evaluate(
        "[...made.overview.shadowRoot.querySelectorAll('.tile .label')].map(e => e.textContent)"
    )
    assert labels == ["Свободно", "Дебит"], labels
    # the visual editor: a checkbox per block and per bar; other keys are kept
    page.evaluate("""() => {
      window.editor = customElements.get('findash-limits-card').getConfigElement();
      editor.hass = ha;
      editor.setConfig({type: 'custom:findash-limits-card', grid_options: {columns: 12}});
      editor.addEventListener('config-changed', e => window.changed = e.detail.config);
      document.body.append(editor);
    }""")
    page.get_by_label("Перенос с прошлого месяца", exact=True).uncheck()
    assert page.evaluate("changed.show_carry === false && changed.grid_options.columns === 12")
    page.get_by_label("Карманные", exact=True).uncheck()
    assert page.evaluate(
        "JSON.stringify(changed.limits) === JSON.stringify(['food', 'eating_out', 'shopping'])"
    )
    page.get_by_label("Перенос с прошлого месяца", exact=True).check()
    assert page.evaluate("!('show_carry' in changed)")
    assert page.evaluate(
        "window.customCards.filter(c => c.type.startsWith('findash-')).length === 6"
    )
    assert not errors, errors
    browser.close()
print(
    "Cards checks passed: 4 new cards, light/dark, phone/desktop, taps, errors, negative forecast, safe title, hidden blocks, chosen bars/tiles and order, 7-day window, editor checkboxes."
)
print(json.dumps({"screenshots": [f"/tmp/findash-cards-{t}.png" for t in THEMES]}))
