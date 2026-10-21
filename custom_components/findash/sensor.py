"""Money flow sensor; attributes contain both views for the card."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            MoneyFlowSensor(entry.runtime_data, entry),
            *(
                OverviewSensor(entry.runtime_data, entry, key, name, icon)
                for key, name, icon in OVERVIEW
            ),
            *(BlockSensor(entry.runtime_data, entry, *block) for block in BLOCKS),
        ]
    )


class MoneyFlowSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Money flow"
    _attr_icon = "mdi:cash-multiple"
    _attr_native_unit_of_measurement = "USD"
    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_money_flow"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Findash",
            "manufacturer": "Findash",
            "model": "Money flow",
        }

    @property
    def native_value(self):
        return self.coordinator.data["flow"]["now"]["rest"]

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {key: data[key] for key in ("flow", "month", "generated_at", "currency")}


OVERVIEW = (
    ("debit", "Debit", "mdi:bank"),
    ("credit", "Credit", "mdi:credit-card-outline"),
    ("cushion", "Cushion", "mdi:piggy-bank-outline"),
    ("free", "Free", "mdi:cash-check"),
)


class OverviewSensor(CoordinatorEntity, SensorEntity):
    """A current monetary total; no sum statistics for fluctuating balances."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "USD"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator, entry, key, name, icon):
        super().__init__(coordinator)
        self.key = key
        self.instance = entry.entry_id
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Findash",
            "manufacturer": "Findash",
            "model": "Money flow",
        }

    @property
    def available(self):
        return super().available and self.key in self.coordinator.data.get("overview", {})

    @property
    def native_value(self):
        return self.coordinator.data.get("overview", {}).get(self.key)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        attrs = {
            "findash_metric": self.key,
            "findash_instance": self.instance,
            "generated_at": data["generated_at"],
        }
        if self.key == "free":
            attrs["mandatory_left"] = data.get("overview", {}).get("mandatory_left")
        return attrs


def _full_limits(block):
    return sum(1 for b in block if b.get("state") == "full")


# key, name, icon, block in the answer, state from the block, unit (None = no unit)
BLOCKS = (
    ("today", "Today", "mdi:calendar-today", "today", lambda b: b["can_spend"], "USD"),
    ("limits", "Limits", "mdi:gauge", "limits", _full_limits, None),
    ("forecast", "Forecast", "mdi:chart-line", "forecast", lambda b: b["min"]["balance"], "USD"),
    ("game", "Game", "mdi:shield-star", "game", lambda b: b["level"], None),
)


class BlockSensor(CoordinatorEntity, SensorEntity):
    """One card's data: a headline number as the state, the whole block as `data`.
    Unavailable when the Findash server is older than the block."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, name, icon, block, value, unit):
        super().__init__(coordinator)
        self.key, self.block, self.value = key, block, value
        self.instance = entry.entry_id
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        if unit:
            self._attr_native_unit_of_measurement = unit
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_suggested_display_precision = 0
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Findash",
            "manufacturer": "Findash",
            "model": "Money flow",
        }

    @property
    def available(self):
        return super().available and self.block in self.coordinator.data

    @property
    def native_value(self):
        block = self.coordinator.data.get(self.block)
        return None if block is None else self.value(block)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "findash_metric": self.key,
            "findash_instance": self.instance,
            "generated_at": data["generated_at"],
            "data": data.get(self.block),
        }
