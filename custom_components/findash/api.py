"""Read-only client. Credentials never reach the dashboard card."""

import math
from urllib.parse import urlsplit

import aiohttp

from .const import PATH


class InvalidAuth(Exception):
    """Credentials were rejected."""


def normalize_url(value):
    url = urlsplit(value.strip())
    if (
        url.scheme not in ("http", "https")
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.path not in ("", "/")
    ):
        raise ValueError("Use the server origin without a path, credentials or query")
    return value.strip().rstrip("/")


def validate_payload(data):
    def number(value):
        return type(value) in (int, float) and math.isfinite(value)

    def require(condition):
        if not condition:
            raise ValueError("Invalid Findash money-flow response")

    try:
        require(data["schema_version"] == 1 and data["currency"] == "USD")
        require(isinstance(data["month"], str) and isinstance(data["generated_at"], str))
        # Older servers still support Money flow; new sensors remain unavailable.
        if "overview" in data:
            require(
                all(
                    number(data["overview"][key])
                    for key in ("debit", "credit", "cushion", "free", "mandatory_left")
                )
            )
        # Blocks of newer servers; each is optional so older servers keep working.
        if "today" in data:
            require(number(data["today"]["can_spend"]) and number(data["today"]["days_left"]))
        if "limits" in data:
            require(isinstance(data["limits"], list))
            require(all(number(b["pct"]) and isinstance(b["name"], str) for b in data["limits"]))
        if "forecast" in data:
            require(number(data["forecast"]["min"]["balance"]))
            require(all(number(v) for v in data["forecast"]["points"]))
        if "game" in data:
            require(number(data["game"]["level"]) and isinstance(data["game"]["quests"], list))
        for mode in ("plan", "now"):
            flow = data["flow"][mode]
            require(all(number(flow[k]) for k in ("income", "mandatory", "left", "rest")))
            require(isinstance(flow["parts"], list))
            ids = set()
            for part in flow["parts"]:
                require(part["id"] in ("need", "one_off", "pocket", "prepay", "buffer"))
                require(part["id"] not in ids and number(part["amount"]))
                ids.add(part["id"])
            if "end" in flow:
                require(
                    all(
                        number(flow["end"][k])
                        for k in ("income_ahead", "mandatory_ahead", "result")
                    )
                )
    except (KeyError, TypeError) as err:
        raise ValueError("Invalid Findash money-flow response") from err
    return data


async def fetch(session, config):
    headers = {"Authorization": f"Bearer {config['token']}"}
    if config.get("cf_client_id"):
        headers["CF-Access-Client-Id"] = config["cf_client_id"]
        headers["CF-Access-Client-Secret"] = config.get("cf_client_secret", "")
    async with session.get(
        normalize_url(config["url"]) + PATH,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=30),
        allow_redirects=False,
    ) as response:
        if response.status in (401, 403) or 300 <= response.status < 400:
            raise InvalidAuth
        response.raise_for_status()
        return validate_payload(await response.json())
