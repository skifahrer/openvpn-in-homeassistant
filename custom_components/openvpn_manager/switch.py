"""Switch platform for OpenVPN Manager."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    DATA_CLIENT,
    ENTITY_ID_VPN_SWITCH,
    ICON_VPN,
    ICON_VPN_CONNECTED,
    ICON_VPN_DISCONNECTED,
    STATUS_CONNECTED,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenVPN Manager switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]

    # Create switch entity
    entities = [OpenVPNSwitch(coordinator, client)]

    async_add_entities(entities)
    _LOGGER.info("OpenVPN Manager switch entity created")


class OpenVPNSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of OpenVPN connection switch."""

    def __init__(self, coordinator, client):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "OpenVPN Connection"
        self._attr_unique_id = f"{DOMAIN}_{ENTITY_ID_VPN_SWITCH}"
        self._attr_has_entity_name = False

    @property
    def is_on(self) -> bool:
        """Return true if VPN is connected."""
        return self.coordinator.data.get("is_running", False)

    @property
    def icon(self) -> str:
        """Return the icon based on state."""
        if self.is_on:
            status = self.coordinator.data.get("status", "")
            if status == STATUS_CONNECTED:
                return ICON_VPN_CONNECTED
            return ICON_VPN
        return ICON_VPN_DISCONNECTED

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        data = self.coordinator.data
        return {
            "status": data.get("status", "unknown"),
            "config_name": data.get("current_config"),
            "wan_ip": data.get("wan_ip"),
            "uptime": data.get("uptime", 0),
            "uptime_formatted": data.get("uptime_formatted"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the VPN connection."""
        try:
            _LOGGER.info("Turning on OpenVPN connection")

            result = await self._client.start_vpn()

            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                _LOGGER.error(f"Failed to start VPN: {error_msg}")
                raise HomeAssistantError(f"Failed to start VPN: {error_msg}")

            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()

        except Exception as e:
            _LOGGER.error(f"Error turning on VPN: {e}")
            raise HomeAssistantError(f"Error turning on VPN: {str(e)}") from e

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the VPN connection."""
        try:
            _LOGGER.info("Turning off OpenVPN connection")

            result = await self._client.stop_vpn()

            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                _LOGGER.error(f"Failed to stop VPN: {error_msg}")
                raise HomeAssistantError(f"Failed to stop VPN: {error_msg}")

            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()

        except Exception as e:
            _LOGGER.error(f"Error turning off VPN: {e}")
            raise HomeAssistantError(f"Error turning off VPN: {str(e)}") from e

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.last_error is None
