# Installation for Home Assistant Container

If you're using **Home Assistant Container** (Docker), add-ons are not available. Follow these instructions instead.

## Requirements

- Home Assistant Container running
- Docker and Docker Compose installed on your host
- Access to your host system

## Installation Steps

### Step 1: Clone This Repository

```bash
cd ~
git clone https://github.com/skifahrer/openvpn-in-homeassistant.git
cd openvpn-in-homeassistant
```

### Step 2: Start the OpenVPN Manager Container

```bash
# Create data directories
mkdir -p data/configs data/logs

# Start the container
docker-compose up -d openvpn-manager
```

Or manually with Docker:

```bash
docker run -d \
  --name openvpn-manager \
  --privileged \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  --device /dev/net/tun \
  -v $(pwd)/data/configs:/data/configs \
  -v $(pwd)/data/logs:/data/logs \
  -v $(pwd)/data:/data \
  -e API_PORT=9876 \
  -e LOG_LEVEL=info \
  -e AUTO_START=false \
  -p 9876:9876 \
  --restart unless-stopped \
  ghcr.io/skifahrer/openvpn-manager:latest
```

### Step 3: Verify Container is Running

```bash
# Check container status
docker ps | grep openvpn-manager

# Check logs
docker logs openvpn-manager

# Test API
curl http://localhost:9876/api/health
```

You should see: `{"success": true, ...}`

### Step 4: Install the Integration in Home Assistant

#### Via HACS:

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click menu (⋮) → **Custom repositories**
4. Add: `https://github.com/skifahrer/openvpn-in-homeassistant`
5. Category: **Integration**
6. Find **OpenVPN Manager** and click **Download**
7. Restart Home Assistant

#### Manual:

1. Copy `custom_components/openvpn_manager` to your Home Assistant config directory:
   ```bash
   cp -r custom_components/openvpn_manager /path/to/homeassistant/config/custom_components/
   ```
2. Restart Home Assistant

### Step 5: Add the Integration

1. In Home Assistant, go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **"OpenVPN Manager"**
4. Configure:
   - API Host: `localhost` (or your host IP if Home Assistant is on different host)
   - API Port: `9876`
5. Click **Submit**

The integration should now auto-detect the running container!

### Step 6: Upload Your VPN Configuration

**Option 1 - Via File System:**

Copy your .ovpn file to the data directory:
```bash
cp your-config.ovpn data/configs/
```

**Option 2 - Via API:**

```bash
curl -X POST -F "file=@your-config.ovpn" http://localhost:9876/api/upload
```

**Option 3 - Via Docker:**

```bash
docker cp your-config.ovpn openvpn-manager:/data/configs/
```

### Step 7: Connect to VPN

1. Go to your Home Assistant dashboard
2. Find the switch: `switch.openvpn_connection`
3. Toggle it **ON**
4. Check `sensor.openvpn_status` - should show "connected"

## Docker Compose Full Example

If you want to run both Home Assistant and OpenVPN Manager together:

```yaml
version: '3.8'

services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    volumes:
      - ./homeassistant:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host

  openvpn-manager:
    build: ./openvpn-addon
    container_name: openvpn-manager
    restart: unless-stopped
    privileged: true
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    devices:
      - /dev/net/tun
    volumes:
      - ./data/configs:/data/configs
      - ./data/logs:/data/logs
      - ./data:/data
    environment:
      - API_PORT=9876
      - LOG_LEVEL=info
    ports:
      - "9876:9876"
```

Then run:
```bash
docker-compose up -d
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs openvpn-manager
```

Common issues:
- Port 9876 already in use
- Missing /dev/net/tun device
- Insufficient permissions

### Can't Connect to API

Test the API directly:
```bash
curl http://localhost:9876/api/health
```

If this fails:
- Container not running
- Port not exposed
- Firewall blocking

### Integration Can't Find Container

If Home Assistant and OpenVPN Manager are on different hosts:
- Use the host's IP address instead of `localhost`
- Make sure port 9876 is accessible between hosts

### VPN Won't Connect

Check OpenVPN logs:
```bash
docker exec openvpn-manager cat /data/logs/openvpn.log
```

Or:
```bash
docker logs openvpn-manager
```

## Updates

### Update Container:

```bash
cd openvpn-in-homeassistant
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

Or with Docker:
```bash
docker pull ghcr.io/skifahrer/openvpn-manager:latest
docker stop openvpn-manager
docker rm openvpn-manager
# Run docker run command again (from Step 2)
```

### Update Integration:

Via HACS: Click **Update** when available

## Systemd Service (Optional)

To start the container on boot:

Create `/etc/systemd/system/openvpn-manager.service`:

```ini
[Unit]
Description=OpenVPN Manager Container
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/openvpn-in-homeassistant
ExecStart=/usr/local/bin/docker-compose up -d openvpn-manager
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable openvpn-manager
sudo systemctl start openvpn-manager
```

## Need Help?

- [GitHub Issues](https://github.com/skifahrer/openvpn-in-homeassistant/issues)
- [Main README](README.md)
