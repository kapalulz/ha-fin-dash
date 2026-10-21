"""Configure Findash from the integrations UI."""

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import InvalidAuth, fetch, normalize_url
from .const import DOMAIN


def schema(defaults):
    password = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))
    return vol.Schema(
        {
            vol.Required("url", default=defaults.get("url", "")): str,
            vol.Required("token"): password,
            vol.Optional("cf_client_id", default=defaults.get("cf_client_id", "")): str,
            vol.Optional("cf_client_secret"): password,
        }
    )


class FindashConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                user_input["url"] = normalize_url(user_input["url"])
                if bool(user_input.get("cf_client_id")) != bool(user_input.get("cf_client_secret")):
                    raise ValueError("Both Cloudflare fields are required")
                await fetch(async_get_clientsession(self.hass), user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_data"
            else:
                await self.async_set_unique_id(user_input["url"])
                if self.source == "reauth":
                    self._abort_if_unique_id_mismatch()
                    return self.async_update_reload_and_abort(
                        self._get_reauth_entry(), data_updates=user_input
                    )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Findash", data=user_input)
        defaults = user_input or getattr(self, "_defaults", {})
        return self.async_show_form(step_id="user", data_schema=schema(defaults), errors=errors)

    async def async_step_reauth(self, entry_data):
        self._defaults = entry_data
        return await self.async_step_user()
