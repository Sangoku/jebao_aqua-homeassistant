from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, LOGGER
from .helpers import (
    get_device_info,
    create_entity_name,
    create_entity_id,
    create_unique_id,
    is_device_data_valid,
    get_attribute_value,
    parse_channel_names,
    get_channel_name_from_attribute,
)


class JebaoPumpSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Jebao Pump Sensor."""

    def __init__(self, coordinator, device, attribute, attribute_models, custom_name=None):
        super().__init__(coordinator)
        self._device = device
        self._attribute = attribute
        self._attribute_models = attribute_models
        device_id = device.get("did")
        device_name = device.get("dev_alias") or device.get("did")

        # Use custom name if provided, otherwise use display_name
        display_name = custom_name if custom_name else attribute["display_name"]
        
        # Use helper functions for consistent entity properties
        self._attr_name = create_entity_name(device_name, display_name)
        self._attr_unique_id = create_unique_id(device_id, attribute["name"])
        self.entity_id = create_entity_id(
            "binary_sensor", device_name, attribute["name"]
        )

    @property
    def device_class(self):
        """Return the class of this device."""
        # Use RUNNING device class for channel status sensors, PROBLEM for faults
        if self._attribute["name"].startswith("channe"):
            return BinarySensorDeviceClass.RUNNING
        return BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        device_data = self.coordinator.device_data.get(self._device["did"])
        return get_attribute_value(device_data, self._attribute["name"]) or False

    @property
    def device_info(self):
        """Return information about the device this entity belongs to."""
        return get_device_info(self._device, self._attribute_models)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device_data = self.coordinator.device_data.get(self._device["did"])
        return is_device_data_valid(device_data)

    @property
    def name(self) -> str:
        """Return the display name of this entity."""
        return self._attr_name

    @property
    def has_entity_name(self) -> bool:
        """Indicate that we are using the device name as the entity name."""
        return True

    @property
    def translation_key(self) -> str:
        """Return the translation key to use in logbook."""
        return self._attribute["name"].lower()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Jebao Pump sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    attribute_models = hass.data[DOMAIN][entry.entry_id]["attribute_models"]

    sensors = []
    for device in coordinator.device_inventory:  # Use device_inventory for the setup
        LOGGER.debug("Device structure: %s", device)
        product_key = device.get("product_key")
        model = attribute_models.get(product_key)

        # Parse custom channel names for this device
        channel_names = parse_channel_names(device)

        if model:
            for attr in model["attrs"]:
                # Create binary sensors for fault attributes and readonly status attributes (like channel running status)
                if attr["data_type"] == "bool" and (attr["type"] == "fault" or attr["type"] == "status_readonly"):
                    # Check if this is a channel status sensor and if we have a custom name
                    custom_name = None
                    if attr["name"].startswith("channe"):
                        channel_name = get_channel_name_from_attribute(attr["name"], channel_names)
                        if channel_name:
                            custom_name = f"{channel_name} Status"
                    
                    sensors.append(JebaoPumpSensor(coordinator, device, attr, attribute_models, custom_name))

    async_add_entities(sensors)
