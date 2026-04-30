"""Thin async wrapper around the AccuWeather client library."""

from __future__ import annotations

from typing import Any

from accuweather import AccuWeather


class AccuWeatherApi:
    """Fetches current conditions and forecasts using a shared AccuWeather client."""

    def __init__(self, client: AccuWeather) -> None:
        """Initialize with a configured AccuWeather instance (location already resolved)."""
        self._client = client

    @property
    def location_key(self) -> str | None:
        """AccuWeather location key."""
        return self._client.location_key

    @property
    def requests_remaining(self) -> int | None:
        """Remaining API quota for the current period, if reported by the client."""
        return getattr(self._client, "requests_remaining", None)

    async def async_fetch_all(self, language: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        """Return current conditions, daily forecast, and hourly forecast."""
        current = await self._client.async_get_current_conditions()
        daily = await self._client.async_get_daily_forecast(language=language)
        hourly = await self._client.async_get_hourly_forecast(language=language)
        return current, daily, hourly
