"""
SensorPush for Home Assistant
See https://github.com/rsnodgrass/hass-sensorpush
"""
import logging

import time
from datetime import timedelta
import voluptuous as vol
from requests.exceptions import HTTPError, ConnectTimeout

from pysensorpush import PySensorPush

from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import dispatcher_send, async_dispatcher_connect
from homeassistant.helpers.event import track_time_interval
from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL
#from homeassistant.components.sensor import ( PLATFORM_SCHEMA )

LOG = logging.getLogger(__name__)

SENSORPUSH_DOMAIN = 'sensorpush'

SENSORPUSH_SERVICE = 'sensorpush_service'
SENSORPUSH_SAMPLES = 'sensorpush_samples'
SIGNAL_SENSORPUSH_UPDATED = 'sensorpush_updated'

NOTIFICATION_ID = 'sensorpush_notification'
NOTIFICATION_TITLE = 'SensorPush'

ATTR_BATTERY_VOLTAGE = 'battery_voltage'
ATTR_DEVICE_ID       = 'device_id'
ATTR_OBSERVED_TIME   = 'observed_time'

CONF_UNIT_SYSTEM = 'unit_system'

UNIT_SYSTEM_IMPERIAL = 'imperial'
UNIT_SYSTEM_METRIC = 'metric'

UNIT_SYSTEMS = {
    UNIT_SYSTEM_IMPERIAL: { 
        'system':   'imperial',
        'temp':     '°F',
        'humidity': 'Rh'
    },
    UNIT_SYSTEM_METRIC: { 
        'system':   'metric',
        'temp':     '°C',
        'humidity': 'Rh'
    }
}

CONFIG_SCHEMA = vol.Schema({
        SENSORPUSH_DOMAIN: vol.Schema({
            vol.Required(CONF_USERNAME): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Optional(CONF_SCAN_INTERVAL, default=60): cv.positive_int,
            vol.Optional(CONF_UNIT_SYSTEM, default='imperial'): cv.string
        })
    }, extra=vol.ALLOW_EXTRA
)

def setup(hass, config):
    """Initialize the SensorPush integration"""
    conf = config[SENSORPUSH_DOMAIN]

    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)

    try:
        sensorpush_service = PySensorPush(username, password)
        #if not sensorpush_service.is_connected:
        #    return False
        # FIXME: log warning if no sensors found?

        # units = UNIT_SYSTEMS['imperial'] # config[CONF_UNIT_SYSTEM]

        # share reference to the service with other components/platforms running within HASS
        hass.data[SENSORPUSH_SERVICE] = sensorpush_service
        hass.data[SENSORPUSH_SAMPLES] = sensorpush_service.samples

    except (ConnectTimeout, HTTPError) as ex:
        LOG.error("Unable to connect to SensorPush: %s", str(ex))
        hass.components.persistent_notification.create(
            f"Error: {ex}<br />You will need to restart Home Assistant after fixing.",
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID,
        )
        return False

    def refresh_sensorpush_data(event_time):
        """Call SensorPush service to refresh latest data"""
        LOG.debug("Updating data from SensorPush cloud API")

        # TODO: discovering new devices (and auto-configuring HASS sensors) is not supported
        #hass.data[SENSORPUSH_SERVICE].update(update_devices=True)

        # retrieve the latest samples from the SensorPush cloud service
        hass.data[SENSORPUSH_SAMPLES] = hass.data[SENSORPUSH_SERVICE].samples

        # notify all listeners (sensor entities) that they may have new data
        dispatcher_send(hass, SIGNAL_SENSORPUSH_UPDATED)

    # subscribe for notifications that an update should be triggered
    hass.services.register(SENSORPUSH_DOMAIN, 'update', refresh_sensorpush_data)

    # automatically update SensorPush data (samples) on the scan interval
    scan_interval = timedelta(seconds = conf.get(CONF_SCAN_INTERVAL))
    track_time_interval(hass, refresh_sensorpush_data, scan_interval)

    return True


class SensorPushEntity(Entity):
    """Base Entity class for SensorPush devices"""

    def __init__(self, hass, sensor_info, field_name):
        self._hass = hass
        self._sensor_info = sensor_info
        self._device_id = sensor_info['id']
        self._field_name = field_name
        self._attrs = {}
        
        if not self._name:
            self._name = f"SensorPush {sensor_info['name']}"

    @property
    def name(self):
        """Return the display name for this sensor"""
        return self._name

    @property
    def icon(self):
        return 'mdi:gauge'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs

    async def async_added_to_hass(self):
        """Register callbacks."""
        # register callback when cached SensorPush data has been updated
        async_dispatcher_connect(self.hass, SIGNAL_SENSORPUSH_UPDATED, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        latest_samples = self._hass.data[SENSORPUSH_SAMPLES]
        all_sensors = latest_samples['sensors']
        data = all_sensors[self._device_id]

        self._state = float(data[self._field_name])

        self._attrs.update({
            ATTR_OBSERVED_TIME   : data['observed'],
            ATTR_BATTERY_VOLTAGE : self._sensor_info['battery_voltage'] # FIXME: this is not updated once the 
        })
        LOG.info("Updated %s to %f %s : %s", self._name, self._state, self.unit_of_measurement, data)

        # let Home Assistant know that SensorPush data for this entity has been updated
        self.async_schedule_update_ha_state()