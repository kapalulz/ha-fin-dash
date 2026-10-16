"""Constants of the fin-dash integration."""

DOMAIN = "fin_dash"

CONF_URL = "url"
CONF_TOKEN = "token"
CONF_CF_CLIENT_ID = "cf_client_id"
CONF_CF_CLIENT_SECRET = "cf_client_secret"
CONF_VERIFY_SSL = "verify_ssl"
CONF_SCAN_MINUTES = "scan_minutes"

DEFAULT_SCAN_MINUTES = 15
MIN_SCAN_MINUTES = 5
MAX_SCAN_MINUTES = 240

# Budget groups of fin-dash (calc.BUDGET_GROUPS): one limit sensor each.
LIMIT_GROUPS = ("food", "eating_out", "shopping", "home", "car", "fun")
