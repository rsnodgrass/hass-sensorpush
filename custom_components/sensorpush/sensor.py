"""
SensorPush Home Assistant sensors

FUTURE:
- support Celsius and Fahrenheit (based on SensorPush's cloud responses)
"""
import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA

from . import ( SensorPushEntity, SENSORPUSH_SERVICE, SENSORPUSH_SAMPLES,
                SENSORPUSH_DOMAIN, CONF_MAXIMUM_AGE,
                CONF_UNIT_SYSTEM, UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC, UNIT_SYSTEMS )

LOG = logging.getLogger(__name__)

DEPENDENCIES = ['sensorpush']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_UNIT_SYSTEM, default=UNIT_SYSTEM_IMPERIAL): cv.string
    }
)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_entities_callback, discovery_info=None):
#def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Setup the SensorPush sensor"""

    sensorpush_service = hass.data.get(SENSORPUSH_SERVICE)
    if not sensorpush_service:
        LOG.info("NOT setting up SensorPush -- missing SENSORPUSH_SERVICE")
        return

#    conf = hass.config[SENSORPUSH_DOMAIN]
    conf = None

    unit_system = UNIT_SYSTEM_IMPERIAL
#    if conf.get(CONF_UNIT_SYSTEM) == UNIT_SYSTEM_METRIC:
#        unit_system = UNIT_SYSTEM_METRIC

    hass_sensors = []
    for sensor_info in sensorpush_service.sensors.values():
        LOG.info(f"SensorInfo: {sensor_info} -- {type(sensor_info)}")

        if sensor_info.get('active') == 'False': # FIXME
            LOG.warn(f"Ignoring inactive SensorPush sensor '{sensor_info.get('name')}")
            continue

        LOG.info(f"Instantiating SensorPush sensors: {sensor_info}")
        hass_sensors.append( SensorPushTemperature(hass, conf, sensor_info, unit_system) )
        hass_sensors.append( SensorPushHumidity(hass, conf, sensor_info, unit_system))

    # execute callback to add new entities
    add_entities_callback(hass_sensors, True)

# pylint: disable=too-many-instance-attributes
class SensorPushHumidity(SensorPushEntity):
    """Humidity sensor for a SensorPush device"""

    def __init__(self, hass, config, sensor_info, unit_system):
        self._state = ''
        super().__init__(hass, config, 'Humidity', sensor_info, unit_system, 'humidity')

    @property
    def icon(self):
        return 'mdi:water-percent'

    @property
    def unit_of_measurement(self):
        """Relative Humidity (Rh %)"""
        return '%'

    @property
    def unique_id(self):
        return f"sensorpush_humidity_{self._device_id}"
    
# pylint: disable=too-many-instance-attributes
class SensorPushTemperature(SensorPushEntity):
    """Temperature sensor for a SensorPush device"""

    def __init__(self, hass, config, sensor_info, unit_system):
        self._state = ''
        super().__init__(hass, config, 'Temperature', sensor_info, unit_system, 'temperature')

    @property
    def unit_of_measurement(self):
        """Temperature (Fahrenheit or Celsius)"""
        return UNIT_SYSTEMS.get(self._unit_system).get('temperature')

    @property
    def unique_id(self):
        return f"sensorpush_temp_{self._device_id}"
