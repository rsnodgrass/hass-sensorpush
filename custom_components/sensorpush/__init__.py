"""
SensorPush for Home Assistant
See https://github.com/rsnodgrass/hass-sensorpush
"""
import logging

import time
import voluptuous as vol
from datetime import datetime, timedelta
import dateutil.parser
from requests.exceptions import HTTPError, ConnectTimeout

from pysensorpush import PySensorPush

from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import dispatcher_send, async_dispatcher_connect
from homeassistant.helpers.event import track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL

from .const import (ATTR_BATTERY_VOLTAGE, ATTR_DEVICE_ID, ATTR_OBSERVED_TIME, ATTR_AGE,
                    ATTR_ATTRIBUTION, ATTRIBUTION, MEASURES, CONF_UNIT_SYSTEM, CONF_MAXIMUM_AGE,
                    ATTR_ALERT_MIN, ATTR_ALERT_MAX, ATTR_ALERT_ENABLED,
                    SENSORPUSH_DOMAIN, UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC, UNIT_SYSTEMS)

LOG = logging.getLogger(__name__)

SENSORPUSH_SERVICE = 'sensorpush_service'
SENSORPUSH_SAMPLES = 'sensorpush_samples'
SIGNAL_SENSORPUSH_UPDATED = 'sensorpush_updated'

NOTIFICATION_ID = 'sensorpush_notification'
NOTIFICATION_TITLE = 'SensorPush'

DATA_UPDATED = "sensorpush_data_updated"

MIN_SCAN_INTERVAL_IN_SECONDS = 30

CONFIG_SCHEMA = vol.Schema({
        SENSORPUSH_DOMAIN: vol.Schema({
            vol.Required(CONF_USERNAME): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Optional(CONF_SCAN_INTERVAL, default=60):
                vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL_IN_SECONDS)),
            vol.Optional(CONF_UNIT_SYSTEM, default=UNIT_SYSTEM_IMPERIAL):
                vol.In( UNIT_SYSTEMS.keys() ),
            vol.Optional(CONF_MAXIMUM_AGE, default=60): cv.positive_int
        })
    }, extra=vol.ALLOW_EXTRA
)

def setup(hass, config):
    """Initialize the SensorPush integration"""
    hass.data[SENSORPUSH_DOMAIN] = {}
    conf = config[SENSORPUSH_DOMAIN]

    unit_system = conf.get(CONF_UNIT_SYSTEM)
    hass.data[SENSORPUSH_DOMAIN][CONF_UNIT_SYSTEM] = unit_system
    LOG.info(f"Using unit system '{unit_system}'")
    
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)

    try:
        sensorpush_service = PySensorPush(username, password)
        hass.data[SENSORPUSH_SERVICE] = sensorpush_service

        #if not sensorpush_service.is_connected:
        #    return False
        # FIXME: log warning if no sensors found?

        hass.data[SENSORPUSH_SAMPLES] = sensorpush_service.samples()

        # FIXME: trigger automatic setup of sensors

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

        # TODO: discovering new devices (and auto-configuring HASS sensors) is not supported
        #hass.data[SENSORPUSH_SERVICE].update(update_devices=True)

        # retrieve the latest samples from the SensorPush cloud service
        latest_samples = hass.data[SENSORPUSH_SERVICE].samples()
        if latest_samples:
            hass.data[SENSORPUSH_SAMPLES] = latest_samples

            # notify all listeners (sensor entities) that they may have new data
            dispatcher_send(hass, SIGNAL_SENSORPUSH_UPDATED)
        else:
            LOG.warn("Unable to fetch latest samples from SensorPush cloud")

    # subscribe for notifications that an update should be triggered
    hass.services.register(SENSORPUSH_DOMAIN, 'update', refresh_sensorpush_data)

    # automatically update SensorPush data (samples) on the scan interval
    scan_interval = timedelta(seconds = conf.get(CONF_SCAN_INTERVAL))
    track_time_interval(hass, refresh_sensorpush_data, scan_interval)

    return True

class SensorPushEntity(RestoreEntity):
    """Base Entity class for SensorPush devices"""

    def __init__(self, hass, config, name_suffix, sensor_info, unit_system, measure):
        self.hass = hass

        self._field_name = measure
        self._unit_system = unit_system
        self._sensor_info = sensor_info
        self._max_age = 7 * 1440
        self._device_id = sensor_info.get('id')

        self._attrs = {}
        self._name = f"{sensor_info.get('name')} {name_suffix}"

    @property
    def name(self):
        """Return the display name for this sensor"""
        return self._name

    @property
    def icon(self):
        return MEASURES[self._field_name].get('icon') or 'mdi:gauge'

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs

    @callback
    def _update_callback(self):
        samples = self.hass.data[SENSORPUSH_SAMPLES]
        sensor_results = samples.get('sensors')

        sensor_data = sensor_results[self._device_id]
        latest_result = sensor_data[0]
        observed_time = latest_result['observed']

        # FIXME: check data['observed'] time against config[CONF_MAXIMUM_AGE], ignoring stale entries
#        observed = dateutil.parser.isoparse(observed_time)
#        delta = datetime.now(datetime.timezone.utc) - datetime.fromtimestamp(observed, datetime.timezone.utc)
#        age_in_minutes = delta.total_seconds() / 60
#        if age_in_minutes > self._max_age:
#            LOG.warning(f"Stale data {self._device_id} detected ({age_in_minutes} min > {self._max_age} min)")

        # FIXME: Note that _sensor_info does not refresh except on restarts.  Need to
        # add support for this to enable alert changes and voltage to be reflected.

        self._state = float(latest_result.get(self._field_name))
        self._attrs.update({
#            ATTR_AGE             : age_in_minutes,
            ATTR_OBSERVED_TIME   : observed_time,
            ATTR_BATTERY_VOLTAGE : self._sensor_info.get(ATTR_BATTERY_VOLTAGE),
            ATTR_ATTRIBUTION     : ATTRIBUTION
        })

        alerts = self._sensor_info.get("alerts").get(self._field_name)
        if alerts.get("min"):
            alert_min = alerts.get("min")
            alert_max = alerts.get("max")

            # NOTE: The SensorPush API currently does not return units for the min/max
            # alert settings and always returns data in Fahrenheit. If user has
            # specified metric unit system convert to Celsius.
            if UNIT_SYSTEM_METRIC == self.hass.data[SENSORPUSH_DOMAIN][CONF_UNIT_SYSTEM]:
                alert_min = (alert_min - 32) / 1.8
                alert_max = (alert_max - 32) / 1.8

            self._attrs.update({
                ATTR_ALERT_MIN: alert_min,
                ATTR_ALERT_MAX: alert_max,
                ATTR_ALERT_ENABLED: alerts.get("enabled")
            })

#        LOG.info(f"{self._state} ... {self._attrs} ... {sensor_data} ... {self._sensor_info}")

        # let Home Assistant know that SensorPush data for this entity has been updated
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        # register callback when cached SensorPush data has been updated
        async_dispatcher_connect(self.hass, SIGNAL_SENSORPUSH_UPDATED, self._update_callback)

        async_dispatcher_connect(
            self.hass, DATA_UPDATED, self._schedule_immediate_update
        )

    @callback
    def _schedule_immediate_update(self):
        self.async_schedule_update_ha_state(True)
