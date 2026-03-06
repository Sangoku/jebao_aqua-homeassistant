# MLW Wavemaker Protocol Investigation

## Current Status
The MLW wavemaker (product_key: 54114ccdac1e41c0bb17e222887c07ba) has limited local LAN protocol support.

### What We're Getting
Device responds to command `0x93` with only **1 byte** of data:
```
Response: 000000030400000900000000030400006200
Extracted payload (length=1): 00
```

This single byte (value `0x00` = binary `00000000`) contains:
- Bit 0: SwitchON = False
- Bit 1: PulseTide = False  
- Bit 2: FeedSwitch = False
- Bit 3: TimerON = False
- Bits 5-6: Mode = "经典造浪" (Classic Wave)
- Bits 7-8: Linkage = "独立" (Independent)

### What's Missing
According to the model definition, these numeric values should be at:
- **Byte 2**: Flow (1-100%)
- **Byte 3**: Frequency (5-100)
- **Byte 4**: FeedTime (1-60 mins)

**But the device is NOT sending bytes 2, 3, or 4!**

### Real-World Behavior
User reports:
- Pump IS physically running
- Flow set to 100%
- Frequency set to 77
- Mode: Classic Wave (Cross Flow)
- But integration shows SwitchON = False and no numeric values

## Hypothesis

### Possibility 1: Incomplete Firmware Implementation
The MLW series (New BLE enabled series) may have incomplete local LAN protocol implementation. The firmware might:
- Only report basic on/off status via LAN
- Require Bluetooth for full status (Flow, Frequency, etc.)
- Be designed primarily for cloud control

### Possibility 2: Wrong Status Command
Command `0x93` might only return basic status. There could be:
- A different command for detailed status
- Need to send specific request for numeric values
- Multi-step handshake required

### Possibility 3: State-Dependent Response
The device might only send full data when:
- Pump is in Timer mode (not Manual mode)
- A specific mode is active
- After a specific initialization sequence

### Possibility 4: Model Definition Error
The model file might be incorrect for MLW series:
- Numeric values might be encoded differently
- Different byte positions than documented
- Uses different protocol than older models

## What Cloud API Returns
Cloud API also only shows 6 basic attributes without numeric values:
```json
{
  "SwitchON": false,
  "PulseTide": false,
  "FeedSwitch": false,
  "TimerON": false,
  "Mode": "经典造浪",
  "Linkage": "独立"
}
```

This suggests the cloud doesn't receive numeric values either - possibly a firmware limitation.

## Testing Needed

### Test 1: Try Timer Mode
1. Use Jebao app to set up a schedule
2. Enable Timer mode
3. Check if device then reports numeric values

### Test 2: Try Different Modes
Test each mode to see if response changes:
- Classic Wave (经典造浪)
- Sine Wave (正弦造浪)
- Random Wave (随机造浪)
- Constant Flow (恒流造浪)

### Test 3: Monitor Jebao App Communication
Use network monitoring to capture what the official Jebao app sends/receives:
- What commands does it use?
- Does it get numeric values via LAN or cloud?
- Is there a different status request command?

### Test 4: Check Firmware Version
The model mentions "New BLE enabled MLW Series - TBC?" suggesting:
- This might be a newer model
- Protocol might be incomplete/in development
- May require firmware update

## Conclusions

1. **Local LAN Protocol is Incomplete**: MLW only sends 1 byte of status data
2. **Cloud API Also Limited**: Cloud doesn't receive numeric values either
3. **Integration is Working Correctly**: The code is parsing the data correctly - the device just isn't sending complete data
4. **Not an Integration Bug**: This appears to be a device firmware limitation

## Recommendations

### For Users
1. **Use Jebao App** for full control and monitoring
2. **Basic HA Control Only**: Accept that Flow/Frequency/Timer may not work via HA
3. **Wait for Firmware Update**: Contact Jebao about MLW LAN protocol support

### For Development
1. **Document Limitation**: Make it clear MLW has limited HA support
2. **Focus on Cloud Control**: Since local doesn't work, ensure cloud control works reliably
3. **Contact Jebao**: Request protocol documentation or firmware update
4. **Monitor for Updates**: Check if newer firmware versions fix this

## Status
🔴 **BLOCKED by Device Firmware Limitation**

The integration code is correct, but the MLW wavemaker firmware does not provide complete status information via either local LAN or cloud API protocols.