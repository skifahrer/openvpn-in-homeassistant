"""Constants for the OpenVPN Manager integration."""

# Domain
DOMAIN = "openvpn_manager"

# Platforms
PLATFORMS = ["switch", "sensor"]

# Configuration defaults
DEFAULT_API_HOST = "localhost"
DEFAULT_API_PORT = 9876
DEFAULT_TIMEOUT = 30
DEFAULT_SCAN_INTERVAL = 60  # seconds

# Configuration keys
CONF_API_HOST = "api_host"
CONF_API_PORT = "api_port"

# Coordinator data keys
DATA_COORDINATOR = "coordinator"
DATA_CLIENT = "client"

# Service names
SERVICE_UPLOAD_CONFIG = "upload_config"
SERVICE_SET_DEFAULT_CONFIG = "set_default_config"
SERVICE_DELETE_CONFIG = "delete_config"

# Service attributes
ATTR_CONFIG_FILE = "config_file"
ATTR_CONFIG_NAME = "config_name"
ATTR_FILE_CONTENT = "file_content"
ATTR_FILENAME = "filename"

# Entity IDs
ENTITY_ID_VPN_SWITCH = "openvpn_connection"
ENTITY_ID_STATUS_SENSOR = "openvpn_status"
ENTITY_ID_IP_SENSOR = "openvpn_ip"
ENTITY_ID_UPTIME_SENSOR = "openvpn_uptime"

# Status values
STATUS_CONNECTED = "connected"
STATUS_DISCONNECTED = "disconnected"
STATUS_CONNECTING = "connecting"
STATUS_ERROR = "error"
STATUS_UNKNOWN = "unknown"

# Icons
ICON_VPN = "mdi:vpn"
ICON_VPN_CONNECTED = "mdi:shield-check"
ICON_VPN_DISCONNECTED = "mdi:shield-off"
ICON_IP = "mdi:ip"
ICON_UPTIME = "mdi:clock-outline"
