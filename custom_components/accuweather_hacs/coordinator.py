"""Single DataUpdateCoordinator for AccuWeather (HACS)."""

from __future__ import annotations

from asyncio import timeout
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from accuweather import ApiError, InvalidApiKeyError, RequestsExceededError
from aiohttp.client_exceptions import ClientConnectorError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .accuweather_api import AccuWeatherApi
from .const import DOMAIN, MANUFACTURER

EXCEPTIONS = (ApiError, ClientConnectorError, RequestsExceededError)

_LOGGER = logging.getLogger(__package__)


@dataclass(frozen=True)
class AccuWeatherPayload:
    """Snapshot from one coordinated poll."""

    current: dict[str, Any]
    daily: list[dict[str, Any]]
    hourly: list[dict[str, Any]]


class AccuWeatherHacsCoordinator(DataUpdateCoordinator[AccuWeatherPayload]):
    """One coordinator refresh = current + daily + hourly."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: AccuWeatherApi,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.api = api
        self.location_key = api.location_key
        name = config_entry.data.get(CONF_NAME) or config_entry.title

        if TYPE_CHECKING:
            assert self.location_key is not None

        self.device_info = _get_device_info(self.location_key, name)

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=name,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> AccuWeatherPayload:
        """Fetch all AccuWeather payloads in one logical update."""
        try:
            async with timeout(30):
                current, daily, hourly = await self.api.async_fetch_all(
                    self.hass.config.language
                )
        except EXCEPTIONS as error:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="forecast_update_error",
                translation_placeholders={"error": repr(error)},
            ) from error
        except InvalidApiKeyError as err:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="auth_error",
                translation_placeholders={"entry": self.config_entry.title},
            ) from err

        remaining = self.api.requests_remaining
        if remaining is not None:
            _LOGGER.debug("Requests remaining: %s", remaining)

        return AccuWeatherPayload(current=current, daily=daily, hourly=hourly)


def _get_device_info(location_key: str, name: str) -> DeviceInfo:
    """Device registry entry for the service."""
    return DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, location_key)},
        manufacturer=MANUFACTURER,
        name=name,
        configuration_url=(
            "https://www.accuweather.com/en/"
            f"_/_/{location_key}/weather-forecast/{location_key}/"
        ),
    )


type AccuWeatherHacsConfigEntry = ConfigEntry[AccuWeatherHacsCoordinator]
