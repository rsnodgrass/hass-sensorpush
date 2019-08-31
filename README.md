# SensorPush Integration for Home Assistant

***NOT YET IMPLEMENTED***

***LOOKING FOR VOLUNTEERS TO HELP***

Home Assistant sensors for [SensorPush temeperature and humidity sensors](https://www.amazon.com/SensorPush-Wireless-Thermometer-Hygrometer-Android/dp/B01AEQ9X9I?tag=rynoshark-20) for Home Assistant. Requires the [SensorPush G1 WiFi Gateway](https://www.amazon.com/SensorPush-G1-WiFi-Gateway-Anywhere/dp/B01N17RWWV?tag=rynoshark-20) for continously collected data from the sensors (though can also synchronize historical data over Bluetooth when nearby using the iOS and Android apps).

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=WREP29UDAMB6G)

### Supported Sensors

- temperature (&deg;F)
- humidity (Rh)
- battery voltage

## Installation

Visit the Home Assistant community if you need [help with installation and configuration of the SensorPush integration](https://community.home-assistant.io/t/sensorpush-humidity-and-temperature-sensors/105711).

### Step 1: Install Custom Components

Easiest installation is by setting up [Home Assistant Community Store (HACS)](https://github.com/custom-components/hacs), and then adding the "Integration" repository: rsnodgrass/hass-sensorpush.

However you can also manually copy all the files in [custom_components/sensorpush/](https://github.com/rsnodgrass/hass-sensorpush/custom_components/sensorpush) directory to `/config/custom_components/sensorpush` on your Home Assistant installation.

### Step 2: Configure Sensors

Example configuration:

```yaml
sensorpush:
  username: your@email.com
  password: your_password
```

### Step 3: Add Lovelace Card

## See Also

* [Community support for Home Assistant SensorPush integration](https://community.home-assistant.io/t/sensorpush-humidity-and-temperature-sensors/105711)

* [SensorPush Wireless Thermometer/Hygrometer - Humidity & Temperature Smart Sensor](https://www.amazon.com/SensorPush-Wireless-Thermometer-Hygrometer-Android/dp/B01AEQ9X9I?tag=rynoshark-20)
* [SensorPush G1 WiFi Gateway](https://www.amazon.com/SensorPush-G1-WiFi-Gateway-Anywhere/dp/B01N17RWWV?tag=rynoshark-20)
* [SensorPush](https://sensorpush.com) (official product page)

* [Pysensorpush](https://github.com/rsnodgrass/pysensorpush) - Python API

## Feature Requests

Priority improvements:

- autocreate sensors

