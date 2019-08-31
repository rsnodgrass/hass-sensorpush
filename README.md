# SensorPush Integration for Home Assistant

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=WREP29UDAMB6G)

Home Assistant integration for [SensorPush temperature and humidity/hygrometer sensors](https://www.amazon.com/SensorPush-Wireless-Thermometer-Hygrometer-Android/dp/B01AEQ9X9I?tag=rynoshark-20).

### Supported Sensors

- temperature (&deg;F)
- humidity (Rh)
- battery voltage

NOTE:

* If you register a new physical sensor with SensorPush, you must restart Home Assistant to discover the new device(s).

*  Ideally SensorPush sensors would be located within range of a [SensorPush G1 WiFi Gateway](https://www.amazon.com/SensorPush-G1-WiFi-Gateway-Anywhere/dp/B01N17RWWV?tag=rynoshark-20) for continously collecting and publishing data from the sensors to the SensorPush cloud. However, SensorPush sensors can also synchronize historical data over Bluetooth when nearby to an iOS or Android device with the SensorPush app).

## Installation

If you have trouble with installation and configuration, visit the [SensorPush Home Assistant community discussion](https://community.home-assistant.io/t/sensorpush-humidity-and-temperature-sensors/105711).

### Step 1: Install Custom Components

Easiest is by setting up [Home Assistant Community Store (HACS)](https://github.com/custom-components/hacs) and then adding the "Integration" repository: *rsnodgrass/hass-sensorpush*. However you can also manually copy all the files in [custom_components/sensorpush/](https://github.com/rsnodgrass/hass-sensorpush/custom_components/sensorpush) directory to `/config/custom_components/sensorpush` on your Home Assistant installation.

### Step 2: Configure SensorPush

Example configuration.yaml entry:

```yaml
sensorpush:
  username: your@email.com
  password: your_password
```

## See Also

* [Community support for Home Assistant SensorPush integration](https://community.home-assistant.io/t/sensorpush-humidity-and-temperature-sensors/105711)
* [pysensorpush](https://github.com/rsnodgrass/pysensorpush) - Python interface to SensorPush cloud API

#### Hardware

* [SensorPush Wireless Thermometer/Hygrometer - Humidity & Temperature Smart Sensor](https://www.amazon.com/SensorPush-Wireless-Thermometer-Hygrometer-Android/dp/B01AEQ9X9I?tag=rynoshark-20)
* [SensorPush G1 WiFi Gateway](https://www.amazon.com/SensorPush-G1-WiFi-Gateway-Anywhere/dp/B01N17RWWV?tag=rynoshark-20)
* [SensorPush](https://sensorpush.com) (official product page)

