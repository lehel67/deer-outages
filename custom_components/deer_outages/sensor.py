"""Sensors for the DEER integration."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DeerConfigEntry, outage_text
from .entity import DeerEntity
from .outages import TYPE_INCIDENT, TYPE_PLANNED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DeerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors."""
    async_add_entities(
        [
            DeerNextOutageSensor(entry.runtime_data),
            DeerUpcomingCountSensor(entry.runtime_data),
        ]
    )


class DeerNextOutageSensor(DeerEntity, SensorEntity):
    """When the next (or the current) outage at the address starts."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:transmission-tower-off"
    # The list changes often and is of no use in the history database.
    _unrecorded_attributes = frozenset({"outages"})

    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "next_outage")

    @property
    def native_value(self) -> datetime | None:
        """Return the start of the first outage that is not over."""
        upcoming = self.coordinator.upcoming()
        return upcoming[0].outage.start if upcoming else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the details of the next outage and the full list."""
        upcoming = self.coordinator.upcoming()
        attributes: dict[str, Any] = {
            "count": len(upcoming),
            "outages": [match.as_dict() for match in upcoming],
            **self._common_attributes,
        }
        if upcoming:
            first = upcoming[0]
            attributes.update(
                {
                    "end": first.outage.end.isoformat(),
                    "type": first.outage.kind,
                    "addresses": [place.text for place in first.places],
                    "message": outage_text(first, self.hass.config.language),
                }
            )
        return attributes


class DeerUpcomingCountSensor(DeerEntity, SensorEntity):
    """How many outages at the address are going on or still to come; 0 if none."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "upcoming_outages")

    @property
    def native_value(self) -> int:
        """Return the number of outages that are not over."""
        return len(self.coordinator.upcoming())

    @property
    def icon(self) -> str:
        """Show a crossed tower while there is anything to know about."""
        return "mdi:transmission-tower-off" if self.native_value else "mdi:transmission-tower"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the split between planned outages and incidents."""
        upcoming = self.coordinator.upcoming()
        return {
            "planned": sum(1 for m in upcoming if m.outage.kind == TYPE_PLANNED),
            "incidents": sum(1 for m in upcoming if m.outage.kind == TYPE_INCIDENT),
            "now": len(self.coordinator.current()),
            **self._common_attributes,
        }
