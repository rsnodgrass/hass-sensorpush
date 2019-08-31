"""
SensorPush for Home Assistant
See https://github.com/rsnodgrass/hass-sensorpush

- battery_voltage
- deviceId
- id
- address?
- active?
"""
import logging

import time
from datetime import timedelta
import pysensorpush
import voluptuous as vol
from requests.exceptions import HTTPError, ConnectTimeout

from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL
#from homeassistant.components.sensor import ( PLATFORM_SCHEMA )

LOG = logging.getLogger(__name__)

SENSORPUSH_DOMAIN = 'sensorpush'

NOTIFICATION_ID = "sensorpush_notification"
NOTIFICATION_TITLE = "SensorPush"

ATTR_ACTIVE          = 'active'
ATTR_BATTERY_VOLTAGE = 'battery_voltage'
ATTR_MAC_ADDRESS     = 'mac_address'
ATTR_DEVICE_ID       = 'device_id'
ATTR_OBSERVED        = 'observed'

SCAN_INTERVAL = timedelta(seconds = 60)

UNIT_SYSTEMS = {
    'imperial': { 
        'system':   'imperial',
        'temp':     '°F',
        'humidity': 'Rh'
    },
    'metric': { 
        'system':   'metric',
        'temp':     '°C',
        'humidity': 'Rh'
    }
}

CONFIG_SCHEMA = vol.Schema({
        SENSORPUSH_DOMAIN: vol.Schema({
            vol.Required(CONF_USERNAME): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.positive_int
        })
    }, extra=vol.ALLOW_EXTRA
)

def setup(hass, config):
    """Set up the SensorPush integration"""
    conf = config[SENSORPUSH_DOMAIN]

    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    scan_interval = conf.get(CONF_SCAN_INTERVAL)

    try:
        sensorpush_service = PySensorPush(username, password)
        #if not sensorpush_service.is_connected:
        #    return False

        # FIXME: log warning if no sensors found?

        updater = SensorPushUpdater(config, sensorpush_service)

        # create sensors for all devices registered with SensorPush
        registered_devices = sensorpush_service.devices
#        for device in registered_devices.values():
#            SensorPushTemperature

#        discovery.load_platform(hass, component, SENSORPUSH_DOMAIN, conf, device, updater)

    #{ 'active': True,
    #                             'address': 'EF:E1:D0:40:F8:37',
    #                             'alerts': { 'humidity': { 'enabled': True,
    #                                                       'max': 58,
    #                                                       'min': 32},
    #                                         'temperature': { 'enabled': True,
    #                                                          'max': 85.00000038146973,
    #                                                          'min': 49.00000038146973}},
    #                             'battery_voltage': 2.93,
    #                             'calibration': { 'humidity': 0,
    #                                              'temperature': 0},
    #                             'deviceId': '36600',
    #                             'id': '36600.3025014081951077535',
    #                             'name': 'Warehouse 3095 - Exterior Unit'}

        # units = UNIT_SYSTEMS['imperial'] # config[CONF_UNIT_SYSTEM]
        return True

    except (ConnectTimeout, HTTPError) as ex:
        LOG.error("Unable to connect to SensorPush: %s", str(ex))
        hass.components.persistent_notification.create(
            f"Error: {ex}<br />You will need to restart Home Assistant after fixing.",
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID,
        )
        return False

class SensorPushEntity(Entity):
    """Base Entity class for SensorPush devices"""

    def __init__(self, sensorpush_updater):
        self._service_updater = sensorpush_updater
        self._attrs = {}

        if self._name is None:
            self._name = 'SensorPush' # default if unspecified

    @property
    def name(self):
        """Return the display name for this sensor"""
        return self._name

    @property
    def icon(self):
        return 'mdi:gauge'

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs

    def _update_state_from_field(self, field):
        if field not in ['humidity', 'temperature']:
            LOG.error(f"Update field {field} not supported")
            return

        # json_response = self._sensorpush_service.update(self._device_id)
        #temperature or humidity

        self._state = float(json_response['temperature'])
        self._attrs.update({
            ATTR_BATTERY_VOLTAGE : json_response['battery_voltage'],
            ATTR_OBSERVED        : json_response['observed']
        })
        LOG.info("Updated %s to %f %s : %s", self._name, self._state, self.unit_of_measurement, json_response)

class SensorPushUpdater:
    """Cached interface to SensorPush service samples"""

    def __init__(self, config, service):
        self._sensorpush_service = service

        # prevent DDoS of SensorPush service, cache results for N seconds
        self._cache_ttl_seconds = 45 # config[CONF_CACHE_TTL]; must be > MIN_CACHE_TTL = 5
        self._last_updated = 0

    @property
    def samples(self):
        current_time = time.time()

        # cache the results (throttle to avoid DoS API)
        if self._last_updated < current_time - self._cache_ttl_seconds:
            self._last_sample = self._sensorpush_service.samples
            self._last_updated = time.time()

        return self._last_sample