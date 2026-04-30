"""AccuWeather (HACS): configurable API key and scan interval."""

from __future__ import annotations

from datetime import timedelta

from accuweather import AccuWeather

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .accuweather_api import AccuWeatherApi
from .const import CONF_LOCATION_KEY, options_scan_interval_seconds
from .coordinator import AccuWeatherHacsConfigEntry, AccuWeatherHacsCoordinator

PLATFORMS = [Platform.SENSOR, Platform.WEATHER]


async def _async_reload(hass: HomeAssistant, entry_id: str) -> None:
    """Reload integration after shutdown so reload does not collide with teardown."""
    if hass.state is not CoreState.stopping:
        await hass.config_entries.async_reload(entry_id)


async def _options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options (or merged data updates) change."""
    await _async_reload(hass, entry.entry_id)


async def async_setup_entry(
    hass: HomeAssistant, entry: AccuWeatherHacsConfigEntry
) -> bool:
    """Set up from a config entry."""
    api_key: str = entry.data[CONF_API_KEY]
    websession = async_get_clientsession(hass)
    poll_seconds = options_scan_interval_seconds(entry.options)

    location_key = entry.data.get(CONF_LOCATION_KEY) or entry.unique_id
    if not location_key:
        msg = "Config entry missing location key"
        raise ValueError(msg)

    accuweather = AccuWeather(
        api_key,
        websession,
        location_key=str(location_key),
    )
    api = AccuWeatherApi(accuweather)
    interval = timedelta(seconds=poll_seconds)

    coordinator = AccuWeatherHacsCoordinator(hass, entry, api, interval)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_options_update_listener))

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AccuWeatherHacsConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
