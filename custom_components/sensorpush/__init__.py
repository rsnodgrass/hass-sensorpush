"""
SensorPush for Home Assistant
See https://github.com/rsnodgrass/hass-sensorpush
"""
import logging

import time
import pysensorpush

from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.const import ( CONF_USERNAME, CONF_PASSWORD, CONF_NAME, CONF_SCAN_INTERVAL )
#from homeassistant.components.sensor import ( PLATFORM_SCHEMA )

_LOGGER = logging.getLogger(__name__)

SENSORPUSH_DOMAIN = 'sensorpush'

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

#CONFIG_SCHEMA = vol.Schema({
#    SENSORPUSH_DOMAIN: vol.Schema({
#        vol.Required(CONF_USERNAME): cv.string,
#        vol.Required(CONF_PASSWORD): cv.string
#        vol.Optional(CONF_SCAN_INTERVAL, default=600): cv.positive_int
#    })
#}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """Set up the SensorPush integration"""
    conf = config[SENSORPUSH_DOMAIN]

    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    
    service = PySensorPush(username, password)
    updater = SensorPushUpdater(config, service)

    # create sensors for all registered devices
    devices = sensorpush.devices()

    self._units = UNIT_SYSTEMS['imperial'] # config[CONF_UNIT_SYSTEM]

#    for component in ['sensor', 'switch']:
#        discovery.load_platform(hass, component, SENSORPUSH_DOMAIN, conf, config)

    return True

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
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs

class SensorPushUpdater:
    """Cached interface to SensorPush service samples"""

    def __init__(self, config, service):
        self._sensorpush_service = service

        # prevent DDoS of SensorPush service, cache results for N seconds
        self._cache_ttl_seconds = 45 # config[CONF_CACHE_TTL]; must be > MIN_CACHE_TTL = 5
        self._last_updated = 0

    def get_samples(self):
        current_time = time.time()

        # cache the results (throttle to avoid DoS API)
        if self._last_updated < current_time - self._cache_ttl_seconds:
            self._last_sample = self._sensorpush_service.samples
            self._last_updated = time.time()

        return self._last_sample