"""Helper functions for Jebao Aqua integration."""

import json
from pathlib import Path
from homeassistant.core import HomeAssistant
from .const import DOMAIN, LOGGER


def parse_channel_names(device: dict) -> dict:
    """Parse custom channel names from device remark field.
    
    Returns a dict mapping channel number to custom name.
    Example: {1: "Peroxide", 2: "Te", 3: "Mg", 4: "Ca", 5: "KH"}
    """
    channel_names = {}
    remark = device.get("remark", "")
    if remark:
        try:
            remark_data = json.loads(remark)
            names = remark_data.get("names", {})
            # Convert CHANNEL_1 format to channel number
            for key, value in names.items():
                if key.startswith("CHANNEL_"):
                    channel_num = int(key.split("_")[1])
                    channel_names[channel_num] = value
            LOGGER.debug(f"Parsed channel names for device {device.get('did')}: {channel_names}")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            LOGGER.debug(f"No custom channel names found or failed to parse: {e}")
    return channel_names


def get_channel_name_from_attribute(attribute_name: str, channel_names: dict) -> str:
    """Extract channel number from attribute name and return custom name if available.
    
    Examples:
    - "channe1" -> returns channel_names[1] or None
    - "Timer1ON" -> returns channel_names[1] or None
    """
    # Try to extract channel number from various formats
    import re
    
    # Match patterns like "channe1", "Timer1ON", etc.
    match = re.search(r'(\d+)', attribute_name)
    if match:
        channel_num = int(match.group(1))
        return channel_names.get(channel_num)
    
    return None


def get_device_info(device, attribute_models=None):
    """Return standardized device information dictionary."""
    # Try to get English name from model file first
    device_name = None
    product_key = device.get("product_key", "")
    
    if attribute_models and product_key in attribute_models:
        model = attribute_models[product_key]
        device_name = model.get("name")
        LOGGER.debug(f"Using English name from model: {device_name}")
    
    # Fall back to dev_alias or default
    if not device_name:
        device_name = device.get("dev_alias") or f"Device {device['did']}"
    
    lan_ip = device.get("lan_ip")

    info = {
        "identifiers": {(DOMAIN, device["did"])},
        "name": device_name,
        "manufacturer": "Jebao",
    }

    if lan_ip:
        info["connections"] = {("ip", lan_ip)}

    LOGGER.debug(f"Device info for {device_name}: {info}")
    return info


async def load_attribute_models(hass: HomeAssistant) -> dict:
    """Load attribute models asynchronously."""
    models_path = Path(hass.config.path("custom_components/jebao_aqua/models"))
    attribute_models = {}

    LOGGER.info(f"Loading attribute models from: {models_path}")

    def _load_model(file_path):
        """Load a single model file."""
        with open(file_path, "r") as file:
            model = json.load(file)
            return model["product_key"], model

    # Load all model files in executor
    for model_file in models_path.glob("*.json"):
        try:
            product_key, model = await hass.async_add_executor_job(
                _load_model, model_file
            )
            attribute_models[product_key] = model
            LOGGER.info(f"Loaded model for product_key: {product_key} from {model_file.name}")
        except Exception as e:
            LOGGER.error(f"Error loading model file {model_file}: {e}")

    LOGGER.info(f"Total models loaded: {len(attribute_models)}")
    LOGGER.info(f"Product keys: {list(attribute_models.keys())}")
    return attribute_models


def create_entity_name(device_name: str, attr_name: str) -> str:
    """Create standardized entity name."""
    # Only return the attribute name since we're using has_entity_name = True
    return attr_name


def create_entity_id(platform: str, device_name: str, attr_name: str) -> str:
    """Create standardized entity ID."""
    device_name_underscore = device_name.replace(" ", "_").lower()
    attr_name_underscore = attr_name.replace(" ", "_").lower()
    return f"{platform}.{device_name_underscore}_{attr_name_underscore}"


def create_unique_id(device_id: str, attr_name: str) -> str:
    """Create standardized unique ID."""
    return f"{device_id}_{attr_name.replace(' ', '_').lower()}"


def is_device_data_valid(device_data: dict) -> bool:
    """Check if device data is valid."""
    LOGGER.debug(f"Checking device data validity: {device_data}")  # Add debug logging
    if not device_data:
        return False
    if not isinstance(device_data, dict):
        return False
    if "attr" not in device_data:
        return False
    if not device_data.get("attr"):  # Add check for empty attr dict
        return False
    return True


def get_attribute_value(device_data: dict, attribute: str):
    """Safely get attribute value from device data."""
    if not is_device_data_valid(device_data):
        return None
    return device_data.get("attr", {}).get(attribute)
