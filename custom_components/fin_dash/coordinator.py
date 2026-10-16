"""Polls fin-dash every few minutes; every entity reads from the same answer."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CloudflareBlocked, FinDashClient, FinDashError, InvalidAuth
from .const import (
    CONF_CF_CLIENT_ID,
    CONF_CF_CLIENT_SECRET,
    CONF_SCAN_MINUTES,
    CONF_TOKEN,
    CONF_URL,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_MINUTES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class FinDashCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        minutes = entry.options.get(CONF_SCAN_MINUTES, DEFAULT_SCAN_MINUTES)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(minutes=minutes),
        )
        verify = entry.data.get(CONF_VERIFY_SSL, True)
        self.client = FinDashClient(
            async_get_clientsession(hass, verify_ssl=verify),
            entry.data[CONF_URL],
            entry.data[CONF_TOKEN],
            entry.data.get(CONF_CF_CLIENT_ID),
            entry.data.get(CONF_CF_CLIENT_SECRET),
            verify,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.fetch()
        except (InvalidAuth, CloudflareBlocked) as err:
            raise ConfigEntryAuthFailed(str(err)) from err  # HA offers to re-enter the token
        except FinDashError as err:
            raise UpdateFailed(f"fin-dash: {err}") from err
