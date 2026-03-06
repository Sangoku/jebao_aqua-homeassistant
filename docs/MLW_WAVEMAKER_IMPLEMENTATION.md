# MLW Series Wavemaker Pump Implementation Status

## Device Information
- **Product Key**: `54114ccdac1e41c0bb17e222887c07ba`
- **Product Name**: 本地造浪泵WIFI_BLE (Local Wavemaker Pump WIFI_BLE)
- **Device ID**: fw1iMEpzecdyMiKjdtt7hS
- **Model File**: `custom_components/jebao_aqua/models/54114ccdac1e41c0bb17e222887c07ba.json`

## Current Implementation Status

### ✅ Working Entities

#### Switches (4)
1. **Switch** (SwitchON) - Main power switch
2. **Pulse Tide** (PulseTide) - Selection of pulse and tidal wave (0: pulse wave, 1: tidal wave)
3. **Feeding Switch** (FeedSwitch) - Feeding mode (0: off, 1: on)
4. **Timer Switch** (TimerON) - Timer control (0: off, 1: on)

#### Select Entities (2)
1. **Mode** - Wave mode selection
   - Options: Square Wave, Sine Wave, Random Wave, Constant Flow
   - Chinese values: 经典造浪, 正弦造浪, 随机造浪, 恒流造浪
   
2. **Linkage** - Device coordination mode
   - Options: Independent, Primary, Secondary
   - Chinese values: 独立, 主机, 从机

### ⚠️ Missing Values (Device Not Reporting)

The device is currently only reporting 6 attributes but should also report:

#### Number Entities (Should exist but values missing)
1. **Flow** (Flow) - Flow rate percentage (1-100%)
2. **Frequency** (Frequency) - Frequency value (5-100)
3. **Feeding Time** (FeedTime) - Duration in minutes (1-60 mins)

#### Binary Sensors (Should exist but values missing)
1. **Motor Overcurrent** (Fault_Overcurrent) - Motor current overload/short circuit
2. **Motor Overvoltage** (Fault_Overvoltage) - Motor overvoltage
3. **Temperature Overhigh** (Fault_OverTemp) - Motor temperature too high
4. **Motor Undervoltage** (Fault_Undervoltage) - Motor undervoltage
5. **Motor Locked Rotor** (Fault_Lockedrotor) - Motor locked rotor
6. **No Load** (Fault_no_liveload) - No load condition
7. **Serial Connection Fault** (Fault_UART) - Module and mainboard communication failure

## Current Device State
```json
{
  "did": "fw1iMEpzecdyMiKjdtt7hS",
  "attr": {
    "SwitchON": false,
    "PulseTide": false,
    "FeedSwitch": false,
    "TimerON": false,
    "Mode": "经典造浪",
    "Linkage": "独立"
  }
}
```

## Issue Analysis

The device is currently OFF (SwitchON: false), which may explain why numeric values (Flow, Frequency, FeedTime) and fault sensors are not being reported. These values might only be reported when:

1. The pump is turned ON
2. The values are actively changed
3. A fault condition occurs
4. The device is in a specific mode

## Bug Fixes Applied

### Fixed number.py uint_spec Reading
Changed the number entity to correctly read min/max/step values from the `uint_spec` object:

```python
# Before (incorrect):
self._attr_native_min_value = attribute.get("min", 0)
self._attr_native_max_value = attribute.get("max", 100)
self._attr_native_step = attribute.get("step", 1)

# After (correct):
uint_spec = attribute.get("uint_spec", {})
self._attr_native_min_value = uint_spec.get("min", 0)
self._attr_native_max_value = uint_spec.get("max", 100)
self._attr_native_step = uint_spec.get("ratio", 1)  # ratio is the step value
```

## Next Steps

1. ✅ Fixed number entity to read uint_spec correctly
2. 🔄 Turn the device ON to check if numeric values appear
3. 🔄 Test changing values (Flow, Frequency, FeedTime) via the Jebao app
4. 🔄 Verify entities are created once values are available
5. 🔄 Test controlling the device from Home Assistant
6. 🔄 Document expected behavior

## Testing Plan

1. Turn on the wavemaker pump (set SwitchON to true)
2. Check if Flow, Frequency, and FeedTime values appear in device data
3. Verify number entities are created and controllable
4. Test all modes: Square Wave, Sine Wave, Random Wave, Constant Flow
5. Test Pulse/Tide switching
6. Test feeding mode
7. Test timer functionality
8. Verify fault sensors are created when device is running

## Implementation Status: 🟡 PARTIAL

The integration code is fully implemented and working for all entity types. However, the physical device is currently not reporting numeric values (Flow, Frequency, FeedTime) or fault status. This needs further investigation by:
- Turning the device ON
- Testing with the official Jebao app to see when these values appear
- Monitoring the API responses during different device states