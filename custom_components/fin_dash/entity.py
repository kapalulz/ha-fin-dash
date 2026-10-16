"""Common base: one "fin-dash" device, predictable entity ids (sensor.fin_dash_<key>)."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_URL, DOMAIN
from .coordinator import FinDashCoordinator


class FinDashEntity(CoordinatorEntity[FinDashCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: FinDashCoordinator, platform: str, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        # stable ids, whatever the UI language: the README cards refer to them
        self.entity_id = f"{platform}.fin_dash_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="fin-dash",
            manufacturer="fin-dash",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=entry.data[CONF_URL],
        )
