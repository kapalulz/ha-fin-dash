"""Fixtures: the integration enabled, and a real /api/ha answer (fictional numbers)."""

import json
from pathlib import Path

import pytest

URL = "https://fin.example.test"
API = f"{URL}/api/ha"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def payload() -> dict:
    return json.loads((Path(__file__).parent / "fixture_api_ha.json").read_text())
