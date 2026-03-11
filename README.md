# OpenVPN Manager for Home Assistant

Connect your Home Assistant to any OpenVPN server for secure remote access.

## What This Does

- Connects Home Assistant to your VPN server (ASUS router, commercial VPN, self-hosted)
- Lets you access Home Assistant remotely through the VPN
- Simple dashboard switch to turn VPN on/off
- Shows connection status and IP address

## Installation

> **Important**: This integration is not yet in the default HACS repository.

> **New in v0.1.0**: Fully automatic! The integration now auto-detects your installation type and handles everything automatically. No manual Docker setup needed!

### Quick Setup (All Installation Types):

#### Step 1: Install via HACS

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

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "OpenVPN Manager"
4. Click on it
5. Configure:
   - Host: `localhost`
   - Port: `9876`
6. Click **Submit** twice (follow the upload instructions shown)

### Step 4: Upload Your VPN Config

After adding the integration, upload your .ovpn file using one of these methods:

**Option A - Via Add-on Files (Easiest):**
1. Go to **Settings → Add-ons → OpenVPN Manager**
2. Click the **Files** tab
3. Navigate to `/data/configs/`
4. Click the folder icon to upload
5. Select your `.ovpn` file

**Option B - Via Terminal/SSH:**
```bash
curl -X POST -F "file=@your-config.ovpn" http://homeassistant.local:9876/api/upload
```

### Step 5: Connect

1. Go to your dashboard
2. Toggle `switch.openvpn_connection` to ON
3. Wait 5-10 seconds
4. Check `sensor.openvpn_status` - should show "connected"

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

### Integration Not Showing After HACS Install

**Problem**: Installed via HACS but can't find "OpenVPN Manager" integration.

**Quick Fix:**
1. **Restart Home Assistant** (Settings → System → Restart) - REQUIRED!
2. Wait 2 minutes for full restart
3. Clear browser cache (Ctrl+Shift+R)
4. Go to **Settings → Devices & Services**
5. Click **+ Add Integration**
6. Search for "OpenVPN Manager"

**Still not showing?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed steps.

### Can't Find Integration in HACS

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
