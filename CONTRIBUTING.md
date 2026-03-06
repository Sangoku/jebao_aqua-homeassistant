# Contributing to Jebao Aqua Home Assistant Integration

This guide covers everything you need to get a development environment running, understand the codebase, and contribute effectively.

---

## 🚀 Quick Start (5 minutes)

### Prerequisites

- Docker Desktop installed
- Git
- Text editor (VS Code recommended)

```bash
# Verify installations
docker --version
git --version
```

### 1. Clone and Start

```bash
# Clone the repository
git clone https://github.com/chrisc123/jebao_aqua-homeassistant.git
cd jebao_aqua-homeassistant

# Start Home Assistant (integration is already mounted)
docker-compose up -d

# Watch startup logs (optional)
docker-compose logs -f homeassistant
```

**Wait for this message in logs:**
```
INFO (MainThread) [homeassistant.bootstrap] Home Assistant initialized in X.XXs
```

First startup takes **2-5 minutes** to download the image and initialize.

### 2. Access Home Assistant

1. Open: **http://localhost:8123**
2. Create your first account
3. Set up basic preferences (location, timezone, etc.)

### 3. Install the Integration

The integration is already mounted in the container via `docker-compose.yml`.

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Jebao Aqua Aquarium Pump"**
4. Follow the setup wizard:
   - Select your country/region
   - Enter your Jebao Aqua app credentials
   - Wait for device discovery (or enter IP manually)

### 4. Start Developing

```bash
# Edit any Python file in the integration
vim custom_components/jebao_aqua/api.py

# Restart Home Assistant to load changes
docker-compose restart homeassistant

# Watch logs for errors
docker-compose logs -f homeassistant | grep jebao_aqua
```

---

## 📁 Repository Structure

```
jebao_aqua-homeassistant/
├── README.md                    # Project overview and user docs
├── CONTRIBUTING.md              # This file
├── MAINTENANCE_GUIDE.md         # Comprehensive maintainer reference
├── docker-compose.yml           # Docker dev environment
├── hacs.json                    # HACS metadata
├── docs/                        # Implementation notes and fix history
├── scripts/                     # Utility and debug scripts
│   ├── fetch_device_models.py   # Fetch model JSON from Gizwits API
│   └── test_mode_debug.py       # Debug mode switching behavior
├── ha-config/                   # Home Assistant config for Docker dev
│   └── configuration.yaml
└── custom_components/
    └── jebao_aqua/
        ├── __init__.py          # Main coordinator & setup
        ├── api.py               # Gizwits API & local protocol
        ├── config_flow.py       # Setup wizard
        ├── const.py             # Configuration constants
        ├── discovery.py         # UDP device discovery
        ├── helpers.py           # Utility functions
        ├── switch.py            # Switch entities
        ├── binary_sensor.py     # Status sensors
        ├── select.py            # Mode selectors
        ├── number.py            # Numeric controls
        ├── sensor.py            # Sensor entities
        └── models/              # Device model JSONs (one per product_key)
```

---

## 🔑 Key Concepts

### Communication Flow

- **Polling**: Local LAN (TCP 12416) every 2 seconds
- **Control**: Gizwits Cloud API (HTTPS)
- **Discovery**: UDP broadcast (port 12414)

### Device Models

Each device needs a JSON file in `models/` named by `product_key` that maps:
- Binary protocol byte/bit positions → entity attributes
- Product key from Gizwits → device model name

### Regional APIs

Three regions with different endpoints:
- `eu` — Europe
- `us` — Americas/Asia (except China)
- `cn` — China

### Important Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `const.py` | API URLs, constants | API changes, new regions |
| `api.py` | Protocol implementation | Protocol updates, new features |
| `config_flow.py` | Setup wizard | UI improvements, new options |
| `__init__.py` | Coordinator logic | Polling changes, setup flow |
| `models/*.json` | Device definitions | New devices, fix mappings |

---

## 🛠️ Common Development Tasks

### Add a New Device Model

1. **Get the product key** from the Gizwits developer portal or APK
2. **Create JSON** in `models/PRODUCT_KEY.json`:

```json
{
  "product_key": "abc123...",
  "name": "Device Name",
  "attrs": [
    {
      "display_name": "Power",
      "name": "switch",
      "data_type": "bool",
      "position": {"byte_offset": 0, "bit_offset": 0, "len": 1, "unit": "bit"},
      "type": "status_writable",
      "id": 0,
      "desc": "Controls power"
    }
  ]
}
```

3. **Test** with actual device
4. **Update** the compatibility table in `README.md`

You can use `scripts/fetch_device_models.py` to fetch the raw datapoint definition from the Gizwits API.

### Add a New Entity Type

1. Create a platform file (e.g., `sensor.py`)
2. Implement entity class extending `CoordinatorEntity`
3. Add platform to `PLATFORMS` in `const.py`
4. Platform is auto-loaded in `__init__.py`

### Access Device Data (in entity class)

```python
device_data = self.coordinator.device_data.get(self._device["did"])
value = device_data.get("attr", {}).get("attribute_name")
```

### Send a Command

```python
await self.coordinator.api.control_device(
    self._device["did"],
    {"attribute_name": value}
)
await self.coordinator.async_request_refresh()
```

### Release a New Version

```bash
# 1. Update version in manifest
vim custom_components/jebao_aqua/manifest.json

# 2. Create and push tag
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0

# 3. Create GitHub release with changelog
```

---

## 🐛 Debugging

### Enable Debug Logging

Add to `ha-config/configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.jebao_aqua: debug
    custom_components.jebao_aqua.api: debug
    custom_components.jebao_aqua.config_flow: debug
    custom_components.jebao_aqua.discovery: debug
```

Then restart: `docker-compose restart homeassistant`

### Key Log Patterns

- ✅ `"Got fresh data for device"` — Local polling works
- ✅ `"Response from Gizwits API"` — Cloud control works
- ❌ `"Failed to fetch device data"` — Connection issue
- ❌ `"Error parsing device status payload"` — Model mapping issue

### View Logs

```bash
# Real-time filtering for Jebao logs
docker-compose logs -f homeassistant | grep jebao_aqua

# Search for errors
docker-compose logs homeassistant | grep -i error | grep jebao

# View last 100 lines
docker-compose logs --tail=100 homeassistant
```

### Network Debugging

```bash
# Test TCP connection to device
nc -v DEVICE_IP 12416

# Capture device traffic
tcpdump -i any port 12416

# Manual UDP discovery broadcast
echo -ne '\x00\x00\x00\x03\x03\x00\x00\x03' | nc -u -b 255.255.255.255 12414
```

---

## 🐳 Docker Reference

```bash
# Start HA
docker-compose up -d

# Restart HA (picks up code changes)
docker-compose restart homeassistant

# Stop HA
docker-compose stop

# Stop and remove container
docker-compose down

# View logs
docker-compose logs -f homeassistant

# Access container shell
docker exec -it ha-jebao-dev bash

# Check integration files are mounted
docker exec -it ha-jebao-dev ls /config/custom_components/jebao_aqua/

# Check Python syntax
docker exec -it ha-jebao-dev python3 -m py_compile /config/custom_components/jebao_aqua/api.py

# Update HA image
docker-compose pull && docker-compose up -d
```

**Why `network_mode: host`?**
- Allows HA to discover devices on your local network via UDP broadcast
- Enables direct TCP communication with Jebao devices
- No port mapping needed

If you need bridged networking instead:
```yaml
# In docker-compose.yml, replace network_mode: host with:
ports:
  - "8123:8123"
  - "12414:12414/udp"
  - "12416:12416/tcp"
```

---

## 🔧 Troubleshooting

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| No devices found | Wrong region or unbound device | Check country/region, verify in app |
| Entities unavailable | LAN IP wrong or device offline | Verify IP, test connectivity |
| Commands don't work | Token expired or API issue | Re-authenticate, check cloud |
| Discovery fails | Different subnet or firewall | Manual IP entry, check network |
| Parsing errors | Wrong model JSON | Fix byte/bit offsets in JSON |
| Port 8123 in use | Another process | `lsof -i :8123` to find it |
| Changes not taking effect | Cached state | `docker-compose down && docker-compose up -d` |

---

## ✅ Pre-Commit Checklist

- [ ] Code follows existing style
- [ ] Tested with real device (or documented as untested)
- [ ] Logs show no errors
- [ ] README updated if compatibility changed
- [ ] Model JSON validated
- [ ] No debug print statements left in
- [ ] Version bumped in `manifest.json` (if releasing)

---

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/chrisc123/jebao_aqua-homeassistant/issues)
- **Detailed maintainer docs**: See [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md)
- **HA Developer Docs**: https://developers.home-assistant.io/
- **Gizwits Docs**: https://docs.gizwits.com/
