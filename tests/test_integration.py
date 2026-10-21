"""The findash integration inside a real Home Assistant, against a recorded answer of
/api/home-assistant/money-flow (fictional numbers). See ../README.md → Проверка."""

import json
from pathlib import Path

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

import custom_components.findash  # noqa: F401  (load ours before the test config dir)

URL = "https://fin.example.test"
API = URL + "/api/home-assistant/money-flow"
DATA = {"url": URL, "token": "t"}


@pytest.fixture
def payload():
    return json.loads((Path(__file__).parent / "fixture_money_flow.json").read_text())


async def test_flow_and_sensors(hass, aioclient_mock, payload):
    aioclient_mock.get(API, json=payload)
    r = await hass.config_entries.flow.async_init(
        "findash", context={"source": config_entries.SOURCE_USER}
    )
    r = await hass.config_entries.flow.async_configure(r["flow_id"], {**DATA, "cf_client_id": ""})
    assert r["type"] is FlowResultType.CREATE_ENTRY, r
    await hass.async_block_till_done()
    states = {s.entity_id: s for s in hass.states.async_all("sensor")}
    print(sorted(states))
    flow = next(s for s in states.values() if "flow" in s.attributes)
    assert float(flow.state) == payload["flow"]["now"]["rest"]
    metrics = {s.attributes.get("findash_metric"): s for s in states.values()}
    for k in ("debit", "credit", "cushion", "free"):
        assert float(metrics[k].state) == payload["overview"][k], k


async def test_errors(hass, aioclient_mock):
    for kw, err in (
        ({"status": 401}, "invalid_auth"),
        ({"status": 302}, "invalid_auth"),
        ({"status": 500}, "cannot_connect"),
        ({"json": {"x": 1}}, "invalid_data"),
    ):
        aioclient_mock.clear_requests()
        aioclient_mock.get(API, **kw)
        r = await hass.config_entries.flow.async_init(
            "findash", context={"source": config_entries.SOURCE_USER}
        )
        r = await hass.config_entries.flow.async_configure(r["flow_id"], DATA)
        assert r.get("errors") == {"base": err}, (kw, r)
        hass.config_entries.flow.async_abort(r["flow_id"])


async def test_reauth(hass, aioclient_mock, payload):
    aioclient_mock.get(API, status=401)
    e = MockConfigEntry(domain="findash", data=DATA, unique_id=URL)
    e.add_to_hass(hass)
    await hass.config_entries.async_setup(e.entry_id)
    await hass.async_block_till_done()
    assert e.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress()
    assert [f["context"]["source"] for f in flows] == ["reauth"]
    aioclient_mock.clear_requests()
    aioclient_mock.get(API, json=payload)
    r = await hass.config_entries.flow.async_configure(
        flows[0]["flow_id"], {**DATA, "token": "new"}
    )
    assert r["type"] is FlowResultType.ABORT and r["reason"] == "reauth_successful", r


async def test_card_blocks(hass, aioclient_mock, payload):
    aioclient_mock.get(API, json=payload)
    e = MockConfigEntry(domain="findash", data=DATA, unique_id=URL)
    e.add_to_hass(hass)
    assert await hass.config_entries.async_setup(e.entry_id)
    await hass.async_block_till_done()
    by = {s.attributes.get("findash_metric"): s for s in hass.states.async_all("sensor")}
    assert float(by["today"].state) == payload["today"]["can_spend"]
    assert by["limits"].attributes["data"] == payload["limits"]
    assert float(by["forecast"].state) == payload["forecast"]["min"]["balance"]
    assert int(by["game"].state) == payload["game"]["level"]


async def test_old_server_keeps_working(hass, aioclient_mock, payload):
    for k in ("today", "limits", "forecast", "game"):
        payload.pop(k)
    aioclient_mock.get(API, json=payload)
    e = MockConfigEntry(domain="findash", data=DATA, unique_id=URL)
    e.add_to_hass(hass)
    assert await hass.config_entries.async_setup(e.entry_id)
    await hass.async_block_till_done()
    by = {s.attributes.get("findash_metric"): s for s in hass.states.async_all("sensor")}
    assert hass.states.get("sensor.findash_today").state == "unavailable"
    assert by["free"].state != "unavailable"


async def test_cards_are_served_and_loaded_automatically(
    hass, hass_client, aioclient_mock, payload
):
    from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, "http", {})
    aioclient_mock.get(API, json=payload)
    e = MockConfigEntry(domain="findash", data=DATA, unique_id=URL)
    e.add_to_hass(hass)
    assert await hass.config_entries.async_setup(e.entry_id)
    await hass.async_block_till_done()

    urls = [u for u in hass.data[DATA_EXTRA_MODULE_URL].urls if "findash-cards.js" in u]
    client = await hass_client()
    resp = await client.get("/findash/findash-cards.js")

    assert urls == ["/findash/findash-cards.js?v=0.4.0"]
    assert resp.status == 200 and "findash-limits-card" in await resp.text()
