"""Config flow for OpenVPN Manager integration."""
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_API_HOST,
    DEFAULT_API_PORT,
    CONF_API_HOST,
    CONF_API_PORT,
)
from .helpers.api_client import APIClient
from .docker_manager import DockerManager

_LOGGER = logging.getLogger(__name__)


class OpenVPNManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenVPN Manager."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self._api_host = DEFAULT_API_HOST
        self._api_port = DEFAULT_API_PORT
        self._addon_detected = False
        self._docker_manager = None

    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - auto-detect or auto-start OpenVPN."""
        errors = {}

        # First, try to detect if service is already running
        if user_input is None:
            # Try to connect to default location
            try:
                client = APIClient(DEFAULT_API_HOST, DEFAULT_API_PORT)
                health = await client.health_check()

                if health.get("success"):
                    # Service is running! Skip to upload step
                    self._addon_detected = True
                    self._api_host = DEFAULT_API_HOST
                    self._api_port = DEFAULT_API_PORT

                    await self.async_set_unique_id(f"{DOMAIN}_{DEFAULT_API_HOST}_{DEFAULT_API_PORT}")
                    self._abort_if_unique_id_configured()

                    # Go directly to upload step
                    return await self.async_step_upload()

            except Exception:
                pass  # Service not running, continue to auto-start

            # Service not running - try to auto-start it
            return await self.async_step_auto_start()

        # This shouldn't be reached
        return await self.async_step_auto_start(user_input)

    async def async_step_auto_start(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Automatically start OpenVPN service (add-on or container)."""

        # Check if we have Supervisor (OS/Supervised install)
        has_supervisor = "hassio" in self.hass.config.components

        if has_supervisor:
            # Running on OS/Supervised - show add-on install instructions
            return await self.async_step_install_addon(user_input)

        # Running on Container/Core - try Docker auto-start
        self._docker_manager = DockerManager(self.hass)

        if not self._docker_manager.is_available():
            # Docker not available
            return self.async_abort(
                reason="docker_not_available",
                description_placeholders={
                    "error": "Docker is not available. Please ensure Docker is installed and accessible."
                }
            )

        # Try to auto-start container
        _LOGGER.info("Attempting to auto-start OpenVPN container")
        result = await self._docker_manager.ensure_container_running()

        if not result.get("success"):
            return self.async_abort(
                reason="container_start_failed",
                description_placeholders={
                    "error": result.get("error", "Unknown error")
                }
            )

        # Container started! Wait a moment for it to initialize
        import asyncio
        await asyncio.sleep(3)

        # Verify it's accessible
        try:
            client = APIClient(DEFAULT_API_HOST, DEFAULT_API_PORT)
            health = await client.health_check()

            if health.get("success"):
                await self.async_set_unique_id(f"{DOMAIN}_{DEFAULT_API_HOST}_{DEFAULT_API_PORT}")
                self._abort_if_unique_id_configured()

                self._api_host = DEFAULT_API_HOST
                self._api_port = DEFAULT_API_PORT

                # Success! Go to upload step
                return await self.async_step_upload()

        except Exception as e:
            _LOGGER.error(f"Container started but API not accessible: {e}")
            return self.async_abort(
                reason="api_not_accessible",
                description_placeholders={
                    "error": "Container started but API not responding. Check container logs."
                }
            )

        return self.async_abort(reason="unknown_error")

    async def async_step_install_addon(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Show installation instructions based on HA installation type."""
        if user_input is not None:
            # User clicked "I've installed", verify it's running
            try:
                client = APIClient(DEFAULT_API_HOST, DEFAULT_API_PORT)
                health = await client.health_check()

                if health.get("success"):
                    await self.async_set_unique_id(f"{DOMAIN}_{DEFAULT_API_HOST}_{DEFAULT_API_PORT}")
                    self._abort_if_unique_id_configured()

                    self._api_host = DEFAULT_API_HOST
                    self._api_port = DEFAULT_API_PORT
                    return await self.async_step_upload()
                else:
                    return self.async_abort(reason="addon_not_running")
            except Exception:
                return self.async_abort(reason="addon_not_running")

        # Detect installation type
        has_supervisor = self.hass.components.hassio.is_hassio() if "hassio" in self.hass.config.components else False

        # Show appropriate instructions based on installation type
        step_id = "install_addon" if has_supervisor else "install_container"

        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema({}),
            description_placeholders={
                "addon_url": "config/hassio/addon/local_openvpn-manager",
            },
        )

    async def async_step_upload(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        """Show upload instructions."""
        if user_input is not None:
            # User clicked "I've uploaded the file" or similar
            return self.async_create_entry(
                title="OpenVPN Manager",
                data={
                    CONF_API_HOST: self._api_host,
                    CONF_API_PORT: self._api_port,
                },
            )

        # Show instructions for uploading .ovpn file
        return self.async_show_form(
            step_id="upload",
            data_schema=vol.Schema({}),
            last_step=True,
        )

    async def async_step_import(self, import_config: Dict[str, Any]) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)
