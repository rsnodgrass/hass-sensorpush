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

from .const import (SENSORPUSH_DOMAIN, CONF_UNIT_SYSTEM, MEASURES,
                    UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC, UNIT_SYSTEMS)

LOG = logging.getLogger(__name__)

DEPENDENCIES = ['sensorpush']

# pylint: disable=unused-argument
def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Create all the SensorPush sensors"""

    sensorpush_service = hass.data.get(SENSORPUSH_SERVICE)
    if not sensorpush_service:
        LOG.info("NOT setting up SensorPush -- SENSORPUSH_SERVICE has not been initialized")
        return

    unit_system = hass.data[SENSORPUSH_DOMAIN][CONF_UNIT_SYSTEM]

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
                sensor = SensorPushMeasurement(hass, config, sensor_info, unit_system, measure)
                hass_sensors.append(sensor)

    # execute callback to add new entities
    add_entities_callback(hass_sensors, True)

# pylint: disable=too-many-instance-attributes
class SensorPushMeasurement(SensorPushEntity):
    """Measurement sensor for a SensorPush device"""
    def __init__(self, hass, config, sensor_info, unit_system, measure):
        self._name = MEASURES[measure]['name']
        self._state = None
        super().__init__(hass, config, self._name, sensor_info, unit_system, measure)

    @property
    def unit_of_measurement(self):
        return UNIT_SYSTEMS[self._unit_system][self._field_name]

    @property
    def unique_id(self):
        return f"sensorpush_{self._field_name}_{self._device_id}"
