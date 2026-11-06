"""DEER power outages: planned outages and incidents at your address."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import async_create_api
from .coordinator import DeerConfigEntry, DeerCoordinator, seen_store

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: DeerConfigEntry) -> bool:
    """Set up one address from a config entry."""
    coordinator = DeerCoordinator(hass, entry, await async_create_api(hass))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DeerConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: DeerConfigEntry) -> None:
    """Forget the announced outages when the address is removed."""
    await seen_store(hass, entry.entry_id).async_remove()
