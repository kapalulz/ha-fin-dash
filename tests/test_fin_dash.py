"""Config flow, sensors and error handling against a mocked fin-dash."""

import aiohttp
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.fin_dash.const import DOMAIN

from .conftest import API, URL

DATA = {"url": URL, "token": "ha-secret", "verify_ssl": True}


async def start_flow(hass, data=DATA):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return await hass.config_entries.flow.async_configure(result["flow_id"], data)


async def test_flow_creates_entry_and_sends_the_token(hass, aioclient_mock, payload):
    aioclient_mock.get(API, json=payload)

    result = await start_flow(hass, {**DATA, "url": URL + "/"})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["url"] == URL  # trailing slash dropped
    headers = aioclient_mock.mock_calls[0][3]
    assert headers["Authorization"] == "Bearer ha-secret"
    assert "CF-Access-Client-Id" not in headers


async def test_flow_explains_each_failure(hass, aioclient_mock):
    cases = [
        ({"status": 401}, "invalid_auth"),
        ({"status": 302}, "cloudflare"),
        ({"status": 403}, "cloudflare"),
        ({"status": 404}, "endpoint_off"),
        ({"text": "<html>login</html>"}, "cannot_connect"),
        ({"exc": aiohttp.ClientConnectionError()}, "cannot_connect"),
    ]
    for kwargs, error in cases:
        aioclient_mock.clear_requests()
        aioclient_mock.get(API, **kwargs)

        result = await start_flow(hass)

        assert result["type"] is FlowResultType.FORM, error
        assert result["errors"] == {"base": error}
        hass.config_entries.flow.async_abort(result["flow_id"])  # one open flow per address


async def test_cloudflare_service_token_is_sent(hass, aioclient_mock, payload):
    aioclient_mock.get(API, json=payload)

    await start_flow(hass, {**DATA, "cf_client_id": "id.access", "cf_client_secret": "s3cret"})

    headers = aioclient_mock.mock_calls[0][3]
    assert headers["CF-Access-Client-Id"] == "id.access"
    assert headers["CF-Access-Client-Secret"] == "s3cret"


async def setup(hass, aioclient_mock, payload):
    aioclient_mock.get(API, json=payload)
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=URL)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_sensors_mirror_fin_dash(hass, aioclient_mock, payload):
    await setup(hass, aioclient_mock, payload)

    free = hass.states.get("sensor.fin_dash_free")
    today = hass.states.get("sensor.fin_dash_can_spend_today")
    fun = hass.states.get("sensor.fin_dash_limit_fun")
    quests = hass.states.get("sensor.fin_dash_quests_done")

    assert float(free.state) == payload["money"]["free"]
    assert free.attributes["unit_of_measurement"] == "USD"
    assert float(today.state) == payload["today"]["can_spend"]
    assert today.attributes["days_left"] == payload["today"]["days_left"]
    assert float(fun.state) == payload["limits"]["fun"]["pct"]
    assert fun.attributes["status"] == "full" and fun.attributes["name"] == "Развлечения"
    assert quests.attributes["total"] == len(payload["game"]["quests"])
    assert hass.states.get("binary_sensor.fin_dash_limit_full").state == "on"
    assert hass.states.get("binary_sensor.fin_dash_forecast_low").state == "off"
    # a group fin-dash has no bar for (no limit, no spending) is unavailable, not zero
    assert hass.states.get("sensor.fin_dash_limit_home").state == "unavailable"
    assert hass.states.get("sensor.fin_dash_next_income_date").state == "2026-10-30"


async def test_missing_mortgage_makes_its_sensors_unavailable(hass, aioclient_mock, payload):
    payload["mortgage"] = None
    payload["game"]["dragon"] = None

    await setup(hass, aioclient_mock, payload)

    assert hass.states.get("sensor.fin_dash_mortgage_balance").state == "unavailable"
    assert hass.states.get("sensor.fin_dash_dragon_hp").state == "unavailable"
    assert hass.states.get("sensor.fin_dash_free").state != "unavailable"


async def test_refused_token_asks_to_reauthenticate(hass, aioclient_mock):
    aioclient_mock.get(API, status=401)
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=URL)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress()
    assert [f["context"]["source"] for f in flows] == ["reauth"]


async def test_options_change_the_poll_interval(hass, aioclient_mock, payload):
    entry = await setup(hass, aioclient_mock, payload)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"scan_minutes": 30}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.runtime_data.update_interval.total_seconds() == 30 * 60


async def test_example_cards_refer_to_real_entities_and_the_game_card_renders(
    hass, aioclient_mock, payload
):
    from pathlib import Path

    import yaml
    from homeassistant.helpers.template import Template

    await setup(hass, aioclient_mock, payload)
    view = yaml.safe_load(
        (Path(__file__).parent.parent / "examples" / "dashboard.yaml").read_text()
    )["views"][0]

    def entities(card):
        for key in ("entity",):
            if key in card:
                yield card[key]
        for sub in card.get("cards", []) + card.get("entities", []):
            yield from entities(sub if isinstance(sub, dict) else {"entity": sub})

    used = {e for card in view["cards"] for e in entities(card)}
    assert used and all(hass.states.get(e) is not None for e in used), used
    game = next(c for c in view["cards"] if c["type"] == "markdown")
    text = Template(game["content"], hass).async_render(parse_result=False)
    assert payload["game"]["title"] in text and "Задания на сегодня" in text
    assert "Дракон ипотеки" in text
