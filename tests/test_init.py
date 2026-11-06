"""Tests for the entities, the timers and the new outage event."""

from __future__ import annotations

from datetime import datetime

from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.deer_outages.const import EVENT_NEW_OUTAGE, SCAN_INTERVAL

from .conftest import INCIDENTS_URL, SCHEDULED_URL, load



def _at(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(
        tzinfo=dt_util.get_time_zone("Europe/Bucharest")
    )


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await hass.config.async_set_time_zone("Europe/Bucharest")
    hass.config.language = "hu"
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_entities(
    hass: HomeAssistant,
    feed: AiohttpClientMocker,
    entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """At noon the street has a planned outage and an incident going on."""
    freezer.move_to(_at("2026-11-06 12:00"))
    await _setup(hass, entry)
    assert entry.state is ConfigEntryState.LOADED
    ids = sorted(hass.states.async_entity_ids())
    now_id = next(i for i in ids if i.startswith("binary_sensor."))
    next_id = next(i for i in ids if i.startswith("sensor."))
    cal_id = next(i for i in ids if i.startswith("calendar."))

    state = hass.states.get(now_id)
    assert state.state == "on"
    assert len(state.attributes["outages"]) == 2
    assert state.attributes["message"].startswith("Tervezett áramszünet 11.06. 10:00–14:00")

    state = hass.states.get(next_id)
    assert dt_util.parse_datetime(state.state) == _at("2026-11-06 10:00")
    assert state.attributes["count"] == 3
    assert state.attributes["addresses"] == ["TARGU SECUIESC, Strada GABOR ARON"]

    result = await hass.services.async_call(
        "calendar",
        "get_events",
        {"start_date_time": "2026-11-06 00:00:00", "end_date_time": "2026-11-20 00:00:00"},
        target={"entity_id": cal_id},
        blocking=True,
        return_response=True,
    )
    events = result[cal_id]["events"]
    assert [e["summary"] for e in events] == [
        "⚡ Áramszünet",
        "⚡ Üzemzavar (vége még nem ismert)",
        "⚡ Áramszünet",
    ]
    assert "teljes település" in events[2]["description"]

    # The incident gets 2 hours (until 13:30), the planned one ends at 14:00.
    freezer.move_to(_at("2026-11-06 14:00:01"))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get(now_id).state == "off"
    assert dt_util.parse_datetime(hass.states.get(next_id).state) == _at("2026-11-12 08:00")


async def test_new_outage_event(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Only outages that show up after the first fetch are announced."""
    freezer.move_to(_at("2026-11-05 12:00"))
    scheduled = load("scheduled.json")
    aioclient_mock.get(SCHEDULED_URL, json=scheduled[:5])
    aioclient_mock.get(INCIDENTS_URL, json=[])
    events = async_capture_events(hass, EVENT_NEW_OUTAGE)
    await _setup(hass, entry)
    assert events == []

    aioclient_mock.clear_requests()
    aioclient_mock.get(SCHEDULED_URL, json=scheduled)
    aioclient_mock.get(INCIDENTS_URL, json=load("incidents.json"))
    freezer.tick(SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert sorted(e.data["id"] for e in events) == ["50003", "70001"]
    zone = next(e.data for e in events if e.data["id"] == "50003")
    assert zone["area_only"] is True
    assert zone["message"] == (
        "Tervezett áramszünet 11.12. 08:00–12:00: TARGU SECUIESC, ZONA PT 7 FABRICII"
    )


async def test_feed_down(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry
) -> None:
    """Setup is retried while the feed cannot be reached."""
    aioclient_mock.get(SCHEDULED_URL, status=500)
    await _setup(hass, entry)
    assert entry.state is ConfigEntryState.SETUP_RETRY
