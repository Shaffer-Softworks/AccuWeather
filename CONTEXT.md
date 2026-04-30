# AccuWeather (HACS) — saved context

## What this repo is

A **Home Assistant custom integration** (`domain: **accuweather_hacs**`), installable via **HACS**, separate from core `accuweather`. It uses the PyPI package **`accuweather==5.1.0`** (same client style as core).

## User-facing behavior

- **Config flow:** API key, latitude/longitude (defaults to HA home), **scan interval** (seconds; min **600**).
- **Options flow:** Optional new API key (blank = keep), scan interval. Legacy options key **`poll_interval`** is still read as scan interval until resaved as **`scan_interval`**.
- **Data:** `CONF_LOCATION_KEY` + `CONF_API_KEY` + lat/lon in entry data; scan interval in **options**.
- **Reload:** `add_update_listener` reloads the config entry when options/data change.

## Architecture

- **Single `DataUpdateCoordinator`** (`AccuWeatherHacsCoordinator`): each refresh calls **`AccuWeatherApi.async_fetch_all`** → **3 API requests** (current conditions, daily forecast, hourly forecast). Sensors and weather read this payload only (no extra polling).
- **Platforms:** `sensor` (parity with core AccuWeather forecast + observation sensors) and `weather` (`CoordinatorEntity` + `WeatherEntity`, not triple `CoordinatorWeatherEntity`).
- **Minimum HA:** **2024.11** (`ConfigEntry.runtime_data`).

## API usage (15k calls/month budgeting)

- **Calls per refresh = 3.** Rough monthly polling ≈ `3 × (86400 / scan_seconds) × days_in_month` (plus setup/reauth/UI validation).

## Branding / icon (HA 2026.3+)

- Local art lives in **`custom_components/accuweather_hacs/brand/`** (`icon.png`, `logo.png`, `@2x`, dark variants). **`has_branding`** requires that directory to exist with valid PNGs. This repo copies official **`accuweather`** assets from **brands.home-assistant.io** for the integration card.

## Translations

- **Do not** use `[%key:common::...%]` in custom integration `strings.json` / `translations/en.json` for fields that do not resolve in the UI; use **plain English** (same fix applied to config flow labels). **`entity.sensor`** block merged from core with key references expanded/fixed.

## Docker (dev)

- Root **`docker-compose.yml`**: `ghcr.io/home-assistant/home-assistant:stable`, port **8123**, named volume for `/config`, bind mount **`./custom_components` → `/config/custom_components`**.

## Files to know

| Area | Path |
|------|------|
| Entry / platforms | `custom_components/accuweather_hacs/__init__.py` |
| Config / options | `custom_components/accuweather_hacs/config_flow.py` |
| Constants / maps | `custom_components/accuweather_hacs/const.py` |
| Coordinator + payload | `custom_components/accuweather_hacs/coordinator.py` |
| API wrapper | `custom_components/accuweather_hacs/accuweather_api.py` |
| Weather | `custom_components/accuweather_hacs/weather.py` |
| Sensors | `custom_components/accuweather_hacs/sensor.py` |
| i18n | `strings.json`, `translations/en.json` |
| HACS metadata | `hacs.json`, `manifest.json` |

## Manifest / repo

- **`documentation`:** `https://github.com/Shaffer-Softworks/AccuWeather` (adjust if the GitHub repo differs).
- **`codeowners`:** `@Shaffer-Softworks`.
