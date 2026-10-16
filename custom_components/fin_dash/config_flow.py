"""Set up from the UI: fin-dash address, its HA_TOKEN and, if HA goes through Cloudflare
Access, a service token. Options: how often to poll."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CannotConnect, CloudflareBlocked, EndpointOff, FinDashClient, InvalidAuth
from .const import (
    CONF_CF_CLIENT_ID,
    CONF_CF_CLIENT_SECRET,
    CONF_SCAN_MINUTES,
    CONF_TOKEN,
    CONF_URL,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_MINUTES,
    DOMAIN,
    MAX_SCAN_MINUTES,
    MIN_SCAN_MINUTES,
)


def _schema(defaults: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_URL, default=defaults.get(CONF_URL, "https://")): str,
            vol.Required(CONF_TOKEN, default=defaults.get(CONF_TOKEN, "")): str,
            vol.Optional(
                CONF_CF_CLIENT_ID, description={"suggested_value": defaults.get(CONF_CF_CLIENT_ID)}
            ): str,
            vol.Optional(
                CONF_CF_CLIENT_SECRET,
                description={"suggested_value": defaults.get(CONF_CF_CLIENT_SECRET)},
            ): str,
            vol.Optional(CONF_VERIFY_SSL, default=defaults.get(CONF_VERIFY_SSL, True)): bool,
        }
    )


class FinDashConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _check(self, data: dict[str, Any]) -> str | None:
        """None if fin-dash answered, else the error key for strings.json."""
        verify = data.get(CONF_VERIFY_SSL, True)
        client = FinDashClient(
            async_get_clientsession(self.hass, verify_ssl=verify),
            data[CONF_URL],
            data[CONF_TOKEN],
            data.get(CONF_CF_CLIENT_ID),
            data.get(CONF_CF_CLIENT_SECRET),
            verify,
        )
        try:
            await client.fetch()
        except InvalidAuth:
            return "invalid_auth"
        except CloudflareBlocked:
            return "cloudflare"
        except EndpointOff:
            return "endpoint_off"
        except CannotConnect:
            return "cannot_connect"
        return None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_URL] = user_input[CONF_URL].strip().rstrip("/")
            await self.async_set_unique_id(user_input[CONF_URL].lower())
            self._abort_if_unique_id_configured()
            if (error := await self._check(user_input)) is None:
                return self.async_create_entry(title="fin-dash", data=user_input)
            errors["base"] = error
        return self.async_show_form(
            step_id="user", data_schema=_schema(user_input or {}), errors=errors
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {**entry.data, **user_input}
            if (error := await self._check(data)) is None:
                return self.async_update_reload_and_abort(entry, data=data)
            errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm", data_schema=_schema(entry.data), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return FinDashOptionsFlow()


class FinDashOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(CONF_SCAN_MINUTES, DEFAULT_SCAN_MINUTES)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_MINUTES, default=current): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_MINUTES, max=MAX_SCAN_MINUTES)
                    )
                }
            ),
        )
