"""
SensorPush Home Assistant sensors

FUTURE:
- support celsius and fahrenheit (based on cloud setup)
"""
import logging

from . import SensorPushService, SensorPushEntity, SENSORPUSH_SERVICE, SENSORPUSH_SAMPLES

LOG = logging.getLogger(__name__)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Setup the SensorPush sensor"""
    hass_sensors = []
    for sensor_info in hass.data[SENSORPUSH_SERVICE].sensors:

        if sensor_info['active'] == 'False': # FIXME
            LOG.warn(f"Ignoring inactive SensorPush sensor '{sensor_info['name']}'")
            continue

        hass_sensors.append(SensorPushTemperature(sensor_info))
        hass_sensors.append(SensorPushHumidity(sensor_info))

    # execute callback to add new entities
    add_entities_callback(hass_sensors)

# pylint: disable=too-many-instance-attributes
class SensorPushHumidity(SensorPushEntity):
    """Humidity sensor for a SensorPush device"""

    def __init__(self, sensor_info):
        self._name = f"{sensor_info['name']} Humidity"
        self._state = 0.0
        super().__init__(sensor_info, 'humidity')

    @property
    def unit_of_measurement(self):
        """Relative Humidity (Rh)"""
        return 'Rh'

# pylint: disable=too-many-instance-attributes
class SensorPushTemperature(SensorPushEntity):
    """Temperature sensor for a SensorPush device"""

    def __init__(self, sensor_info):
        self._name = f"{sensor_info['name']} Temperature"
        self._state = 0.0
        super().__init__(sensor_info, 'temperature')

    @property
    def unit_of_measurement(self):
        """Unit of measurement"""
        return '°F'
