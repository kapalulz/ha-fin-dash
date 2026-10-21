"""Set up Findash."""

import logging
from datetime import timedelta
from pathlib import Path

import aiohttp
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.loader import async_get_integration

from .api import InvalidAuth, fetch
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]
CARDS_URL = "/findash/findash-cards.js"
CARDS_FILE = Path(__file__).parent / "frontend" / "findash-cards.js"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)  # set up from the UI only


async def async_setup(hass, config):
    """Serve the dashboard cards and load them on every dashboard: no manual resource.
    The version in the URL makes browsers fetch a new file after an update."""
    version = hass.data.setdefault(DOMAIN, {}).get("version")
    if version is None:
        version = str((await async_get_integration(hass, DOMAIN)).version)
        hass.data[DOMAIN]["version"] = version
        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARDS_URL, str(CARDS_FILE), cache_headers=False)]
        )
        add_extra_js_url(hass, f"{CARDS_URL}?v={version}")
    return True


async def async_setup_entry(hass, entry):
    async def update():
        try:
            return await fetch(async_get_clientsession(hass), entry.data)
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed("Check Findash and Cloudflare credentials") from err
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed("Cannot read Findash money flow") from err

    coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name="Findash",
        config_entry=entry,
        update_method=update,
        update_interval=timedelta(minutes=5),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
