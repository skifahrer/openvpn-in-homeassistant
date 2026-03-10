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

_LOGGER = logging.getLogger(__name__)


class OpenVPNManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenVPN Manager."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self._api_host = DEFAULT_API_HOST
        self._api_port = DEFAULT_API_PORT

    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Get user input
            api_host = user_input[CONF_API_HOST]
            api_port = user_input[CONF_API_PORT]

            # Validate connection
            try:
                client = APIClient(api_host, api_port)
                health = await client.health_check()

                if not health.get("success"):
                    errors["base"] = "cannot_connect"
                else:
                    # Connection successful - create entry
                    await self.async_set_unique_id(f"{DOMAIN}_{api_host}_{api_port}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title="OpenVPN Manager",
                        data={
                            CONF_API_HOST: api_host,
                            CONF_API_PORT: api_port,
                        },
                    )

            except Exception as e:
                _LOGGER.error(f"Error connecting to OpenVPN Manager add-on: {e}")
                errors["base"] = "cannot_connect"

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_HOST, default=DEFAULT_API_HOST): cv.string,
                vol.Required(CONF_API_PORT, default=DEFAULT_API_PORT): cv.port,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "default_host": DEFAULT_API_HOST,
                "default_port": str(DEFAULT_API_PORT),
            },
        )

    async def async_step_import(self, import_config: Dict[str, Any]) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)
