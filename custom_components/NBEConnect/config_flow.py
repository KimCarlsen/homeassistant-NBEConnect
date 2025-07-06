import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)


class NbeConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for NBEConnect custom integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step when setting up the integration."""
        errors = {}

        if user_input is not None:
            # Validate the user input
            if not user_input.get("serial"):
                errors["base"] = "missing_serial"
            if not user_input.get("password"):
                errors["base"] = "missing_password"

            if not errors:
                # Configuration is valid, create the entry
                # Check if an entry with this serial already exists to prevent duplicates
                await self.async_set_unique_id(user_input["serial"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="NBEConnect by svj", data=user_input)
        
        # Define the schema for the user input form
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(
                    "serial", 
                    description={
                        "label": "Boiler Serial Number", 
                        "hint": "Enter the serial number found on your NBE boiler label."
                    }
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="serial")
                ),
                vol.Required(
                    "password", 
                    description={
                        "label": "Boiler Password", 
                        "hint": "Enter the password found on your NBE boiler label."
                    }
                ): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD, autocomplete="current-password"
                    )
                ),
                vol.Optional(
                    "ip_address", 
                    description={
                        "label": "Boiler IP Address (Optional)", 
                        "hint": "Enter the fixed IP address of your boiler. Leave empty for auto-discovery."
                    }
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="ip_address")
                )
            }
        )

        # Show the configuration form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return NbeConnectOptionsFlowHandler(config_entry)


class NbeConnectOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle NBEConnect options flow."""

    def __init__(self, config_entry):
        """Initialize NBEConnect options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Validate the user input for reconfigure
            if not user_input.get("serial"):
                errors["base"] = "missing_serial"
            if not user_input.get("password"):
                errors["base"] = "missing_password"

            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input
                )
                return self.async_create_entry(title="", data=user_input) # Title is not shown for options flow

        # Get current data to pre-fill the form
        current_data = self.config_entry.data

        # Define the schema for the reconfigure form, pre-filling with current values
        OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Required(
                    "serial",
                    default=current_data.get("serial", ""),
                    description={
                        "label": "Boiler Serial Number", 
                        "hint": "Enter the serial number found on your NBE boiler label."
                    }
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="serial")
                ),
                vol.Required(
                    "password",
                    default=current_data.get("password", ""),
                    description={
                        "label": "Boiler Password", 
                        "hint": "Enter the password found on your NBE boiler label."
                    }
                ): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD, autocomplete="current-password"
                    )
                ),
                vol.Optional(
                    "ip_address",
                    default=current_data.get("ip_address", ""),
                    description={
                        "label": "Boiler IP Address (Optional)", 
                        "hint": "Enter the fixed IP address of your boiler. Leave empty for auto-discovery."
                    }
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="")
                )
            }
        )

        # Show the reconfigure form
        return self.async_show_form(
            step_id="init",
            data_schema=OPTIONS_SCHEMA,
            errors=errors
        )
