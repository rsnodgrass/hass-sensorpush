"""
SensorPush Home Assistant sensors

FUTURE:
- support Celsius and Fahrenheit (based on SensorPush's cloud responses)
"""
import logging

from . import ( SensorPushEntity, SENSORPUSH_SERVICE, SENSORPUSH_SAMPLES,
                SENSORPUSH_DOMAIN, CONF_MAXIMUM_AGE,
                CONF_UNIT_SYSTEM, UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC, UNIT_SYSTEMS )

LOG = logging.getLogger(__name__)

# pylint: disable=unused-argument
async def async_setup_platform(hass, config, async_add_entities_callback, discovery_info=None):
#def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Setup the SensorPush sensor"""

    sensorpush_service = hass.data.get(SENSORPUSH_SERVICE)
    if not sensorpush_service:
        log.INFO("NOT setting up SensorPush -- missing SENSORPUSH_SERVICE")
        return

    conf = config[SENSORPUSH_DOMAIN]

    unit_system = UNIT_SYSTEM_IMPERIAL
    if conf.get(CONF_UNIT_SYSTEM) == UNIT_SYSTEM_METRIC:
        unit_system = UNIT_SYSTEM_METRIC

    LOG.info(f"Setting up SensorPush sensors based on sensor_info: {sensorpush_service.sensors}")

    hass_sensors = []
    for sensor_info in sensorpush_service.sensors:

        if sensor_info['active'] == 'False': # FIXME
            LOG.warn(f"Ignoring inactive SensorPush sensor '{sensor_info['name']}'")
            continue

        LOG.info(f"Setting up SensorPush sensors: {sensor_info}")
        hass_sensors.append(SensorPushTemperature(hass, conf, sensor_info, unit_system))
        hass_sensors.append(SensorPushHumidity(hass, conf, sensor_info, unit_system))

    # execute callback to add new entities
    async_add_entities_callback(hass_sensors, True)

# pylint: disable=too-many-instance-attributes
class SensorPushHumidity(SensorPushEntity):
    """Humidity sensor for a SensorPush device"""

    def __init__(self, hass, config, sensor_info, unit_system):
        self._name = f"{sensor_info['name']} Humidity"
        self._unit_system = unit_system
        self._state = 0.0
        super().__init__(hass, config, sensor_info, 'humidity')

    @property
    def unit_of_measurement(self):
        """Relative Humidity (Rh)"""
        return 'Rh'

# pylint: disable=too-many-instance-attributes
class SensorPushTemperature(SensorPushEntity):
    """Temperature sensor for a SensorPush device"""

    def __init__(self, hass, config, sensor_info, unit_system):
        self._name = f"{sensor_info['name']} Temperature"
        self._unit_system = unit_system
        self._state = 0.0
        super().__init__(hass, config, sensor_info, 'temperature')

    @property
    def unit_of_measurement(self):
        """Temperature (Fahrenheit or Celsius)"""
        return UNIT_SYSTEMS[self._unit_system]['temp']