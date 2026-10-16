"""Sensors: one per number of fin-dash's /api/ha. Values are read with small functions over
the answer, so a missing block (no mortgage, no game yet) just makes that sensor unavailable."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import FinDashConfigEntry
from .const import LIMIT_GROUPS
from .coordinator import FinDashCoordinator
from .entity import FinDashEntity

Data = dict[str, Any]


def _get(data: Data, *path: str) -> Any:
    for key in path:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


@dataclass(frozen=True, kw_only=True)
class FinDashSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Data], Any]
    attrs_fn: Callable[[Data], dict[str, Any] | None] = lambda d: None
    money: bool = False  # unit = the currency fin-dash reports


def _money(key: str, *path: str, icon: str, attrs=None) -> FinDashSensorDescription:
    return FinDashSensorDescription(
        key=key,
        translation_key=key,
        icon=icon,
        money=True,
        value_fn=lambda d: _get(d, *path),
        attrs_fn=attrs or (lambda d: None),
    )


def _limit(gid: str) -> FinDashSensorDescription:
    def attrs(d: Data) -> dict[str, Any] | None:
        lim = _get(d, "limits", gid)
        if not lim:
            return None
        return {
            "name": lim["name"],
            "spent": lim["spent"],
            "limit": lim["limit"],
            "left": lim["left"],
            "status": lim["state"],  # ok | warn | full | none
            "carry": lim["carry"],
            "month_elapsed": d.get("elapsed_pct"),
        }

    return FinDashSensorDescription(
        key=f"limit_{gid}",
        translation_key=f"limit_{gid}",
        icon="mdi:gauge",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        value_fn=lambda d: _get(d, "limits", gid, "pct"),
        attrs_fn=attrs,
    )


SENSORS: tuple[FinDashSensorDescription, ...] = (
    _money("free", "money", "free", icon="mdi:cash-check",
           attrs=lambda d: {"mandatory_left": _get(d, "money", "mandatory_left")}),
    _money("can_spend_today", "today", "can_spend", icon="mdi:calendar-today",
           attrs=lambda d: {"days_left": _get(d, "today", "days_left")}),
    _money("debit", "money", "debit", icon="mdi:bank"),
    _money("credit", "money", "credit", icon="mdi:credit-card-outline"),
    _money("cushion", "money", "cushion", icon="mdi:piggy-bank-outline"),
    _money("mandatory_left", "money", "mandatory_left", icon="mdi:receipt-text-clock"),
    _money("pocket_spent", "pocket", "spent", icon="mdi:shopping",
           attrs=lambda d: {k: _get(d, "pocket", k) for k in ("monthly", "left", "pct")}),
    FinDashSensorDescription(
        key="pocket_pct", translation_key="pocket_pct", icon="mdi:shopping",
        native_unit_of_measurement=PERCENTAGE, suggested_display_precision=0,
        value_fn=lambda d: _get(d, "pocket", "pct"),
    ),
    FinDashSensorDescription(
        key="month_elapsed", translation_key="month_elapsed", icon="mdi:calendar-month",
        native_unit_of_measurement=PERCENTAGE, suggested_display_precision=0,
        value_fn=lambda d: d.get("elapsed_pct"),
    ),
    *(_limit(gid) for gid in LIMIT_GROUPS),
    _money("forecast_min", "forecast", "min", icon="mdi:chart-line",
           attrs=lambda d: {k: _get(d, "forecast", k) for k in
                            ("min_date", "end", "next_income_date", "next_income")}),
    FinDashSensorDescription(
        key="next_income_date", translation_key="next_income_date", icon="mdi:cash-plus",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda d: _date(_get(d, "forecast", "next_income_date")),
        attrs_fn=lambda d: {"amount": _get(d, "forecast", "next_income")},
    ),
    _money("next_payment", "next_payment", "amount", icon="mdi:calendar-clock",
           attrs=lambda d: d.get("next_payment") and
           {k: d["next_payment"][k] for k in ("date", "what", "type")}),
    _money("subscriptions_monthly", "subscriptions_monthly", icon="mdi:repeat"),
    _money("sinking_monthly", "sinking_monthly", icon="mdi:calendar-sync"),
    _money("mortgage_balance", "mortgage", "balance", icon="mdi:home-city-outline",
           attrs=lambda d: d.get("mortgage") and
           {k: d["mortgage"][k] for k in ("payment", "prepay_monthly", "months_saved",
                                          "remaining_months")}),
    _money("prepay_monthly", "mortgage", "prepay_monthly", icon="mdi:sword"),
    FinDashSensorDescription(
        key="warnings", translation_key="warnings", icon="mdi:alert-outline",
        value_fn=lambda d: len(d.get("warnings") or []),
        attrs_fn=lambda d: {"items": d.get("warnings") or []},
    ),
    # the game
    FinDashSensorDescription(
        key="level", translation_key="level", icon="mdi:shield-star",
        value_fn=lambda d: _get(d, "game", "level"),
        attrs_fn=lambda d: {k: _get(d, "game", k) for k in ("title", "xp", "level_pct")},
    ),
    FinDashSensorDescription(
        key="streak", translation_key="streak", icon="mdi:fire",
        native_unit_of_measurement=UnitOfTime.DAYS,
        value_fn=lambda d: _get(d, "game", "streak"),
        attrs_fn=lambda d: {"best": _get(d, "game", "best_streak")},
    ),
    _money("piggy", "game", "piggy", icon="mdi:treasure-chest"),
    FinDashSensorDescription(
        key="quests_done", translation_key="quests_done", icon="mdi:sword-cross",
        value_fn=lambda d: _get(d, "game", "quests_done"),
        attrs_fn=lambda d: {"total": len(_get(d, "game", "quests") or []),
                            "quests": _get(d, "game", "quests") or []},
    ),
    FinDashSensorDescription(
        key="achievements", translation_key="achievements", icon="mdi:trophy",
        value_fn=lambda d: _get(d, "game", "achievements"),
        attrs_fn=lambda d: {"total": _get(d, "game", "achievements_total")},
    ),
    FinDashSensorDescription(
        key="dragon_hp", translation_key="dragon_hp", icon="mdi:fire-circle",
        native_unit_of_measurement=PERCENTAGE, suggested_display_precision=1,
        value_fn=lambda d: _get(d, "game", "dragon", "pct"),
        attrs_fn=lambda d: _get(d, "game", "dragon") and
        {k: d["game"]["dragon"][k] for k in ("hp", "max_hp")},
    ),
)  # fmt: skip


async def async_setup_entry(
    hass: HomeAssistant, entry: FinDashConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(FinDashSensor(coordinator, d) for d in SENSORS)


class FinDashSensor(FinDashEntity, SensorEntity):
    entity_description: FinDashSensorDescription

    def __init__(self, coordinator: FinDashCoordinator, description: FinDashSensorDescription):
        super().__init__(coordinator, "sensor", description.key)
        self.entity_description = description
        if description.money:
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_suggested_display_precision = 0

    @property
    def native_unit_of_measurement(self) -> str | None:
        if self.entity_description.money:
            return (self.coordinator.data or {}).get("currency") or "USD"
        return self.entity_description.native_unit_of_measurement

    @property
    def available(self) -> bool:
        return super().available and self.native_value is not None

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return self.entity_description.attrs_fn(self.coordinator.data or {}) or None
