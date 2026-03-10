"""The OpenVPN Manager integration."""
import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    PLATFORMS,
    DEFAULT_SCAN_INTERVAL,
    DATA_COORDINATOR,
    DATA_CLIENT,
    CONF_API_HOST,
    CONF_API_PORT,
)
from .helpers.api_client import APIClient

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Dict[str, Any]) -> bool:
    """Set up the OpenVPN Manager integration from YAML configuration."""
    # YAML configuration is not supported, only config flow
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenVPN Manager from a config entry."""
    _LOGGER.info(f"Setting up OpenVPN Manager integration for {entry.entry_id}")

    # Get configuration
    api_host = entry.data.get(CONF_API_HOST)
    api_port = entry.data.get(CONF_API_PORT)

    # Create API client
    client = APIClient(api_host, api_port)

    # Test connection
    try:
        health = await client.health_check()
        if not health.get("success"):
            raise UpdateFailed(f"Cannot connect to OpenVPN Manager add-on: {health.get('error')}")
    except Exception as e:
        _LOGGER.error(f"Failed to connect to OpenVPN Manager add-on: {e}")
        raise UpdateFailed(f"Cannot connect to add-on at {api_host}:{api_port}") from e

    # Create coordinator
    coordinator = OpenVPNManagerCoordinator(hass, client)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator and client
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_CLIENT: client,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("OpenVPN Manager integration setup complete")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info(f"Unloading OpenVPN Manager integration for {entry.entry_id}")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class OpenVPNManagerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching OpenVPN Manager data."""

    def __init__(self, hass: HomeAssistant, client: APIClient):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client
        self._last_error = None

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API."""
        try:
            response = await self.client.get_status()

            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                _LOGGER.error(f"API returned error: {error_msg}")
                raise UpdateFailed(f"API error: {error_msg}")

            # Extract data from response
            data = response.get("data", {})

            _LOGGER.debug(f"Coordinator updated data: {data}")
            self._last_error = None

            return data

        except UpdateFailed:
            raise
        except Exception as e:
            error_msg = f"Error communicating with add-on: {str(e)}"
            _LOGGER.error(error_msg)
            self._last_error = error_msg
            raise UpdateFailed(error_msg) from e

    @property
    def last_error(self) -> str | None:
        """Return the last error message."""
        return self._last_error
