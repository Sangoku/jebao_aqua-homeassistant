# Mode Debug Script Instructions

## Overview
This script helps debug and reverse engineer the mode switching behavior of your Jebao Aqua Wavemaker device.

**Device Details:**
- Device Name: 1.0 W_8AE4F4
- IP Address: 192.168.0.237
- Device ID: fw1iMEpzecdyMiKjdtt7hS
- Product Key: 54114ccdac1e41c0bb17e222887c07ba

## What the Script Does

The debug script will:
1. **Login** to the Gizwits cloud API
2. **Read current status** of the device (including current mode)
3. **Test each mode** (0-3) by sending control commands
4. **Verify changes** by reading the status back from the API
5. **Test local TCP connection** to examine raw protocol data
6. **Log everything** to a timestamped log file for analysis

## Modes Being Tested

According to the device model, there are 4 modes:
- **Mode 0**: 经典造浪 (Square Wave / Classic) - **THIS IS THE PROBLEMATIC ONE**
- **Mode 1**: 正弦造浪 (Sine Wave)
- **Mode 2**: 随机造浪 (Random Wave)  
- **Mode 3**: 恒流造浪 (Constant Flow)

## How to Run

### 1. Install Dependencies
```bash
pip install aiohttp
```

### 2. Make the Script Executable
```bash
chmod +x test_mode_debug.py
```

### 3. Run the Script
```bash
python3 test_mode_debug.py
```

### 4. During Execution
The script will:
- Ask for your Gizwits email and password (used to login to the cloud API)
- Display the current device status
- For each mode (0, 1, 2, 3):
  - Send the mode change command
  - Wait 3 seconds
  - Read back the status to verify
  - **PAUSE** and ask you to press Enter before testing the next mode
  
**IMPORTANT**: During each pause, check your Jebao app to see if the device actually changed modes!

### 5. What to Monitor

While the script runs, keep the Jebao mobile app open and watch for:
- Does the mode indicator change in the app?
- Does the pump behavior change (sound, flow pattern)?
- Is there any error or notification in the app?

## Output Files

The script creates a log file: `mode_debug_YYYYMMDD_HHMMSS.log`

This file contains:
- All API requests and responses (headers, body, status codes)
- Binary protocol data from local TCP connection
- Parsed device status bytes showing bit-level details
- All mode change attempts and their results

## What to Look For

### In the Console Output:
- ✓ = Success
- ✗ = Failure
- Check if API confirms mode changes
- Note which modes work and which don't

### In the App:
- Does "Classic Mode" (Mode 0) actually activate?
- Do other modes work correctly?
- Any error messages or unusual behavior?

### In the Log File:
- Look for differences in API responses between working and non-working modes
- Check the raw byte data from local connection to see actual device state
- Compare what the API reports vs. what the device shows in the app

## Interpreting Results

The script parses byte 0 of the device status, which contains multiple flags:
```
Byte 0 bits:
- Bit 0: SwitchON (pump on/off)
- Bit 1: PulseTide (pulse vs tidal wave)
- Bit 2: FeedSwitch (feeding mode)
- Bit 3: TimerON (timer enabled)
- Bits 5-6: Mode (00=Classic, 01=Sine, 10=Random, 11=Constant)
- Bits 7-8: Linkage (Independent/Primary/Secondary)
```

## Expected Behavior

**If working correctly:**
- API returns status 200 for all mode changes
- Device mode in app matches the requested mode
- Bit analysis shows mode bits changing correctly

**If Classic Mode (0) is broken:**
- API might return 200 but device doesn't respond
- App shows different mode than what was requested
- Device may ignore the command entirely
- Bit analysis might show mode bits stuck or not updating

## Next Steps After Testing

Based on the results:
1. If API returns errors → Cloud API issue
2. If API succeeds but device doesn't respond → Local device firmware issue
3. If mode bits don't change → Protocol encoding issue
4. If app shows different mode → UI/mapping issue in the app

Share the log file and your observations to help diagnose the issue!

## Troubleshooting

**Connection timeout:**
- Verify device IP address (192.168.0.237) is correct
- Ensure device is on the same network
- Check firewall settings

**Login failed:**
- Verify email and password are correct
- Check if Gizwits account is active
- Try logging into the mobile app first

**Permission denied:**
- Run `chmod +x test_mode_debug.py`
- Or use `python3 test_mode_debug.py` instead

**Module not found:**
- Install aiohttp: `pip install aiohttp`
- Ensure Python 3.7+ is being used