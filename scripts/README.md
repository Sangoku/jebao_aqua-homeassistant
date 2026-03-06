# Scripts

Utility and debug scripts for working with the Jebao Aqua integration.

## fetch_device_models.py

Fetches device model datapoint definitions from the Gizwits API and saves them as JSON files in `custom_components/jebao_aqua/models/`.

```bash
pip install aiohttp
python3 scripts/fetch_device_models.py
```

## test_mode_debug.py

Debug script for reverse-engineering mode switching behaviour on a specific device. Logs all API requests/responses and binary protocol data to a timestamped log file.

See [docs/MODE_DEBUG_INSTRUCTIONS.md](../docs/MODE_DEBUG_INSTRUCTIONS.md) for full usage instructions.

```bash
pip install aiohttp
python3 scripts/test_mode_debug.py
```
