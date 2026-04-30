"""Constants for AccuWeather (HACS) integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_EXCEPTIONAL,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
)

API_METRIC = "Metric"
ATTRIBUTION = "Data provided by AccuWeather"
ATTR_CATEGORY_VALUE = "CategoryValue"
ATTR_DIRECTION = "Direction"
ATTR_ENGLISH = "English"
ATTR_LEVEL = "level"
ATTR_SPEED = "Speed"
ATTR_VALUE = "Value"
DOMAIN = "accuweather_hacs"
MAX_FORECAST_DAYS = 4

AIR_QUALITY_CATEGORY_MAP = {
    1: "good",
    2: "moderate",
    3: "unhealthy",
    4: "very_unhealthy",
    5: "hazardous",
}
POLLEN_CATEGORY_MAP = {
    1: "low",
    2: "moderate",
    3: "high",
    4: "very_high",
    5: "extreme",
}
MANUFACTURER = "AccuWeather, Inc."

CONF_SCAN_INTERVAL = "scan_interval"
CONF_LOCATION_KEY = "location_key"

# Older installs used this options key before the plan-aligned name.
LEGACY_OPTION_POLL_INTERVAL = "poll_interval"

DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
MIN_SCAN_INTERVAL = timedelta(minutes=10)  # 600s — API fairness floor from plan
MAX_SCAN_INTERVAL = timedelta(days=1)

CONDITION_CLASSES: dict[str, list[int]] = {
    ATTR_CONDITION_CLEAR_NIGHT: [33, 34, 37],
    ATTR_CONDITION_CLOUDY: [7, 8, 38],
    ATTR_CONDITION_EXCEPTIONAL: [24, 30, 31],
    ATTR_CONDITION_FOG: [11],
    ATTR_CONDITION_HAIL: [25],
    ATTR_CONDITION_LIGHTNING: [15],
    ATTR_CONDITION_LIGHTNING_RAINY: [16, 17, 41, 42],
    ATTR_CONDITION_PARTLYCLOUDY: [3, 4, 6, 35, 36],
    ATTR_CONDITION_POURING: [18],
    ATTR_CONDITION_RAINY: [12, 13, 14, 26, 39, 40],
    ATTR_CONDITION_SNOWY: [19, 20, 21, 22, 23, 43, 44],
    ATTR_CONDITION_SNOWY_RAINY: [29],
    ATTR_CONDITION_SUNNY: [1, 2, 5],
    ATTR_CONDITION_WINDY: [32],
}
CONDITION_MAP = {
    code: ha_cond
    for ha_cond, codes in CONDITION_CLASSES.items()
    for code in codes
}


def options_scan_interval_seconds(options: dict) -> int:
    """Resolve scan interval from options, honoring the legacy key."""
    if CONF_SCAN_INTERVAL in options:
        return int(options[CONF_SCAN_INTERVAL])
    if LEGACY_OPTION_POLL_INTERVAL in options:
        return int(options[LEGACY_OPTION_POLL_INTERVAL])
    return int(DEFAULT_SCAN_INTERVAL.total_seconds())
