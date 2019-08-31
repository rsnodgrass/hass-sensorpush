"""
SensorPush Home Assistant sensors

FUTURE:
- support celsius and fahrenheit (based on cloud setup)
- convert to async
"""
import logging

from homeassistant.const import ( TEMP_FAHRENHEIT, ATTR_TEMPERATURE )
from . import SensorPushService, SensorPushEntity

LOG = logging.getLogger(__name__)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_sensors_callback, discovery_info=None):
    """Setup the SensorPush sensor"""
    service = SensorPushService(config)

    # FUTURE: support multiple sensors
    sensors = []
    sensors.append(SensorPushTemperature(service, device_id))
    sensors.append(SensorPushHumidity(service, device_id))

    for sensor in sensors:
        sensor.update()

    # execute callback to add new entities
    add_sensors_callback(sensors)

# pylint: disable=too-many-instance-attributes
class SensorPushHumidity(SensorPushEntity):
    """Humidity sensor for a SensorPush device"""

    def __init__(self, sensorpush_service, device_id):
        self._device_id = device_id
        self._name = 'SensorPush Humidity'
        self._state = 0.0
        super().__init__(sensorpush_service)

    @property
    def unit_of_measurement(self):
        """Relative Humidity (Rh)"""
        return 'Rh'

    @property
    def state(self):
        """Humidity"""
        return self._state

    def update(self):
        """Update sensor state"""
        self._update_state_from_field('humidity')

# pylint: disable=too-many-instance-attributes
class SensorPushTemperature(SensorPushEntity):
    """Temperature sensor for a SensorPush device"""

    def __init__(self, sensorpush_service, device_id):
        self._device_id = device_id
        self._name = 'SensorPush Temperature'
        self._state = 0.0
        super().__init__(sensorpush_service)

    @property
    def unit_of_measurement(self):
        """Unit of measurement"""
        return '°F'

    @property
    def state(self):
        """Temperature"""
        return self._state

    def update(self):
        """Update sensor state"""
        self._update_state_from_field('temperature')