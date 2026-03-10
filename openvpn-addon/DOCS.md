# OpenVPN Manager Add-on

OpenVPN client for Home Assistant - connects to any OpenVPN server.

## Configuration

```json
{
  "auto_start": false,
  "api_port": 9876,
  "log_level": "info"
}
```

**auto_start** - Automatically connect to VPN when add-on starts (true/false, default: false)

**api_port** - Port for the HTTP API server (default: 9876)

**log_level** - Logging level: debug, info, warning, or error

## Setup

1. Start this add-on
2. Install the OpenVPN Manager integration
3. Upload your .ovpn file via API or manually to `/data/configs/`
4. Toggle VPN on from dashboard

## Getting .ovpn Files

- **ASUS Router**: VPN → VPN Server → OpenVPN → Export
- **Commercial VPN**: Download from provider's website
- **Self-hosted**: Generate using easy-rsa on your OpenVPN server

## API

The add-on provides an HTTP API at `http://localhost:9876/api`

- `POST /api/upload` - Upload .ovpn file
- `POST /api/start` - Start VPN
- `POST /api/stop` - Stop VPN
- `GET /api/status` - Get VPN status
- `GET /api/configs` - List configurations
- `GET /api/logs` - View logs

## Logs

View logs in **Settings → Add-ons → OpenVPN Manager → Log**

## Support

[GitHub Issues](https://github.com/skifahrer/openvpn-in-homeassistant/issues)
