# Home Assistant Custom Integration: Jebao Aquarium Pumps

![Logo](jebao-m-series-pump-controller.png)

This custom integration for Home Assistant allows users to control and monitor certain models of Wi-Fi enabled Jebao Aquarium Wavemakers/Pumps. Currently tested with the M series devices (with white and purple controller), though in theory it should be possible to get working with any device that supports Wi-Fi and makes use of the "Jebao Aqua" app for control.

The integration polls devices via the LAN for status updates and uses the Gizwits Cloud API for remote control.

> _Note: I'm not a developer. This code was almost entirely written by ChatGPT based on my packet captures, the Gizwits documentation and some resources from the mobile app APK. I now realise it doesn't conform to established practices for Home Assistant to directly interface with the API from an integration, but it does work!_

## Compatibility

> [!IMPORTANT]
> As of late 2024, it seems two different hardware versions of some model series may be available. The newer versions include support for Bluetooth (BLE) in addition to WiFi and use an ESP32C3 microcontroller rather than the legacy ESP8266.
> The WiFi+BLE devices do not yet work with this plugin - I'm investigating what's changed in the communication protocol and hope to add support soon.

| Device Model | Compatibility |
|---|---|
| Jebao MCP Series Crossflow Wavemaker | ✅ Tested and working |
| Jebao MLW Series Wavemaker | ✅ Tested and working (see [known limitations](MAINTENANCE_GUIDE.md#known-device-limitations)) |
| Jebao MLW-20 Wavemaker | ✅ Added - WiFi only model |
| Jebao SLW Series Wavemaker | ⚠️ Added but not confirmed working |
| Jebao EP Series Pump | ⚠️ Added but not confirmed working |
| Jebao Smart Doser 3.1 | ✅ Added by @jeffcybulski |
| Jebao MD 2.4 Dosing Pump | ✅ Added by @joluan01 |
| Jebao MD 4.4 Dosing Pump | ✅ Added by @jeffcybulski |
| Jebao MD 4.5 Smart Doser | ✅ Added - 5 channel model |
| Generic Wavemaker Pump | ✅ Added - basic wavemaker support |
| Any WiFi+Bluetooth enabled Jebao device | ❌ Not working but under investigation |
| Other Jebao Pumps | Not tested |


## Background

* The pump control unit houses an Espressif ESP8266 microcontroller running a version of the [Gizwits GAgent](https://docs.gizwits.com/en-us/DeviceDev/GAgent.html#Features) firmware.
* Both the mobile app and pumps communicate exclusively with Gizwits cloud — there is no indication of any Jebao-specific infrastructure in use.
* Gizwits is "The largest IoT development platform in Asia". The [Bestway/Lay-Z-Spa](https://github.com/cdpuk/ha-bestway) and [PH-803W pH Controller](https://github.com/dala318/python_ph803w) projects are examples of other Home Assistant integrations that interact with the Gizwits platform.
* Local interface on TCP/12416 — cloud helpfully provides payload structure.
* TODO: Devices appear to use unencrypted MQTT between device and cloud — it _might_ be possible to reconfigure devices to point to an arbitrary MQTT server.


## Features

- Control Jebao Aquarium Pumps remotely via the Gizwits API.
- Poll device status locally for real-time updates (primarily to avoid excessive cloud requests, but also provides faster response to control commands).
- Supports switches, sensors, selectors, and numeric inputs for comprehensive control.
- Custom channel names for dosing pumps (read from device `remark` field set by the Jebao app).
- Diagnostic sensors showing device IP, MAC, firmware versions, and online status.
- Does not support the native 'scheduling' features from the app — use HA automations instead.

**TODO:**
- LAN IP Auto discovery — easy at a protocol level, just need to figure out how to get a Home Assistant integration to listen for UDP packets on a given port.
- Local Control — In theory it would be more robust to avoid interacting with the Gizwits API at all. Currently we use the local interface for _polling_ but not for _control_. See: https://github.com/tancou/jebao-dosing-pump-md-4.4


## Installation

### Via HACS

Add this repository as a custom repository in HACS, then install "Jebao Aqua Aquarium Pump".

### Manual Installation

1. The pumps must already be set up with the Jebao Aqua app and connected to a Wi-Fi network routable from your Home Assistant installation.
2. Note down the local IP addresses of your pumps using the app (from the individual pump control interface, enter "Settings" via the icon in the top right, then view "Device Information").
3. Copy the `custom_components/jebao_aqua` directory to your Home Assistant `custom_components` directory.
4. Add the "Jebao Aqua Aquarium Pump" integration via the Home Assistant integrations dashboard. You'll be prompted to enter your Jebao Aqua app login details. The integration will discover devices linked to your account and ask you to provide the local IP for each.


## Usage

Once installed and configured, the integration allows you to:

- Turn pumps on and off.
- Adjust flow, frequency, and mode settings.
- Monitor status and fault indicators.
- View dosing schedules and daily totals (MD-4.5 doser).


## Troubleshooting

If you encounter issues, enable debug logging and check the Home Assistant logs:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.jebao_aqua: debug
```

You can also raise an issue in this repository.

For known device-specific limitations (especially MLW series), see the [Known Device Limitations](MAINTENANCE_GUIDE.md#known-device-limitations) section of the maintenance guide.


## Documentation

| Document | Purpose |
|---|---|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development environment setup, workflow, and contribution guide |
| [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md) | Architecture, code structure, adding devices, troubleshooting |
| [docs/](docs/) | Implementation notes, fix history, and investigation logs |


## Adding New Device Models

Each device needs a JSON file in `custom_components/jebao_aqua/models/` named by its Gizwits `product_key`. See [Adding New Device Models](MAINTENANCE_GUIDE.md#adding-new-device-models) in the maintenance guide, or use `scripts/fetch_device_models.py` to fetch the raw datapoint definition from the Gizwits API.
