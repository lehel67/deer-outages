"""Texts for notifications and calendar events, in the Home Assistant language."""

from __future__ import annotations

TEXTS: dict[str, dict[str, str]] = {
    "hu": {
        "planned": "Tervezett áramszünet",
        "incident": "Üzemzavar",
        "calendar_planned": "⚡ Áramszünet",
        "calendar_incident": "⚡ Üzemzavar",
        "end_unknown": "vége még nem ismert",
        "from": "{start}-tól",
        "area": "A teljes település vagy körzet érintett lehet.",
        "duration": "Időtartam: {duration}",
        "date": "%m.%d.",
    },
    "ro": {
        "planned": "Întrerupere programată",
        "incident": "Incident",
        "calendar_planned": "⚡ Întrerupere curent",
        "calendar_incident": "⚡ Incident",
        "end_unknown": "sfârșit încă necunoscut",
        "from": "de la {start}",
        "area": "Poate fi afectată întreaga localitate sau zonă.",
        "duration": "Durată: {duration}",
        "date": "%d.%m.",
    },
    "en": {
        "planned": "Planned power outage",
        "incident": "Incident",
        "calendar_planned": "⚡ Power outage",
        "calendar_incident": "⚡ Incident",
        "end_unknown": "end not known yet",
        "from": "from {start}",
        "area": "The whole locality or zone may be affected.",
        "duration": "Duration: {duration}",
        "date": "%d/%m",
    },
}


def texts(language: str | None) -> dict[str, str]:
    """Return the texts of a Home Assistant language, English if not known."""
    return TEXTS.get((language or "en").split("-")[0], TEXTS["en"])
