"""
SensorPush Home Assistant sensors

FUTURE:
- support Celsius and Fahrenheit (based on SensorPush's cloud responses)
"""

import logging

from homeassistant.components.sensor import SensorEntity

from . import SensorPushEntity, SENSORPUSH_SERVICE

from .const import MEASURES, MEASURE_BAROMETRIC_PRESSURE

LOG = logging.getLogger(__name__)

DEPENDENCIES = ['sensorpush']


# pylint: disable=unused-argument
def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Create all the SensorPush sensors"""

    sensorpush_service = hass.data.get(SENSORPUSH_SERVICE)
    if not sensorpush_service:
        LOG.error(
            'NOT setting up SensorPush -- SENSORPUSH_SERVICE has not been initialized'
        )
        return

    hass_sensors = []
    for sensor_info in sensorpush_service.sensors.values():
        LOG.info(f'SensorInfo: {sensor_info} -- {type(sensor_info)}')
        # supported_measurements = sensor_info["calibration"].keys()

        if sensor_info.get('active') == 'False':  # FIXME
            LOG.warn(f"Ignoring inactive SensorPush sensor '{sensor_info.get('name')}")
            continue

        LOG.info(f'Instantiating SensorPush sensors: {sensor_info}')
        for measure in MEASURES:
            # only include measurements supported by this sensor
            if (
                sensor_info.get('type') == 'HTP.xw'
                or measure != MEASURE_BAROMETRIC_PRESSURE
            ):
                sensor = SensorPushMeasurement(hass, config, sensor_info, measure)
                hass_sensors.append(sensor)

    # execute callback to add new entities
    add_entities_callback(hass_sensors, True)


# pylint: disable=too-many-instance-attributes
class SensorPushMeasurement(SensorPushEntity, SensorEntity):
    """Measurement sensor for a SensorPush device"""

    def __init__(self, hass, config, sensor_info, measure):
        self._name = MEASURES[measure]['name']
        self._state = None
        super().__init__(hass, config, self._name, sensor_info, measure)

    @property
    def unique_id(self):
        return f'sensorpush_{self._field_name}_{self._device_id}'
