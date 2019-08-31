"""
Support for SensorPUsh sensors

FUTURE:
- convert to async
- support celsius and fahrenheit (based on HA default config?)
- battery_voltage
- deviceId
- id
- address?
- active?
"""
import logging

from homeassistant.const import ( TEMP_FAHRENHEIT, ATTR_TEMPERATURE )
from . import SensorPushService, SensorPushEntity

_LOGGER = logging.getLogger(__name__)

ATTR_TIME            = 'time'
ATTR_ACTIVE          = 'active'
ATTR_BATTERY_VOLTAGE = 'battery_voltage'
ATTR_MAC_ADDRESS     = 'mac_address'
ATTR_DEVICE_ID       = 'device_id'

#SCAN_INTERVAL = timedelta(seconds=0.1)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_sensors_callback, discovery_info=None):
    """Setup the SensorPush sensor"""
    service = SensorPushService(config)

    # get a list of all SensorPush devices
    response = service.get_request('/icds/me')
    # Example response:
    #   { "is_paired": true,
    #     "device_id": "a0b405bfe487",
    #     "id": "2faf8cd6-a8eb-4b63-bd1a-33298a26eca8",
    #     "location_id": "e7b2833a-f2cb-a4b1-ace2-36c21075d493" }
    json_response = response.json()
    device_id = json_response['id']

    # FUTURE: support multiple sensors
    sensors = []
    sensors.append(SPTemperatureSensor(service, device_id))
    sensors.append(SPHumiditySensor(service, device_id))

    for sensor in sensors:
        sensor.update()

    # execute callback to add new entities
    add_sensors_callback(sensors)


# pylint: disable=too-many-instance-attributes
class SPHumiditySensor(SensorPushEntity):
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

    @property
    def icon(self):
        return 'mdi:water-pump'

    def update(self):
        """Update sensor state"""
#        json_response = self._sensorpush_service.update(self._device_id)

        self._state = float(json_response['humidity'])
        self._attrs.update({
            ATTR_TIME            : json_response['time'],
            ATTR_BATTERY_VOLTAGE : json_response['battery_voltage']
        })
        _LOGGER.info("Updated %s to %f %s : %s", self._name, self._state, self.unit_of_measurement, json_response)

# pylint: disable=too-many-instance-attributes
class SPTemperatureSensor(SensorPushEntity):
    """Temperature sensor for a SensorPush device"""

    def __init__(self, sensorpush_service, device_id):
        self._device_id = device_id
        self._name = 'SensorPush Temperature'
        self._state = 0.0
        super().__init__(sensorpush_service)

    @property
    def unit_of_measurement(self):
        """Fahrenheit"""
        return 'F'

    @property
    def state(self):
        """Temperature"""
        return self._state

    @property
    def icon(self):
        return 'mdi:gauge'

    def update(self):
        """Update sensor state"""
        # json_response = self._sensorpush_service.update(self._device_id)

        self._state = float(json_response['temperature'])
        self._attrs.update({
            ATTR_TIME            : json_response['time']
            ATTR_BATTERY_VOLTAGE : json_response['battery_voltage']
        })
        _LOGGER.info("Updated %s to %f %s : %s", self._name, self._state, self.unit_of_measurement, json_response)
