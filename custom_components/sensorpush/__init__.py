"""
SensorPush for Home Assistant

See also:

* https://github.com/rsnodgrass/hass-sensorpush
* http://www.sensorpush.com/api/docs
* https://community.home-assistant.io/t/sensorpush-humidity-and-temperature-sensors/105711

"""
import logging
import json
import requests
import time
from threading import Thread, Lock

from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.const import ( CONF_USERNAME, CONF_PASSWORD, CONF_NAME, CONF_SCAN_INTERVAL )
#from homeassistant.components.sensor import ( PLATFORM_SCHEMA )

_LOGGER = logging.getLogger(__name__)

SENSORPUSH_DOMAIN = 'sensorpush'
SENSORPUSH_USER_AGENT = 'Home Assistant (https://homeassistant.io/; https://github.com/rsnodgrass/hass-sensorpush)'

# cache expiry in minutes; TODO: make this configurable (with a minimum to prevent DDoS)
SENSORPUSH_CACHE_EXPIRY=10

SENSORPUSH_API = 'https://api.sensorpush.com/api/v1'

UNIT_SYSTEMS = {
    'imperial_us': { 
        'system':   'imperial_us',
        'temp':     '°F',
        'humidity': 'Rh'
    },
    'imperial_uk': { 
        'system':   'imperial_uk',
        'temp':     '°F',
        'humidity': 'Rh'
    },
    'metric': { 
        'system':   'metric',
        'temp':     '°C',
        'humidity': 'Rh'
    }
}

mutex = Lock()

#CONFIG_SCHEMA = vol.Schema({
#    SENSORPUSH_DOMAIN: vol.Schema({
#        vol.Required(CONF_USERNAME): cv.string,
#        vol.Required(CONF_PASSWORD): cv.string
#        vol.Optional(CONF_SCAN_INTERVAL, default=600): cv.positive_int
#    })
#}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """Set up the SensorPush integration"""
#    conf = config[SENSORPUSH_DOMAIN]
#    conf = {}
#    for component in ['sensor', 'switch']:
#        discovery.load_platform(hass, component, SENSORPUSH_DOMAIN, conf, config)
    return True

class SensorPushEntity(Entity):
    """Base Entity class for SensorPush devices"""

    def __init__(self, sensorpush_service):
        """Store service upon init."""
        self._service = sensorpush_service
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

class SensorPushService:
    """Client interface to the SensorPush service API"""

    def __init__(self, config):
        self._auth_token = None
        self._auth_token_expiry = 0
        
        self._username = config[CONF_USERNAME]
        self._password = config[CONF_PASSWORD]

#        self._units = UNIT_SYSTEMS[self._get_unit_system]

    def _authentication_token(self):
        now = int(time.time())
        if not self._auth_token or now > self._auth_token_expiry:
            # authenticate to the Flo API
            #   POST https://api.meetflo.com/api/v1/users/auth
            #   Payload: {username: "your@email.com", password: "1234"}

            auth_url = SENSORPUSH_API + '/oath/authorize'
            payload = json.dumps({
                'username': self._username,
                'password': self._password
            })
            headers = { 
                'User-Agent': SENSORPUSH_USER_AGENT,
                'Content-Type': 'application/json;charset=UTF-8'
            }

            _LOGGER.debug("Authenticating SensorPush account %s via %s", self._username, auth_url)
            response = requests.post(auth_url, data=payload, headers=headers)
            # Example response:
            # { "token": "caJhb.....",
            #   "tokenPayload": { "user": { "user_id": "9aab2ced-c495-4884-ac52-b63f3008b6c7", "email": "your@email.com"},
            #                     "timestamp": 1559246133 },
            #   "tokenExpiration": 86400,
            #   "timeNow": 1559226161 }

            json_response = response.json()

            _LOGGER.debug("SensorPush user %s authentication results %s : %s", self._username, auth_url, json_response)
            self._auth_token_expiry = now + int( int(json_response['tokenExpiration']) / 2)
            self._auth_token = json_response['token']

        return self._auth_token

    def get_request(self, url_path):
        url = SENSORPUSH_API + url_path
        headers = { 
            'authorization': self._authentication_token(), 
            'User-Agent': SENSORPUSH_USER_AGENT
        }
        response = requests.get(url, headers=headers)
        _LOGGER.debug("SensorPush GET %s : %s", url, response.content)
        return response
