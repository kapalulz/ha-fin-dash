"""Talks to fin-dash: GET /api/ha with a Bearer token, optionally through Cloudflare Access
with a service token. No Home Assistant imports here, so it is easy to test."""

from __future__ import annotations

from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=30)


class FinDashError(Exception):
    """Base error."""


class CannotConnect(FinDashError):
    """Network error, timeout or an unexpected answer."""


class InvalidAuth(FinDashError):
    """fin-dash refused the token (401)."""


class CloudflareBlocked(FinDashError):
    """Cloudflare Access answered instead of fin-dash: the service token is missing or wrong."""


class EndpointOff(FinDashError):
    """fin-dash answered 404: HA_TOKEN is not set there, or the version is too old."""


def endpoint(url: str) -> str:
    return url.rstrip("/") + "/api/ha"


def headers(token: str, cf_id: str | None = None, cf_secret: str | None = None) -> dict:
    out = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if cf_id and cf_secret:  # Cloudflare Access service token
        out["CF-Access-Client-Id"] = cf_id
        out["CF-Access-Client-Secret"] = cf_secret
    return out


class FinDashClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        token: str,
        cf_id: str | None = None,
        cf_secret: str | None = None,
        verify_ssl: bool = True,
    ) -> None:
        self._session = session
        self._url = endpoint(url)
        self._headers = headers(token, cf_id, cf_secret)
        self._ssl = None if verify_ssl else False

    async def fetch(self) -> dict[str, Any]:
        try:
            async with self._session.get(
                self._url,
                headers=self._headers,
                timeout=TIMEOUT,
                allow_redirects=False,  # Cloudflare Access redirects to its login page
                ssl=self._ssl,
            ) as resp:
                if resp.status in (301, 302, 303, 307, 308) or resp.status == 403:
                    raise CloudflareBlocked(f"HTTP {resp.status}")
                if resp.status == 401:
                    raise InvalidAuth("token refused")
                if resp.status == 404:
                    raise EndpointOff("GET /api/ha not found")
                if resp.status != 200:
                    raise CannotConnect(f"HTTP {resp.status}")
                try:
                    data = await resp.json(content_type=None)
                except (ValueError, aiohttp.ContentTypeError) as err:
                    raise CannotConnect("not JSON") from err
        except (TimeoutError, aiohttp.ClientError) as err:
            raise CannotConnect(type(err).__name__) from err
        if not isinstance(data, dict) or "money" not in data:
            raise CannotConnect("unexpected answer")
        return data
