"""Diagnostics support for the DEER integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_LOCALITY, CONF_STREETS
from .coordinator import DeerConfigEntry

# The address is personal; it is left out of files that users post in issues.
TO_REDACT = {CONF_LOCALITY, CONF_STREETS, "title", "unique_id", "addresses", "locality", "streets"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: DeerConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for one configured address."""
    coordinator = entry.runtime_data
    data = {
        "entry": entry.as_dict(),
        "region": coordinator.region,
        "county": coordinator.county,
        "locality": coordinator.locality,
        "streets": coordinator.streets,
        "last_update_success": coordinator.last_update_success,
        "stale": coordinator.stale,
        "has_usable_data": coordinator.has_usable_data,
        "seen_count": coordinator.seen_count,
        "outages": [match.as_dict() for match in coordinator.data or []],
    }
    return async_redact_data(data, TO_REDACT)
