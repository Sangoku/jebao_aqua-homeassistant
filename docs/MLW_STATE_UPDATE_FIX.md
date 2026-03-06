# MLW Wavemaker State Update Fix

## Issue Description
Device 54114ccdac1e41c0bb17e222887c07ba (MLW Wavemaker) was not reflecting state changes in the Home Assistant GUI. Commands were being sent successfully, but the frontend did not update to show the new state.

## Root Cause Analysis

The issue had two components:

1. **Command Response Delay**: After sending commands via the Gizwits API, there was a significant delay before the device state was updated and available for polling. The previous implementation only waited 3 seconds for switches and didn't wait at all for select/number entities.

2. **Coordinator Update Propagation**: While the coordinator was polling the device every 2 seconds (`UPDATE_INTERVAL`), entities were not explicitly triggering UI state writes when coordinator data changed. The default `CoordinatorEntity` behavior wasn't sufficient for this device.

## Solution Implemented

### Two-Part Fix

#### 1. Explicit State Updates on Coordinator Refresh
Added `_handle_coordinator_update()` method to all entity types (switch, select, number) that:
- Logs coordinator updates for debugging
- Calls parent class handler
- Explicitly calls `async_write_ha_state()` to force UI updates

This ensures state changes from:
- Initial load
- Regular coordinator polling (every 2 seconds)
- External changes (via mobile app)

Are properly reflected in the Home Assistant frontend.

#### 2. Command Polling with Retries
Updated command methods in all entity types to:
- Send command to device
- Wait 5 seconds for device to process
- Poll up to 3 times (every 2 seconds) to verify state change
- Log detailed information about verification attempts
- Warn if state doesn't update after all attempts

**Timing Configuration:**
- Initial wait: 5 seconds
- Polling attempts: 3 attempts × 2 seconds each
- Maximum wait: 11 seconds (5s + 3×2s)
- Typical success: 7-9 seconds

## Files Modified

### 1. `custom_components/jebao_aqua/switch.py`
- Added `import asyncio`
- Added `_handle_coordinator_update()` method
- Updated `async_turn_on()` with 5s wait + 3×2s polling
- Updated `async_turn_off()` with 5s wait + 3×2s polling
- Added comprehensive debug logging

### 2. `custom_components/jebao_aqua/select.py`
- Added `import asyncio`
- Added `_handle_coordinator_update()` method
- Updated `async_select_option()` with 5s wait + 3×2s polling
- Added comprehensive debug logging

### 3. `custom_components/jebao_aqua/number.py`
- Added `import asyncio`
- Added `_handle_coordinator_update()` method
- Updated `async_set_native_value()` with 5s wait + 3×2s polling
- Added comprehensive debug logging

## Testing Instructions

### 1. Restart Home Assistant
After implementing these changes, restart Home Assistant to reload the integration:
```bash
# From Home Assistant UI: Settings > System > Restart
# Or via CLI:
ha core restart
```

### 2. Enable Debug Logging
Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.jebao_aqua: debug
```

Then restart Home Assistant again.

### 3. Test Scenarios

#### Test 1: Initial State Load
1. Restart Home Assistant
2. Check logs for "Coordinator update" messages
3. Verify all entity states are correct in the UI

#### Test 2: Home Assistant Commands
1. Toggle a switch (e.g., Switch ON)
2. Watch logs for:
   - "Sending turn_on command"
   - "Polling attempt 1/2/3"
   - "Switch state verified"
3. Verify UI updates within 7-11 seconds
4. Repeat for select entities (Mode, Linkage)
5. Repeat for number entities (Flow, Frequency, Feeding Time)

#### Test 3: External Changes (Mobile App)
1. Change device state via Jebao mobile app
2. Within 2-4 seconds, check if HA UI reflects the change
3. Check logs for "Coordinator update" messages
4. Verify state is correct

#### Test 4: Rapid Commands
1. Send multiple commands quickly
2. Verify each command is processed
3. Check logs for any warnings or errors

### 4. Expected Log Output

**Successful Command:**
```
[custom_components.jebao_aqua.switch] Sending turn_on command for fw1iMEpzecdyMiKjdtt7hS Switch
[custom_components.jebao_aqua.switch] Polling attempt 1 for fw1iMEpzecdyMiKjdtt7hS Switch: current_value=False
[custom_components.jebao_aqua.switch] Polling attempt 2 for fw1iMEpzecdyMiKjdtt7hS Switch: current_value=True
[custom_components.jebao_aqua.switch] Switch fw1iMEpzecdyMiKjdtt7hS Switch state verified as ON after 2 attempts
```

**Coordinator Update:**
```
[custom_components.jebao_aqua.switch] Coordinator update for switch fw1iMEpzecdyMiKjdtt7hS Switch (SwitchON): device_data={'did': 'fw1iMEpzecdyMiKjdtt7hS', 'attr': {'SwitchON': True, ...}}
```

**Failed Update (Warning):**
```
[custom_components.jebao_aqua.switch] Switch fw1iMEpzecdyMiKjdtt7hS Switch state did not update to ON after 3 polling attempts
```

## Benefits

1. ✅ **Reliable State Updates**: Multiple polling attempts catch delayed device responses
2. ✅ **External Changes**: Coordinator polling ensures app changes are reflected
3. ✅ **Debug Visibility**: Comprehensive logging helps troubleshoot issues
4. ✅ **User Feedback**: Users see state changes within 7-11 seconds
5. ✅ **Graceful Degradation**: System continues working even if state verification fails

## Potential Issues & Solutions

### Issue: Commands take too long (>11 seconds)
**Solution**: Increase polling attempts or wait times in the entity files:
- Change `await asyncio.sleep(5)` to a longer value
- Change `range(3)` to `range(4)` or `range(5)`
- Change `await asyncio.sleep(2)` between polls to a longer value

### Issue: Too many log messages
**Solution**: Change logging level back to `info` in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.jebao_aqua: info
```

### Issue: State never updates
**Potential causes**:
1. Device is offline or not responding
2. API credentials expired
3. Network connectivity issues
4. Device firmware issue

**Debug steps**:
1. Check device is online in Jebao app
2. Verify Home Assistant can reach the device (check network)
3. Check coordinator logs for API errors
4. Try reloading the integration

## Performance Considerations

- **Network Load**: Each command triggers 3-4 API requests over 5-11 seconds
- **Coordinator Load**: Continues polling every 2 seconds (unchanged)
- **User Experience**: 7-11 second delay for command feedback is acceptable for this type of device
- **Concurrent Commands**: Multiple entities can be controlled simultaneously without conflicts due to per-device locks in coordinator

## Future Improvements

1. **Optimistic Updates**: Could implement immediate UI feedback with verification
2. **Device-Specific Timing**: Could add timing configuration to device model files
3. **Websocket Support**: If Gizwits adds websocket support, could use push notifications instead of polling
4. **Adaptive Polling**: Could adjust polling frequency based on success rates

## Related Files

- `MLW_WAVEMAKER_IMPLEMENTATION.md` - Original device implementation docs
- `custom_components/jebao_aqua/const.py` - Contains `UPDATE_INTERVAL = timedelta(seconds=2)`
- `custom_components/jebao_aqua/__init__.py` - Contains coordinator implementation
- `custom_components/jebao_aqua/api.py` - Contains API communication methods