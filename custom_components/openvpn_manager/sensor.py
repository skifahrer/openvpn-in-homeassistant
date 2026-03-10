"""Sensor platform for OpenVPN Manager."""
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    ENTITY_ID_STATUS_SENSOR,
    ENTITY_ID_IP_SENSOR,
    ENTITY_ID_UPTIME_SENSOR,
    ICON_VPN,
    ICON_IP,
    ICON_UPTIME,
    STATUS_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenVPN Manager sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    # Create sensor entities
    entities = [
        OpenVPNStatusSensor(coordinator),
        OpenVPNIPSensor(coordinator),
        OpenVPNUptimeSensor(coordinator),
    ]

    async_add_entities(entities)
    _LOGGER.info("OpenVPN Manager sensor entities created")


class OpenVPNStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of OpenVPN connection status sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "OpenVPN Status"
        self._attr_unique_id = f"{DOMAIN}_{ENTITY_ID_STATUS_SENSOR}"
        self._attr_icon = ICON_VPN
        self._attr_has_entity_name = False

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self.coordinator.data.get("status", STATUS_UNKNOWN)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        data = self.coordinator.data
        return {
            "is_running": data.get("is_running", False),
            "config_name": data.get("current_config"),
            "process_id": data.get("process_id"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class OpenVPNIPSensor(CoordinatorEntity, SensorEntity):
    """Representation of OpenVPN WAN IP sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "OpenVPN IP"
        self._attr_unique_id = f"{DOMAIN}_{ENTITY_ID_IP_SENSOR}"
        self._attr_icon = ICON_IP
        self._attr_has_entity_name = False

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        wan_ip = self.coordinator.data.get("wan_ip")
        return wan_ip if wan_ip else "Not Connected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "is_connected": self.coordinator.data.get("is_running", False),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class OpenVPNUptimeSensor(CoordinatorEntity, SensorEntity):
    """Representation of OpenVPN uptime sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "OpenVPN Uptime"
        self._attr_unique_id = f"{DOMAIN}_{ENTITY_ID_UPTIME_SENSOR}"
        self._attr_icon = ICON_UPTIME
        self._attr_native_unit_of_measurement = "s"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_has_entity_name = False

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data.get("uptime", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        uptime_formatted = self.coordinator.data.get("uptime_formatted")
        attrs = {}
        if uptime_formatted:
            attrs["formatted"] = uptime_formatted
        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
