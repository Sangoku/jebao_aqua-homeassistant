# Jebao Aqua Integration - Quick Start for Maintainers

This is a condensed reference guide for maintainers. For comprehensive details, see [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md).

## 🚀 Quick Setup

```bash
# Clone and setup
git clone https://github.com/chrisc123/jebao_aqua-homeassistant.git
cd jebao_aqua-homeassistant

# Link to HA (development)
ln -s $(pwd)/custom_components/jebao_aqua \
      ~/.homeassistant/custom_components/jebao_aqua

# Restart Home Assistant
```

## 📁 Repository Structure

```
custom_components/jebao_aqua/
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
└── models/              # Device model JSONs
    └── *.json          # One file per product_key
```

## 🔑 Key Concepts

### Communication Flow
- **Polling**: Local LAN (TCP 12416) every 2 seconds
- **Control**: Gizwits Cloud API (HTTPS)
- **Discovery**: UDP broadcast (port 12414)

### Device Models
Each device needs a JSON file in `models/` that maps:
- Binary protocol positions → Entity attributes
- Product key from Gizwits → Device model

### Regional APIs
Three regions with different endpoints:
- `eu` - Europe
- `us` - Americas/Asia (except China)
- `cn` - China

## 🛠️ Common Tasks

### Add New Device Model

1. **Get product key** from Gizwits developer portal or APK
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
4. **Update** README.md compatibility table

### Debug Issues

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.jebao_aqua: debug
```

**Key log patterns:**
- ✅ `"Got fresh data for device"` - Local polling works
- ✅ `"Response from Gizwits API"` - Cloud control works
- ❌ `"Failed to fetch device data"` - Connection issue
- ❌ `"Error parsing device status payload"` - Model mapping issue

### Test Changes

```bash
# Manual testing
1. Modify code
2. Restart Home Assistant
3. Check logs for errors
4. Test entity controls
5. Verify status updates

# Network debugging
nc -v DEVICE_IP 12416              # Test TCP connection
tcpdump -i any port 12416          # Capture device traffic
echo -ne '\x00...' | nc -u -b 255.255.255.255 12414  # Manual discovery
```

### Release New Version

```bash
# 1. Update version
vim custom_components/jebao_aqua/manifest.json  # Change "version"

# 2. Create tag
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0

# 3. Create GitHub release with changelog
```

## 🐛 Troubleshooting Quick Reference

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| No devices found | Wrong region or unbound device | Check country/region, verify in app |
| Entities unavailable | LAN IP wrong or device offline | Verify IP, test connectivity |
| Commands don't work | Token expired or API issue | Re-authenticate, check cloud |
| Discovery fails | Different subnet or firewall | Manual IP entry, check network |
| Parsing errors | Wrong model JSON | Fix byte/bit offsets in JSON |

## 📊 Important Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `const.py` | API URLs, constants | API changes, new regions |
| `api.py` | Protocol implementation | Protocol updates, new features |
| `config_flow.py` | Setup wizard | UI improvements, new options |
| `__init__.py` | Coordinator logic | Polling changes, setup flow |
| `models/*.json` | Device definitions | New devices, fix mappings |

## 🔍 Code Patterns

### Add New Entity Type

1. Create platform file (e.g., `sensor.py`)
2. Implement entity class extending `CoordinatorEntity`
3. Add platform to `PLATFORMS` in `const.py`
4. Platform auto-loaded in `__init__.py`

### Access Device Data

```python
# In entity class
device_data = self.coordinator.device_data.get(self._device["did"])
value = device_data.get("attr", {}).get("attribute_name")
```

### Send Command

```python
await self.coordinator.api.control_device(
    self._device["did"],
    {"attribute_name": value}
)
await self.coordinator.async_request_refresh()
```

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/chrisc123/jebao_aqua-homeassistant/issues)
- **Detailed docs**: See MAINTENANCE_GUIDE.md
- **HA Docs**: https://developers.home-assistant.io/
- **Gizwits Docs**: https://docs.gizwits.com/

## ✅ Pre-Commit Checklist

- [ ] Code follows existing style
- [ ] Tested with real device
- [ ] Logs show no errors
- [ ] README updated if needed
- [ ] Model JSON validated
- [ ] No debug code left in
- [ ] Version bumped (if releasing)

## 📈 Project Status

**Current Version**: 0.1.0  
**Maintainer**: TBD (taking over maintenance)  
**Original Author**: @chrisc123  

**Known Limitations**:
- ❌ WiFi+BLE devices (ESP32C3) not supported
- ⚠️ Cloud API required for control (local control not implemented)
- ⚠️ Native scheduling from app not supported (use HA automations)

**Roadmap**:
1. WiFi+BLE device support
2. Local control (no cloud dependency)
3. HACS integration
4. Automated tests

---

For comprehensive information, consult [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md).