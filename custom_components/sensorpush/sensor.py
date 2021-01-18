"""
SensorPush Home Assistant sensors

FUTURE:
- support Celsius and Fahrenheit (based on SensorPush's cloud responses)
"""
import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA

from . import ( SensorPushEntity, SENSORPUSH_SERVICE, SENSORPUSH_SAMPLES)

from .const import (CONF_UNIT_SYSTEM, UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC, UNIT_SYSTEMS,
                    CONF_MAXIMUM_AGE, SENSORPUSH_DOMAIN,
                    UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC, UNIT_SYSTEMS,
                    MEASURE_TEMP, MEASURE_HUMIDITY, MEASURE_DEWPOINT, MEASURE_BAROMETRIC_PRESSURE,
                    MEASURE_VPD, MEASURES)

LOG = logging.getLogger(__name__)

DEPENDENCIES = ['sensorpush']

# pylint: disable=unused-argument
def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Create all the SensorPush sensors"""

    sensorpush_service = hass.data.get(SENSORPUSH_SERVICE)
    if not sensorpush_service:
        LOG.info("NOT setting up SensorPush -- SENSORPUSH_SERVICE has not been initialized")
        return

    conf = config.get(SENSORPUSH_DOMAIN)
    LOG.info(f"Config = {config}")

    unit_system = UNIT_SYSTEM_IMPERIAL
    if config.get(CONF_UNIT_SYSTEM) == UNIT_SYSTEM_METRIC:
        unit_system = UNIT_SYSTEM_METRIC
    LOG.info(f"Using unit system '{unit_system}'")

    hass_sensors = []
    for sensor_info in sensorpush_service.sensors.values():
        LOG.info(f"SensorInfo: {sensor_info} -- {type(sensor_info)}")
        supported_measurements = sensor_info["calibration"].keys()

        if sensor_info.get('active') == 'False': # FIXME
            LOG.warn(f"Ignoring inactive SensorPush sensor '{sensor_info.get('name')}")
            continue

        LOG.info(f"Instantiating SensorPush sensors: {sensor_info}")
        for measure in MEASURES:
            # only include measurements supported by this sensor
            if measure in supported_measurements:
                sensor = SensorPushMeasurement(hass, conf, sensor_info, unit_system, measure)
                hass_sensors.append(sensor)

    # execute callback to add new entities
    add_entities_callback(hass_sensors, True)

# pylint: disable=too-many-instance-attributes
class SensorPushMeasurement(SensorPushEntity):
    """Measurement sensor for a SensorPush device"""
    def __init__(self, hass, config, sensor_info, unit_system, measure):
        self._measure = measure
        self._unit_system = unit_system
        self._name = MEASURES[self._measure]['name']
        self._sensor_info = sensor_info
        self._state = None

        super().__init__(hass, config, self._name, sensor_info, unit_system, measure)

    @property
    def icon(self):
        return MEASURES[self._measure]['icon']

    @property
    def unit_of_measurement(self):
        return UNIT_SYSTEMS[self._unit_system][self._measure]

    @property
    def unique_id(self):
        return f"sensorpush_{self._measure}_{self._device_id}"
