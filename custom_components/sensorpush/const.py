SENSORPUSH_DOMAIN = 'sensorpush'

ATTR_BATTERY_VOLTAGE = 'battery_voltage'
ATTR_DEVICE_ID       = 'device_id'
ATTR_OBSERVED_TIME   = 'observed_time'

CONF_UNIT_SYSTEM = 'unit_system'
CONF_MAXIMUM_AGE = 'maximum_age' # maximum age (in minutes) of observations before they expire

UNIT_SYSTEM_IMPERIAL = 'imperial'
UNIT_SYSTEM_METRIC = 'metric'

UNIT_SYSTEMS = {
    UNIT_SYSTEM_IMPERIAL: { 
        'system':      'imperial',
        'temperature': '°F',
        'humidity':    '%' # 'Rh'
    },
    UNIT_SYSTEM_METRIC: { 
        'system':      'metric',
        'temperature': '°C',
        'humidity':    '%' # 'Rh'
    }
}