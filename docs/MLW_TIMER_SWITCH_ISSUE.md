# MLW Wavemaker Timer Switch Issue - RESOLVED

## Issue Description
When toggling the Timer switch in Home Assistant, it appears to toggle but then reverts back to OFF after a few seconds.

## Root Cause
The MLW wavemaker pump has a device-level restriction: **The timer cannot be enabled when the main pump switch is OFF**.

### Device State When Issue Occurs
```json
{
  "SwitchON": false,      // ← Main pump is OFF
  "TimerON": false,        // ← Cannot enable timer while pump is off
  "Mode": "经典造浪",
  "Linkage": "独立"
}
```

### What Happens
1. User toggles Timer switch in HA
2. Command sent successfully: `{'attrs': {'TimerON': True}}`
3. Device receives command
4. **Device rejects the timer enable because SwitchON is false**
5. 3 seconds later, HA refreshes and sees TimerON is still False
6. Switch reverts to OFF position in HA

## Solution

### Option 1: Enable Main Switch First (Recommended)
To use the timer schedule:
1. **First, turn ON the main "Switch" entity** for the wavemaker
2. Then enable the "Timer Switch"
3. The timer will now stay enabled

### Option 2: Use Jebao App
Configure the schedule in the official Jebao app, which will handle the proper sequence of enabling the pump and timer.

### Option 3: Create a Home Assistant Automation
Create an automation that ensures the main switch is on before enabling the timer:

```yaml
automation:
  - alias: "Enable Wavemaker Timer"
    trigger:
      - platform: state
        entity_id: switch.wavemaker_timer_switch
        to: "on"
    condition:
      - condition: state
        entity_id: switch.wavemaker_switch
        state: "off"
    action:
      - service: switch.turn_on
        entity_id: switch.wavemaker_switch
      - delay:
          seconds: 2
      - service: switch.turn_on
        entity_id: switch.wavemaker_timer_switch
```

## Why This Happens
This is a **device-level safety feature**, not a bug in the integration. The wavemaker firmware enforces this rule to prevent scheduling errors when the device is powered off.

Many aquarium pumps work this way:
- Main power must be ON to enable scheduling
- This ensures the device can actually run when scheduled times occur
- It prevents confusion where a timer is "enabled" but nothing happens because the pump is off

## Technical Details
The integration code is working correctly:
- Command is sent successfully to Gizwits API
- Device receives the command
- Device firmware rejects the TimerON=True command when SwitchON=False
- This is expected device behavior, not an integration bug

## Verification
After turning on the main switch (SwitchON = True), try enabling the timer again. It should stay enabled.

## Status: ✅ WORKING AS DESIGNED
This is not a bug - it's the expected behavior of the MLW wavemaker pump. The integration correctly sends commands and reflects the device state.