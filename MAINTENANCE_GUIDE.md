# Jebao Aqua Home Assistant Integration - Maintenance Guide

## Table of Contents
1. [Repository Overview](#repository-overview)
2. [Architecture & Technical Stack](#architecture--technical-stack)
3. [Key Components](#key-components)
4. [Development Setup](#development-setup)
5. [Code Structure](#code-structure)
6. [Known Device Limitations](#known-device-limitations)
7. [Testing Procedures](#testing-procedures)
8. [Adding New Device Models](#adding-new-device-models)
9. [Common Maintenance Tasks](#common-maintenance-tasks)
10. [Troubleshooting](#troubleshooting)
11. [Contributing Guidelines](#contributing-guidelines)
12. [Release Process](#release-process)

---

## Repository Overview

**Project**: Jebao Aqua Home Assistant Custom Integration  
**Purpose**: Control and monitor WiFi-enabled Jebao aquarium pumps through Home Assistant  
**Current Version**: 0.1.0  
**Repository**: https://github.com/chrisc123/jebao_aqua-homeassistant  
**Original Author**: @chrisc123  

### Compatibility Status

| Device Type | Status | Notes |
|------------|--------|-------|
| MCP Series Crossflow | ✅ Working | Tested |
| MLW Series | ✅ Working | Tested |
| SLW Series | ⚠️ Unconfirmed | Added but not tested |
| EP Series | ⚠️ Unconfirmed | Added but not tested |
| Smart Doser 3.1 | ✅ Working | Added by @jeffcybulski |
| MD 4.4 Dosing Pump | ✅ Working | Added by @jeffcybulski |
| MD 2.4 Dosing Pump | ✅ Working | Added by @joluan01 |
| WiFi+BLE Devices | ❌ Not Working | Under investigation |

### Important Limitations

⚠️ **CRITICAL**: As of late 2024, newer Jebao devices with WiFi+Bluetooth (ESP32C3) are NOT compatible. Only older WiFi-only devices (ESP8266) work.

---

## Architecture & Technical Stack

### Communication Architecture

```
┌─────────────────┐
│  Home Assistant │
│    Integration  │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌───────┐  ┌──────────┐
│ Local │  │ Gizwits  │
│  LAN  │  │   Cloud  │
│ Poll  │  │   API    │
└───┬───┘  └────┬─────┘
    │           │
    └─────┬─────┘
          ▼
    ┌──────────┐
    │  Jebao   │
    │  Device  │
    │(ESP8266) │
    └──────────┘
```

### Technology Stack

- **Language**: Python 3.x (async/await)
- **Framework**: Home Assistant Core
- **API Platform**: Gizwits IoT Cloud
- **Protocols**: 
  - HTTP/REST (Cloud API)
  - TCP/Binary (Local LAN - Port 12416)
  - UDP Broadcast (Device Discovery - Port 12414)
- **Dependencies**: 
  - `aiohttp` (async HTTP)
  - `voluptuous` (config validation)
  - `pycountry` (country/region mapping)

### Data Flow

1. **Polling**: Local LAN polling (every 2 seconds) for status updates
2. **Control**: Commands sent via Gizwits Cloud API
3. **Discovery**: UDP broadcast for auto-detecting device IPs

---

## Key Components

### File Structure

```
custom_components/jebao_aqua/
├── __init__.py              # Main integration setup & coordinator
├── manifest.json            # Integration metadata
├── const.py                 # Constants & configuration
├── api.py                   # Gizwits API & local protocol handler
├── config_flow.py           # Setup wizard & options flow
├── discovery.py             # UDP device discovery
├── helpers.py               # Shared utility functions
├── switch.py                # Switch entities (on/off controls)
├── binary_sensor.py         # Binary sensor entities (status)
├── select.py                # Select entities (mode/enum selection)
├── number.py                # Number entities (flow/frequency)
├── models/                  # Device model definitions
│   ├── 5b3c136f....json    # Doser 2.4 model
│   ├── 1d8c63ea....json    # MCP model
│   └── [other models].json
└── translations/            # UI translations
    ├── en.json
    ├── de.json
    └── it.json
```

### Core Classes

#### `GizwitsDataUpdateCoordinator`
- Manages device data updates
- Handles both cloud and local polling
- Implements device-specific update locks
- Update interval: 2 seconds

#### `GizwitsApi`
- Cloud authentication & token management
- Device control via REST API
- Local LAN communication (TCP port 12416)
- Binary protocol parsing for device status

#### Entity Platform Classes
- `JebaoPumpSwitch` - Boolean controls
- `JebaoPumpBinarySensor` - Status indicators
- `JebaoPumpSelect` - Mode/option selection
- `JebaoPumpNumber` - Numeric value controls

---

## Development Setup

> **See [CONTRIBUTING.md](CONTRIBUTING.md) for the full Docker-based development environment setup, quick start guide, and common development tasks.**

### Summary

The recommended development workflow uses Docker Compose to run a local Home Assistant instance with the integration mounted directly from source:

```bash
git clone https://github.com/chrisc123/jebao_aqua-homeassistant.git
cd jebao_aqua-homeassistant
docker-compose up -d
# Open http://localhost:8123
```

Code changes take effect after `docker-compose restart homeassistant`.

### Development Tools

```bash
# Code formatting
pip install black
black custom_components/jebao_aqua/

# Linting
pip install pylint
pylint custom_components/jebao_aqua/

# Type checking
pip install mypy
mypy custom_components/jebao_aqua/
```

---

## Code Structure

### Critical Files & Their Responsibilities

#### `__init__.py` - Integration Entry Point
**Key Functions:**
- `async_setup()` - Initialize integration
- `async_setup_entry()` - Setup from config entry
- `load_attribute_models()` - Load device models from JSON
- `GizwitsDataUpdateCoordinator._async_update_data()` - Core polling logic

**Important Notes:**
- Uses async context manager for API session
- Implements per-device update locks to prevent race conditions
- Gracefully handles devices without LAN IPs (cloud-only mode)

#### `api.py` - Communication Layer
**Key Methods:**
- `async_login()` - Authenticate with Gizwits
- `get_device_data()` - Fetch device status (cloud)
- `get_local_device_data()` - Poll device locally
- `control_device()` - Send commands to device
- `_parse_device_status()` - Decode binary status payload

**Binary Protocol Details:**
```
Local Protocol (TCP 12416):
1. Send 0x0006 - Get binding key
2. Send 0x0008 + key - Authenticate
3. Send 0x0093 - Request status
4. Parse LEB128 encoded response
```

#### `config_flow.py` - Setup Wizard
**Flow Steps:**
1. `async_step_user()` - Country/credentials input
2. `async_step_device_setup()` - LAN IP configuration
3. Device discovery runs automatically
4. Creates config entry with all device data

**Options Flow:**
- Allows reconfiguration
- Re-discovers devices
- Updates config entry dynamically

#### `const.py` - Configuration
**Key Constants:**
- `GIZWITS_APP_ID` - Android app ID
- `GIZWITS_API_URLS` - Regional API endpoints (EU/US/CN)
- `UPDATE_INTERVAL` - 2 seconds
- `LAN_PORT` - 12416 (device communication)
- `BROADCAST_PORT` - 12414 (discovery)
- `SERVICE_MAP` - Country to region mapping

#### Device Model JSON Structure
```json
{
  "product_key": "5b3c136fd4b74f3fb2a366a254c76c9a",
  "name": "Doser 2.4 WiFi 4-Channel",
  "attrs": [
    {
      "display_name": "Power Switch",
      "name": "switch",
      "data_type": "bool",
      "position": {
        "byte_offset": 0,
        "bit_offset": 0,
        "len": 1,
        "unit": "bit"
      },
      "type": "status_writable",
      "id": 0,
      "desc": "Controls the power state"
    }
  ]
}
```

**Data Types:**
- `bool` - Binary switch
- `enum` - Selection from list
- `uint8` - 8-bit unsigned integer
- `binary` - Raw hex data

---

## Known Device Limitations

### MLW Series Wavemaker (product_key: `54114ccdac1e41c0bb17e222887c07ba`)

The MLW series (newer BLE-enabled models) has **incomplete firmware support** for both local LAN and cloud API protocols.

**What works:**
- ✅ Mode selection (Classic Wave, Sine Wave, Random Wave, Constant Flow) — via local UDP
- ✅ Linkage setting (Independent, Primary, Secondary)
- ✅ Basic switches (Main switch, Pulse/Tide, Feeding switch)
- ✅ Cloud control commands

**What doesn't work (firmware limitation, not an integration bug):**
- ❌ Flow value monitoring — device only sends 1 byte of status data; bytes 2-4 (Flow, Frequency, FeedTime) are never transmitted
- ❌ Frequency value monitoring
- ❌ Feed Time value monitoring
- ❌ Fault sensor reporting (Overcurrent, Overvoltage, OverTemp, etc.)

**Root cause:** The MLW wavemaker sends only 1 byte of status data via both local LAN (TCP 12416) and cloud API. The model definition expects bytes at positions 2, 3, 4 for numeric values, but the device firmware does not transmit them. This is consistent across both communication paths, suggesting a firmware limitation rather than a protocol issue.

**Timer switch behaviour:** The timer cannot be enabled when the main pump switch is OFF — this is a device-level safety feature, not a bug. Turn on the main switch first, then enable the timer.

**Mode control:** MLW devices use local UDP protocol for mode changes (not cloud API). The integration detects MLW devices by product_key and routes mode commands accordingly.

For full details, see [`docs/MLW_PROTOCOL_INVESTIGATION.md`](docs/MLW_PROTOCOL_INVESTIGATION.md) and [`docs/MLW_MODE_SELECTOR_FIX.md`](docs/MLW_MODE_SELECTOR_FIX.md).

### Devices Without Local Model Files

Devices without a matching JSON in `models/` automatically fall back to cloud API for all communication. This provides full functionality but without local LAN polling. To add local support, create a model file following the structure in [Adding New Device Models](#adding-new-device-models).

### WiFi+BLE Devices (ESP32C3)

Newer Jebao devices with both WiFi and Bluetooth (ESP32C3 microcontroller) are **not compatible** with this integration. The communication protocol appears to have changed. Only older WiFi-only devices (ESP8266) are supported.

---

## Testing Procedures

### Manual Testing Checklist

#### Initial Setup Test
- [ ] Integration appears in HACS/Integrations
- [ ] Config flow starts successfully
- [ ] Country selection works
- [ ] Login succeeds with valid credentials
- [ ] Login fails gracefully with invalid credentials
- [ ] Device discovery finds devices
- [ ] Manual IP entry works when discovery fails
- [ ] Integration creates successfully

#### Entity Creation Test
- [ ] All devices appear in Devices page
- [ ] Switch entities created for boolean attributes
- [ ] Select entities created for enum attributes
- [ ] Number entities created for uint attributes
- [ ] Binary sensors created for status attributes
- [ ] Entity names are human-readable
- [ ] Unique IDs are stable across restarts

#### Functionality Test
- [ ] Switches turn on/off
- [ ] Selects change modes
- [ ] Numbers adjust values
- [ ] Status updates within 2 seconds
- [ ] Commands execute successfully
- [ ] Multiple devices work independently
- [ ] Devices survive HA restart
- [ ] Integration survives HA reload

#### Network Conditions Test
- [ ] Works with LAN IP (local polling)
- [ ] Falls back to cloud when IP unavailable
- [ ] Handles device offline gracefully
- [ ] Recovers when device comes back online
- [ ] Handles network timeout properly

#### Edge Cases
- [ ] Multiple devices of same model
- [ ] Device with no LAN IP configured
- [ ] Device changes IP address
- [ ] Cloud API rate limiting
- [ ] Malformed device data

### Automated Testing (Future)

```python
# Example test structure
import pytest
from custom_components.jebao_aqua.api import GizwitsApi

@pytest.mark.asyncio
async def test_login_success():
    api = GizwitsApi(login_url="...", ...)
    async with api:
        token, error = await api.async_login("test@example.com", "password")
        assert token is not None
        assert error is None

@pytest.mark.asyncio
async def test_parse_device_status():
    # Test binary protocol parsing
    payload = bytes.fromhex("0100...")
    result = api._parse_device_status(payload, test_model)
    assert result["switch"] == True
```

---

## Adding New Device Models

### Process Overview

New devices require a JSON model file that maps binary data positions to attributes. Follow these steps:

### Step 1: Capture Device Data

1. **Setup Packet Capture**
```bash
# On device's network
tcpdump -i any -w jebao_capture.pcap port 12416 or port 12414
```

2. **Use Gizwits Developer Tools**
- Access: https://dev.gizwits.com/
- Login with developer account
- Find your device's product key
- Get datapoint definitions from: `/app/datapoint?product_key=YOUR_KEY`

3. **Inspect APK (Android)**
```bash
# Decompile APK
apktool d JebaoAqua.apk

# Find model definitions in assets or resources
grep -r "product_key" JebaoAqua/
```

### Step 2: Create Model JSON

Create `custom_components/jebao_aqua/models/PRODUCT_KEY.json`:

```json
{
  "product_key": "YOUR_PRODUCT_KEY_HERE",
  "name": "Device Model Name",
  "attrs": [
    {
      "display_name": "Human Readable Name",
      "name": "api_attribute_name",
      "data_type": "bool|enum|uint8|binary",
      "position": {
        "byte_offset": 0,
        "bit_offset": 0,
        "len": 1,
        "unit": "bit|byte"
      },
      "type": "status_writable|status_readonly",
      "id": 0,
      "desc": "Description for enum or general purpose",
      "enum": ["Option1", "Option2"],  // For enum types
      "uint_spec": {                    // For uint8 types
        "min": 0,
        "max": 100,
        "ratio": 1,
        "addition": 0
      }
    }
  ]
}
```

### Step 3: Understand Binary Position

**Example Byte Layout:**
```
Byte 0: [bit7][bit6][bit5][bit4][bit3][bit2][bit1][bit0]
        Timer4 Timer3 Timer2 Timer1 Ch4    Ch3    Ch2    Ch1
Byte 1: [bit7-bit0] - Reserved or other data
Byte 2: [uint8] - Interval Time 1
Byte 3: [uint8] - Interval Time 2
```

**Endianness Notes:**
- Some multi-byte values need endian swapping
- Code automatically handles this for values spanning byte boundaries
- First two bytes are swapped if needed (see `_swap_endian()`)

### Step 4: Test Model

1. **Add device to Home Assistant**
2. **Check logs for parsing errors**
```
custom_components.jebao_aqua: Error parsing device status payload
```
3. **Verify entities created correctly**
4. **Test control commands work**

### Step 5: Document and Contribute

1. Update README.md compatibility table
2. Add notes about specific device quirks
3. Create pull request with:
   - Model JSON file
   - Test results
   - Screenshots
   - Any special configuration needed

### Common Pitfalls

❌ **Incorrect bit_offset** - Entities show wrong state  
✅ Use Wireshark to decode actual binary data

❌ **Wrong data_type** - Parser fails  
✅ Match type to actual data (bool for 1-bit, uint8 for 8-bit numbers)

❌ **Missing enum values** - Select shows nothing  
✅ Provide complete list in "desc" array

❌ **Byte offset off by one** - All values wrong  
✅ Remember: byte 0 is first byte, not byte 1

---

## Common Maintenance Tasks

### Updating Gizwits API Endpoints

If Gizwits changes their API:

1. **Update `const.py`**
```python
GIZWITS_API_URLS = {
    "eu": {
        "LOGIN_URL": "https://NEW_URL/app/smart_home/login/pwd",
        # ... other URLs
    }
}
```

2. **Test login flow**
3. **Update all regions (EU/US/CN)**

### Adding New Language Translation

1. **Create translation file**
```bash
cp custom_components/jebao_aqua/translations/en.json \
   custom_components/jebao_aqua/translations/fr.json
```

2. **Translate strings**
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Configuration du compte Jebao Aqua",
        "description": "Entrez vos informations..."
      }
    }
  }
}
```

3. **Test in Home Assistant** (set language in profile)

### Adjusting Polling Interval

⚠️ **Warning**: Faster polling increases network load and cloud API requests

In `const.py`:
```python
UPDATE_INTERVAL = timedelta(seconds=2)  # Current
UPDATE_INTERVAL = timedelta(seconds=5)  # Less frequent
```

**Considerations:**
- Gizwits has rate limits
- Local polling is fast, cloud is slow
- 2 seconds is reasonable for real-time control

### Handling API Authentication Changes

If Gizwits changes auth:

1. **Check `api.py` `async_login()` method**
2. **Update request payload format**
3. **Update token parsing logic**
4. **Test error handling for new error codes**

Example:
```python
# Old format
data = {"appKey": APP_ID, "data": {...}}

# If changed to
data = {"appId": APP_ID, "credentials": {...}}
```

### Version Bumping

1. **Update `manifest.json`**
```json
{
  "version": "0.2.0"
}
```

2. **Update HACS compatibility** (if needed)
```json
{
  "hacs": "1.6.0",
  "homeassistant": "2023.5.0"
}
```

3. **Tag release in git**
```bash
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "No devices found"

**Symptoms:**
- Setup completes but no devices listed
- Empty device list after login

**Solutions:**
1. Verify devices are bound to account in Jebao Aqua app
2. Check regional server selection (EU/US/CN)
3. Verify API token is valid
4. Check Home Assistant logs for API errors

**Debug Steps:**
```python
# Enable debug logging
LOGGER.debug("Devices response: %s", response)
```

#### Issue: "Entities unavailable"

**Symptoms:**
- Entities show as "Unavailable"
- No status updates

**Solutions:**
1. Check device is online
2. Verify LAN IP is correct (ping from HA host)
3. Check firewall rules (TCP 12416)
4. Test cloud fallback (remove LAN IP)

**Debug:**
```bash
# Test LAN connectivity
nc -v DEVICE_IP 12416

# Check routes
ip route get DEVICE_IP
```

#### Issue: "Control commands don't work"

**Symptoms:**
- Switches don't change state
- Selects don't update mode
- Commands time out

**Solutions:**
1. Verify Gizwits cloud API is accessible
2. Check token hasn't expired (re-authenticate)
3. Verify device is online in Jebao Aqua app
4. Check Home Assistant logs for API errors

**Debug:**
```bash
# Test cloud API manually
curl -X POST https://euapi.gizwits.com/app/control/DEVICE_ID \
  -H "X-Gizwits-User-token: YOUR_TOKEN" \
  -H "X-Gizwits-Application-Id: c3703c4888ec4736a3a0d9425c321604" \
  -H "Content-Type: application/json" \
  -d '{"attrs": {"switch": true}}'
```

#### Issue: "Device discovery fails"

**Symptoms:**
- Setup wizard doesn't find devices
- Must manually enter IP addresses

**Solutions:**
1. Ensure HA and devices on same subnet
2. Check UDP broadcast is allowed (firewall/router)
3. Verify devices are powered on
4. Try manual IP entry as fallback

**Debug:**
```bash
# Send manual discovery broadcast
echo -ne '\x00\x00\x00\x03\x03\x00\x00\x03' | nc -u -b 255.255.255.255 12414

# Listen for responses
tcpdump -i any udp port 12414
```

#### Issue: "Entities show stale data"

**Symptoms:**
- Values don't update after changes
- Last updated time is old
- Changes via app don't reflect in HA

**Solutions:**
1. Check coordinator update interval
2. Verify device isn't rate-limiting
3. Force refresh via developer tools
4. Check network latency

**Debug:**
```yaml
# Force refresh in HA Developer Tools > Services
service: homeassistant.update_entity
target:
  entity_id: switch.pump_power
```

#### Issue: "Integration won't load"

**Symptoms:**
- Error during startup
- Integration not available
- Config entry fails

**Solutions:**
1. Check Home Assistant version compatibility
2. Verify all files present in custom_components
3. Check for Python syntax errors
4. Review logs for import errors

**Debug:**
```bash
# Check file permissions
ls -la ~/.homeassistant/custom_components/jebao_aqua/

# Validate JSON files
python3 -m json.tool models/PRODUCT_KEY.json

# Check imports
python3 -c "from custom_components.jebao_aqua import api"
```

### Log Analysis

**Key log patterns to look for:**

```
# Successful authentication
"Login response status: 200"
"Got fresh data for device"

# Device communication
"Successfully parsed local device data"
"Response from Gizwits API"

# Errors
"Failed to fetch device data"
"Error parsing device status payload"
"No valid device data received"
"Connection error with local device"
```

**Enable maximum debugging:**

```yaml
logger:
  default: warning
  logs:
    custom_components.jebao_aqua: debug
    custom_components.jebao_aqua.api: debug
    custom_components.jebao_aqua.config_flow: debug
    homeassistant.components.http: info
```

---

## Contributing Guidelines

### Before Contributing

1. **Read existing code** - Understand the architecture
2. **Test thoroughly** - Verify on actual devices
3. **Document changes** - Update README and this guide
4. **Follow conventions** - Match existing code style

### Code Style Guidelines

**Python Style:**
- Follow PEP 8
- Use async/await for I/O operations
- Type hints for function signatures
- Descriptive variable names

**Example:**
```python
async def get_device_data(self, device_id: str) -> dict | None:
    """Get device data either locally or from cloud.
    
    Args:
        device_id: The device identifier
        
    Returns:
        Device data dictionary or None if failed
    """
    try:
        # Implementation
        pass
    except Exception as e:
        LOGGER.error(f"Error: {e}")
        return None
```

**Home Assistant Conventions:**
- Use `DataUpdateCoordinator` for polling
- Implement `CoordinatorEntity` for entities
- Use `async_add_executor_job` for blocking I/O
- Proper device_info and unique_id implementation

### Pull Request Process

1. **Fork and branch**
```bash
git checkout -b feature/new-device-model
```

2. **Make changes**
- Add new model JSON
- Update compatibility table
- Add translations if needed

3. **Test locally**
- Install in test HA instance
- Verify all functionality
- Check logs for errors

4. **Document**
- Update README.md
- Update MAINTENANCE_GUIDE.md
- Add code comments

5. **Submit PR**
- Clear title and description
- List testing performed
- Include screenshots/logs
- Reference any issues

**PR Template:**
```markdown
## Description
Brief description of changes

## Device Tested
- Model: Jebao XXX
- Product Key: xxxxx
- Firmware: x.x.x

## Testing Performed
- [ ] Setup completes successfully
- [ ] Entities created correctly
- [ ] Controls work as expected
- [ ] Status updates in real-time
- [ ] Tested with cloud-only mode
- [ ] Tested with LAN mode

## Screenshots
[If applicable]

## Related Issues
Fixes #123
```

### Areas for Contribution

**High Priority:**
1. WiFi+BLE device support (ESP32C3)
2. Local control implementation (no cloud dependency)
3. Automated testing framework
4. Additional device models

**Medium Priority:**
1. HACS integration
2. Enhanced error messages
3. Setup wizard improvements
4. Performance optimizations

**Low Priority:**
1. Additional translations
2. UI enhancements
3. Documentation improvements
4. Code refactoring

---

## Release Process

### Version Numbering

Follow Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes, API changes
- **MINOR**: New features, new devices
- **PATCH**: Bug fixes, minor improvements

**Examples:**
- `0.1.0` → `0.2.0`: Added 3 new device models
- `0.2.0` → `0.2.1`: Fixed authentication bug
- `0.2.1` → `1.0.0`: Complete rewrite of local protocol

### Pre-Release Checklist

- [ ] All tests pass
- [ ] Version bumped in manifest.json
- [ ] CHANGELOG.md updated
- [ ] README.md updated
- [ ] Documentation reviewed
- [ ] No debug code left in
- [ ] All TODOs addressed or documented
- [ ] Breaking changes documented

### Release Steps

1. **Update version**
```bash
# Edit manifest.json
{
  "version": "0.2.0"
}
```

2. **Update CHANGELOG.md**
```markdown
## [0.2.0] - 2024-01-23

### Added
- Support for Jebao EP Series pumps
- German translation

### Fixed
- Device discovery timeout issue
- Entity naming consistency

### Changed
- Polling interval reduced to 2 seconds
```

3. **Create git tag**
```bash
git add .
git commit -m "Release v0.2.0"
git tag -a v0.2.0 -m "Version 0.2.0 - Added EP Series support"
git push origin main
git push origin v0.2.0
```

4. **Create GitHub release**
- Go to GitHub releases page
- Draft new release
- Select the tag
- Add release notes from CHANGELOG
- Attach any additional files if needed

5. **Announce**
- Update discussion thread
- Post in relevant communities
- Update documentation site

### Post-Release

1. **Monitor issues** - Watch for bug reports
2. **Track metrics** - Downloads, stars, forks
3. **Plan next version** - Collect feature requests
4. **Update roadmap** - Document future plans

---

## Additional Resources

### Useful Links

**Gizwits Platform:**
- Developer Portal: https://dev.gizwits.com/
- API Documentation: https://docs.gizwits.com/
- Forum: https://club.gizwits.com/

**Home Assistant:**
- Developer Docs: https://developers.home-assistant.io/
- Architecture: https://developers.home-assistant.io/docs/architecture_index
- Integration Quality Scale: https://www.home-assistant.io/docs/quality_scale/

**Related Projects:**
- Bestway/Lay-Z-Spa: https://github.com/cdpuk/ha-bestway
- PH-803W Controller: https://github.com/dala318/python_ph803w
- Jebao Dosing Pump: https://github.com/tancou/jebao-dosing-pump-md-4.4

### Community Support

**GitHub:**
- Issues: Report bugs and feature requests
- Discussions: Ask questions, share experiences
- Wiki: Additional documentation

**Home Assistant Community:**
- Forum Thread: [Link to be created]
- Discord: Home Assistant Integration Development channel

### Maintainer Responsibilities

**Regular Tasks:**
- Review and respond to issues
- Merge pull requests
- Update compatibility list
- Monitor Gizwits API changes
- Test with new HA versions

**Quarterly:**
- Review and update documentation
- Audit dependencies
- Plan feature roadmap
- Engage with community

**Annually:**
- Major version planning
- Architecture review
- Security audit
- Performance optimization

---

## Appendix

### Binary Protocol Reference

**Command Structure:**
```
Header: 0x00 0x00 0x00 0x03 (fixed)
Length: LEB128 encoded
Flag: 0x00
Command: 2 bytes
Payload: Variable length
```

**Known Commands:**
- `0x0006`: Get binding key
- `0x0008`: Authenticate
- `0x0093`: Get device status
- `0x0090`: Set device attributes (implemented for MLW local control)

### LEB128 Encoding

Variable-length integer encoding used in protocol:
```python
def encode_leb128(value):
    result = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        result.append(byte)
        if value == 0:
            break
    return bytes(result)
```

### Endianness Handling

Multi-byte values may need byte swapping:
```python
def swap_endian(hex_str):
    """Swap first two bytes if value spans byte boundary"""
    if len(hex_str) >= 4:
        return hex_str[2:4] + hex_str[0:2] + hex_str[4:]
    return hex_str
```

### Device Model Template

Complete template for new device models:

```json
{
  "product_key": "YOUR_PRODUCT_KEY",
  "name": "Device Model Name",
  "attrs": [
    {
      "display_name": "Power Switch",
      "name": "switch",
      "data_type": "bool",
      "position": {
        "byte_offset": 0,
        "bit_offset": 0,
        "len": 1,
        "unit": "bit"
      },
      "type": "status_writable",
      "id": 0,
      "desc": "Controls device power"
    },
    {
      "display_name": "Operating Mode",
      "name": "mode",
      "data_type": "enum",
      "position": {
        "byte_offset": 0,
        "bit_offset": 4,
        "len": 3,
        "unit": "bit"
      },
      "type": "status_writable",
      "id": 1,
      "desc": ["Constant", "Wave", "Pulse", "Feed", "Custom"],
      "enum": ["constant", "wave", "pulse", "feed", "custom"]
    },
    {
      "display_name": "Flow Rate",
      "name": "flow",
      "data_type": "uint8",
      "position": {
        "byte_offset": 1,
        "bit_offset": 0,
        "len": 1,
        "unit": "byte"
      },
      "type": "status_writable",
      "id": 2,
      "desc": "Flow rate percentage",
      "uint_spec": {
        "min": 0,
        "max": 100,
        "ratio": 1,
        "addition": 0
      }
    }
  ]
}
```

---

## Document Version History

- **v1.0** (2024-01-23): Initial maintenance guide created
- Future versions will be documented here

---

## Contact & Support

**Maintainer**: To be assigned  
**Original Author**: @chrisc123  
**Repository**: https://github.com/chrisc123/jebao_aqua-homeassistant  
**Issues**: https://github.com/chrisc123/jebao_aqua-homeassistant/issues

For questions, issues, or contributions, please use GitHub issues and discussions.
