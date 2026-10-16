"""Problems to automate on: the forecast goes below zero, a limit is used up."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import FinDashConfigEntry
from .coordinator import FinDashCoordinator
from .entity import FinDashEntity

Data = dict[str, Any]


def _full_limits(d: Data) -> list[str]:
    return [v["name"] for v in (d.get("limits") or {}).values() if v.get("state") == "full"]


@dataclass(frozen=True, kw_only=True)
class FinDashBinaryDescription(BinarySensorEntityDescription):
    is_on_fn: Callable[[Data], bool | None]
    attrs_fn: Callable[[Data], dict[str, Any] | None] = lambda d: None


BINARY_SENSORS = (
    FinDashBinaryDescription(
        key="forecast_low",
        translation_key="forecast_low",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: (d.get("forecast") or {}).get("low"),
        attrs_fn=lambda d: {
            "min": (d.get("forecast") or {}).get("min"),
            "min_date": (d.get("forecast") or {}).get("min_date"),
        },
    ),
    FinDashBinaryDescription(
        key="limit_full",
        translation_key="limit_full",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: bool(_full_limits(d)),
        attrs_fn=lambda d: {"limits": _full_limits(d)},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: FinDashConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(FinDashBinary(entry.runtime_data, d) for d in BINARY_SENSORS)


class FinDashBinary(FinDashEntity, BinarySensorEntity):
    entity_description: FinDashBinaryDescription

    def __init__(self, coordinator: FinDashCoordinator, description: FinDashBinaryDescription):
        super().__init__(coordinator, "binary_sensor", description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.is_on_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return self.entity_description.attrs_fn(self.coordinator.data or {})
