"""Sensor platform for Jebao Aqua."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jebao Aqua sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    # Iterate through device inventory to get product_key
    for device_info in coordinator.device_inventory:
        device_id = device_info.get("did")
        product_key = device_info.get("product_key")
        
        # Check if this is an MD-4.5 doser with schedule data
        if product_key == "5ab6019f2dbb4ae7a42b48d2b8ce0530":
            # Create schedule sensors for each channel
            for channel in range(1, 6):  # Channels 1-5
                entities.append(
                    JebaoChannelScheduleSensor(coordinator, device_id, channel)
                )
    
    if entities:
        async_add_entities(entities)


class JebaoChannelScheduleSensor(SensorEntity):
    """Sensor showing channel dosing schedule."""

    def __init__(self, coordinator, device_id: str, channel: int) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._device_id = device_id
        self._channel = channel
        self._attr_name = f"Channel {channel} Schedule"
        self._attr_unique_id = f"{device_id}_ch{channel}_schedule"
        
    @property
    def device_info(self):
        """Return device information."""
        device = self._coordinator.data.get(self._device_id, {})
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": device.get("dev_alias", f"Jebao {self._device_id}"),
            "manufacturer": "Jebao",
            "model": device.get("product_name", "Unknown"),
        }

    @property
    def state(self) -> str:
        """Return the state."""
        schedule_data = self._parse_schedule()
        if not schedule_data:
            return "Not configured"
        
        # Calculate total daily volume
        total_ml = sum(entry["dose_ml"] for entry in schedule_data)
        return f"{total_ml} mL/day"
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        schedule_data = self._parse_schedule()
        
        # Calculate totals
        total_doses = len(schedule_data)
        total_ml = sum(entry["dose_ml"] for entry in schedule_data) if schedule_data else 0
        
        attrs = {
            "channel": self._channel,
            "total_doses_per_day": total_doses,
            "total_volume_ml_per_day": total_ml,
            "schedule_entries": schedule_data,
            "raw_data": self._get_raw_schedule(),
        }
        return attrs
    
    def _get_raw_schedule(self) -> str:
        """Get raw CHxSWTime data."""
        device = self._coordinator.data.get(self._device_id, {})
        attr = device.get("attr", {})
        field_name = f"CH{self._channel}SWTime"
        return attr.get(field_name, "")
    
    def _parse_schedule(self) -> list[dict]:
        """Parse CHxSWTime hex string into schedule entries."""
        raw = self._get_raw_schedule()
        if not raw or raw == "0" * len(raw):
            return []
        
        entries = []
        # Parse hex string in 12-character (6-byte) blocks
        for i in range(0, min(len(raw), 240), 12):  # Max 20 entries
            block = raw[i:i+12]
            if block == "0" * 12:
                break  # End of schedule entries
                
            try:
                # Parse bytes
                hour = int(block[0:2], 16)
                minute = int(block[2:4], 16) 
                unknown1 = int(block[4:6], 16)
                value = int(block[6:8], 16)
                unknown2 = int(block[8:10], 16)
                unknown3 = int(block[10:12], 16)
                
                # Only add if hour seems valid (0-23)
                if 0 <= hour <= 23:
                    entries.append({
                        "time": f"{hour:02d}:{minute:02d}",
                        "dose_ml": value,
                        "raw": block,
                    })
            except ValueError:
                continue
        
        return entries
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._device_id in self._coordinator.data

    async def async_update(self):
        """Update the sensor."""
        await self._coordinator.async_request_refresh()