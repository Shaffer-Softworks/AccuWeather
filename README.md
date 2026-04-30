# AccuWeather (HACS)

Custom Home Assistant integration for [AccuWeather](https://www.accuweather.com/), installable via [HACS](https://www.hacs.xyz/).

This integration uses the same **`accuweather`** Python client as Home Assistant Core, with a **distinct domain** (`accuweather_hacs`) so it does not replace the built-in `accuweather` integration.

## Features

- **API key** — set at onboarding; change later under **Configure** (leave the API key field blank to keep the current key).
- **Scan interval** — one interval (seconds) for the whole integration. A single [`DataUpdateCoordinator`](https://developers.home-assistant.io/docs/integration_quality_scale_index/#data-update-coordinator) refresh loads **current conditions**, **daily forecast**, and **hourly forecast** together via [`accuweather_api.py`](custom_components/accuweather_hacs/accuweather_api.py). Default **3600** s; **minimum 600** s (10 minutes) to reduce accidental API overuse.
- **Location** — latitude/longitude (defaults to your Home Assistant home). The AccuWeather **location key** is stored in the config entry after validation.

Older installs may still have the legacy options key `poll_interval`; it is treated the same as `scan_interval` until you save options once.

## Prerequisites

An AccuWeather Data Services API key from the [developer portal](https://developer.accuweather.com/).

**Quota:** Every scan performs several API calls. Respect your daily request limits.

## Install with HACS

1. Open HACS → **Integrations**.
2. **⋮ menu** → **Custom repositories**.
3. Add this repository URL, category **Integration**, then **Add**.
4. Install **AccuWeather (HACS)** and restart Home Assistant.

## Configure

1. **Settings → Devices & services → Add integration**.
2. Search **AccuWeather (HACS)**.
3. Enter your API key, optional coordinates, and scan interval.
4. Later changes: integration card → **Configure** → scan interval and optional new API key.

## Requirements

Home Assistant **2024.11** or newer (`ConfigEntry.runtime_data`).

## Brand assets

Home Assistant **2026.3+** loads integration art from [`custom_components/accuweather_hacs/brand/`](custom_components/accuweather_hacs/brand/) (`icon.png`, `logo.png`, `@2x`, and dark variants). This repo ships the same artwork as the official **Accuweather** entry on [brands.home-assistant.io](https://brands.home-assistant.io/accuweather/) so the UI icon resolves; swap files there if you want custom branding.

## Compare to core

Core’s `accuweather` integration uses **multiple** coordinators with different cadences. This project uses **one** coordinator and one user-controlled scan interval so API usage is easier to reason about.
