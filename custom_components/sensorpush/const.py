SENSORPUSH_DOMAIN = 'sensorpush'

ATTRIBUTION="Data by SensorPush"
ATTR_ATTRIBUTION="attribution"

ATTR_AGE             = 'age'
ATTR_BATTERY_VOLTAGE = 'battery_voltage'
ATTR_DEVICE_ID       = 'device_id'
ATTR_OBSERVED_TIME   = 'observed_time'
ATTR_ALERT_MIN       = 'alert_min'
ATTR_ALERT_MAX       = 'alert_max'
ATTR_ALERT_ENABLED   = 'alert_enabled'

CONF_MAXIMUM_AGE = 'maximum_age' # maximum age (in minutes) of observations before they expire

MEASURE_TEMP = "temperature"
MEASURE_HUMIDITY = "humidity"
MEASURE_DEWPOINT = "dewpoint"
MEASURE_BAROMETRIC_PRESSURE = "barometric_pressure"
MEASURE_VPD = "vpd"

ICON = 'icon'
NAME = 'name'

# FIXME: read this from a *localized* JSON configuration map!
MEASURES = {
    MEASURE_TEMP: {
        NAME: "Temperature",
        ICON: "mdi:thermometer"
    },
    MEASURE_HUMIDITY: { # Relative Humidity (Rh %)
        NAME: "Humidity",
        ICON: 'mdi:water-percent'
    },
    MEASURE_DEWPOINT: {
        NAME: "Dewpoint",
        ICON: "mdi:thermometer"
    },
    MEASURE_BAROMETRIC_PRESSURE: {
        NAME: "Barometric Pressure",
        ICON: "mdi:nature"
    },
    MEASURE_VPD: {
        NAME: "Vapor Pressure Deficit",
        ICON: "mdi:thermometer"
    }
}

UNIT_SYSTEMS = {
    'system': 'imperial',
    MEASURE_BAROMETRIC_PRESSURE: 'inHg',
    MEASURE_DEWPOINT: '°F',
    MEASURE_HUMIDITY: '%', # 'Rh'
    MEASURE_TEMP: '°F',
    MEASURE_VPD: 'kPa'
}
