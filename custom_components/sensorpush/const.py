from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT

SENSORPUSH_DOMAIN = 'sensorpush'

ATTR_AGE             = 'age'
ATTR_BATTERY_VOLTAGE = 'battery_voltage'
ATTR_DEVICE_ID       = 'device_id'
ATTR_OBSERVED_TIME   = 'observed_time'
ATTR_LIMIT_MIN       = 'limit_min'
ATTR_LIMIT_MAX       = 'limit_max'

CONF_UNIT_SYSTEM = 'unit_system'
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

UNIT_SYSTEM_IMPERIAL = 'imperial'
UNIT_SYSTEM_METRIC = 'metric'

UNIT_SYSTEMS = {
    UNIT_SYSTEM_IMPERIAL: { 
        'system': 'imperial',
        MEASURE_BAROMETRIC_PRESSURE: 'inHg',
        MEASURE_DEWPOINT: TEMP_FAHRENHEIT,
        MEASURE_HUMIDITY: '%', # 'Rh'
        MEASURE_TEMP: TEMP_FAHRENHEIT,
        MEASURE_VPD: 'kPa'
    },

    UNIT_SYSTEM_METRIC: { 
        'system': 'metric',
        MEASURE_BAROMETRIC_PRESSURE: 'mbar',
        MEASURE_DEWPOINT: TEMP_CELSIUS, # FIXME: icon mdi:temperature-celsius
        MEASURE_HUMIDITY: '%', # 'Rh'
        MEASURE_TEMP: TEMP_CELSIUS,
        MEASURE_VPD: 'kPa'
    }
}