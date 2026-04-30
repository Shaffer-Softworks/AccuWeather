"""Config flow for AccuWeather (HACS)."""

from __future__ import annotations

from asyncio import timeout
from typing import TYPE_CHECKING, Any

from accuweather import AccuWeather, ApiError, InvalidApiKeyError, RequestsExceededError
from aiohttp import ClientError
from aiohttp.client_exceptions import ClientConnectorError
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_LOCATION_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    options_scan_interval_seconds,
)


class AccuWeatherHacsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            websession = async_get_clientsession(self.hass)
            try:
                async with timeout(10):
                    accuweather = AccuWeather(
                        user_input[CONF_API_KEY],
                        websession,
                        latitude=user_input[CONF_LATITUDE],
                        longitude=user_input[CONF_LONGITUDE],
                    )
                    await accuweather.async_get_location()
            except (ApiError, ClientConnectorError, TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            except InvalidApiKeyError:
                errors[CONF_API_KEY] = "invalid_api_key"
            except RequestsExceededError:
                errors[CONF_API_KEY] = "requests_exceeded"
            else:
                await self.async_set_unique_id(
                    accuweather.location_key, raise_on_progress=False
                )
                self._abort_if_unique_id_configured()

                if TYPE_CHECKING:
                    assert accuweather.location_name is not None
                    assert accuweather.location_key is not None

                scan_seconds = int(user_input[CONF_SCAN_INTERVAL])
                data = {
                    CONF_API_KEY: user_input[CONF_API_KEY],
                    CONF_LATITUDE: user_input[CONF_LATITUDE],
                    CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                    CONF_LOCATION_KEY: accuweather.location_key,
                }
                return self.async_create_entry(
                    title=accuweather.location_name,
                    data=data,
                    options={CONF_SCAN_INTERVAL: scan_seconds},
                )

        default_scan = int(DEFAULT_SCAN_INTERVAL.total_seconds())
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(
                        CONF_LATITUDE,
                        default=self.hass.config.latitude,
                    ): cv.latitude,
                    vol.Optional(
                        CONF_LONGITUDE,
                        default=self.hass.config.longitude,
                    ): cv.longitude,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=default_scan,
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=int(MIN_SCAN_INTERVAL.total_seconds()),
                            max=int(MAX_SCAN_INTERVAL.total_seconds()),
                            step=60,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> AccuWeatherHacsOptionsFlow:
        """Options flow."""
        return AccuWeatherHacsOptionsFlow()


class AccuWeatherHacsOptionsFlow(OptionsFlow):
    """Options: API key and scan interval."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            websession = async_get_clientsession(self.hass)
            api_key = user_input.get(CONF_API_KEY, "").strip()
            if not api_key:
                api_key = self.config_entry.data[CONF_API_KEY]

            scan_seconds = int(user_input[CONF_SCAN_INTERVAL])

            try:
                async with timeout(10):
                    accuweather = AccuWeather(
                        api_key,
                        websession,
                        latitude=self.config_entry.data[CONF_LATITUDE],
                        longitude=self.config_entry.data[CONF_LONGITUDE],
                    )
                    await accuweather.async_get_location()
            except (ApiError, ClientConnectorError, TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            except InvalidApiKeyError:
                errors[CONF_API_KEY] = "invalid_api_key"
            except RequestsExceededError:
                errors[CONF_API_KEY] = "requests_exceeded"
            else:
                new_data = dict(self.config_entry.data)
                new_data[CONF_API_KEY] = api_key
                new_data[CONF_LOCATION_KEY] = accuweather.location_key
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=new_data,
                )
                return self.async_create_entry(
                    title="", data={CONF_SCAN_INTERVAL: scan_seconds}
                )

        current_scan = options_scan_interval_seconds(self.config_entry.options)

        schema = vol.Schema(
            {
                vol.Optional(CONF_API_KEY, description={"suggested_value": ""}): str,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_scan,
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=int(MIN_SCAN_INTERVAL.total_seconds()),
                        max=int(MAX_SCAN_INTERVAL.total_seconds()),
                        step=60,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="s",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "location": self.config_entry.title,
            },
        )
