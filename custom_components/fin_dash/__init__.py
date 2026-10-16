"""fin-dash: personal finance numbers as Home Assistant sensors."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import FinDashCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

type FinDashConfigEntry = ConfigEntry[FinDashCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: FinDashConfigEntry) -> bool:
    coordinator = FinDashCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload_on_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FinDashConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _reload_on_options(hass: HomeAssistant, entry: FinDashConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
