# OpenVPN Manager for Home Assistant

Connect your Home Assistant to any OpenVPN server for secure remote access.

## What This Does

- Connects Home Assistant to your VPN server (ASUS router, commercial VPN, self-hosted)
- Lets you access Home Assistant remotely through the VPN
- Simple dashboard switch to turn VPN on/off
- Shows connection status and IP address

## Installation

> **Important**: This integration is not yet in the default HACS repository.

### Step 1: Install the Add-on

1. Go to **Settings → Add-ons → Add-on Store**
2. Click menu (⋮) → **Repositories**
3. Add: `https://github.com/skifahrer/openvpn-in-homeassistant`
4. Find **OpenVPN Manager** and click **Install**
5. Click **Start**

### Step 2: Install the Integration

**Via HACS (add as custom repository):**

1. Open **HACS → Integrations**
2. Click menu (⋮) → **Custom repositories**
3. Add repository:
   - Repository: `https://github.com/skifahrer/openvpn-in-homeassistant`
   - Category: **Integration**
4. Click **Add**
5. Search "OpenVPN Manager" and click **Download**
6. Restart Home Assistant

**Manual install:**

1. Copy `custom_components/openvpn_manager` to your `config/custom_components/` directory
2. Restart Home Assistant

### Step 3: Add Integration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search "OpenVPN Manager"
3. Configure:
   - Host: `localhost`
   - Port: `9876`

### Step 4: Upload Your VPN Config

Upload your `.ovpn` file:

```bash
curl -X POST -F "file=@your-config.ovpn" http://homeassistant.local:9876/api/upload
```

### Step 5: Connect

Toggle `switch.openvpn_connection` to ON in your dashboard.

## Dashboard Entities

After setup:

- `switch.openvpn_connection` - Turn VPN on/off
- `sensor.openvpn_status` - Connection status
- `sensor.openvpn_ip` - Your VPN IP address
- `sensor.openvpn_uptime` - Connection uptime

## Common Use Cases

### Remote Access via ASUS Router

1. Enable OpenVPN server on your ASUS router
2. Export the `.ovpn` configuration file
3. Upload to Home Assistant (no modifications needed)
4. Toggle VPN on
5. Access HA from anywhere at `http://[VPN-IP]:8123`

### Commercial VPN (Privacy)

1. Download `.ovpn` from your provider (NordVPN, ExpressVPN, etc.)
2. Upload to Home Assistant
3. Toggle VPN on
4. Your HA's public IP becomes the VPN server's IP

## Configuration

Add-on settings (**Settings → Add-ons → OpenVPN Manager → Configuration**):

```json
{
  "auto_start": false,
  "api_port": 9876,
  "log_level": "info"
}
```

- `auto_start` - Auto-connect VPN when add-on starts (default: false)
- `api_port` - API server port (default: 9876)
- `log_level` - debug, info, warning, or error

## Getting .ovpn Files

- **ASUS Router**: VPN → VPN Server → OpenVPN → Export
- **Commercial VPNs**: Download from provider's website
- **Self-hosted**: Generate using OpenVPN server's easy-rsa tools

## Dashboard Card Example

```yaml
type: entities
title: VPN
entities:
  - entity: switch.openvpn_connection
  - entity: sensor.openvpn_status
  - entity: sensor.openvpn_ip
```

## Troubleshooting

### VPN Won't Connect

Check add-on logs: **Settings → Add-ons → OpenVPN Manager → Log**

Common issues:
- Wrong server address in .ovpn file
- Authentication failed (check credentials)
- Port blocked by firewall

### Can't Find Integration

Make sure you:
1. Added the repository as a **custom repository** in HACS
2. Selected **Integration** as the category (not Add-on)
3. Restarted Home Assistant after installation

### Integration Can't Connect to Add-on

Verify:
- Add-on is running (green "Started" indicator)
- API host is set to `localhost`
- API port is `9876`

## API Endpoints

The add-on exposes a REST API at `http://localhost:9876/api`:

- `GET /api/status` - Get VPN status
- `POST /api/start` - Start VPN
- `POST /api/stop` - Stop VPN
- `POST /api/upload` - Upload .ovpn file
- `GET /api/configs` - List configurations
- `GET /api/logs` - View logs

## Support

- [GitHub Issues](https://github.com/skifahrer/openvpn-in-homeassistant/issues)
- [Home Assistant Community](https://community.home-assistant.io/)

## License

MIT License - see [LICENSE](LICENSE) file for details.
