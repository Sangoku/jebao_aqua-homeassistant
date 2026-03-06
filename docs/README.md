# Implementation Notes & Fix History

This directory contains detailed notes from development sessions, bug investigations, and feature implementations. These are preserved for historical context and deep-dive reference.

## Contents

### MLW Series Wavemaker

| File | Description |
|------|-------------|
| [MLW_WAVEMAKER_IMPLEMENTATION.md](MLW_WAVEMAKER_IMPLEMENTATION.md) | MLW device entity status and implementation overview |
| [MLW_PROTOCOL_INVESTIGATION.md](MLW_PROTOCOL_INVESTIGATION.md) | Investigation into why MLW only sends 1 byte of status data |
| [MLW_MODE_SELECTOR_FIX.md](MLW_MODE_SELECTOR_FIX.md) | How mode selection was fixed to use local UDP protocol |
| [MLW_STATE_UPDATE_FIX.md](MLW_STATE_UPDATE_FIX.md) | Fix for state not reflecting in HA UI after commands |
| [MLW_TIMER_SWITCH_ISSUE.md](MLW_TIMER_SWITCH_ISSUE.md) | Timer switch behaviour (device-level restriction, not a bug) |

### Feature Implementations

| File | Description |
|------|-------------|
| [SCHEDULE_SENSORS_IMPLEMENTATION.md](SCHEDULE_SENSORS_IMPLEMENTATION.md) | MD-4.5 doser schedule sensors (CHxSWTime decoding) |
| [CHANNEL_NAMES_IMPLEMENTATION.md](CHANNEL_NAMES_IMPLEMENTATION.md) | Custom channel names from device `remark` field |
| [DEVICE_INFO_SENSORS.md](DEVICE_INFO_SENSORS.md) | Diagnostic sensors for IP, MAC, firmware versions |

### Bug Fixes

| File | Description |
|------|-------------|
| [INTEGRATION_FIXES.md](INTEGRATION_FIXES.md) | Payload parsing fix, missing model fallback, Docker log mounting |
| [INTEGRATION_STATUS_SUMMARY.md](INTEGRATION_STATUS_SUMMARY.md) | Status summary after initial fixes (Jan 2026) |
| [DEVICE_NAME_FIX.md](DEVICE_NAME_FIX.md) | Fix for Chinese device names causing initialization failures |

### Development Tools

| File | Description |
|------|-------------|
| [MODE_DEBUG_INSTRUCTIONS.md](MODE_DEBUG_INSTRUCTIONS.md) | Instructions for using the mode debug script |
| [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) | Original detailed Docker development setup guide |
| [QUICK_START.md](QUICK_START.md) | Original quick-start maintainer reference |
| [START_HERE.md](START_HERE.md) | Original 5-minute getting started guide |

---

For current documentation, see the root-level [README.md](../README.md), [CONTRIBUTING.md](../CONTRIBUTING.md), and [MAINTENANCE_GUIDE.md](../MAINTENANCE_GUIDE.md).
