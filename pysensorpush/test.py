#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# sensorpush.py, Copyright Bjoern Olausson
# -----------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# To view the license visit
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# or write to
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#
# This Python 3 program is intended to query the SensorPush API and
# persistantly store temeprature an humidity values in InfluxDB
#

import sys
import json
import requests
import time
import datetime
import argparse
from requests.adapters import HTTPAdapter
from pprint import pprint
from influxdb import InfluxDBClient

# __version__ = '1.3.0'
# __version_info__ = tuple([int(num) for num in __version__.split('.')])

LOGIN = 'SensorPush login'
PASSWD = 'SensorPush password'
IFDB_IP = 'InfluxDP IP'
IFDB_PORT = 'InfluxDP port'
IFDB_USER = 'InfluxDP user'
IFDB_PW = 'InfluxDB password'
IFDB_DB = 'InfluxDP database'

RETRYWAIT = 60
MAXRETRY = 3

API_URL_BASE = 'https://api.sensorpush.com/api/v1'
API_URL_OA_AUTH = f'{API_URL_BASE}/oauth/authorize'
API_URL_OA_ATOK = f'{API_URL_BASE}/oauth/accesstoken'
API_URL_GW = f'{API_URL_BASE}/devices/gateways'
API_URL_SE = f'{API_URL_BASE}/devices/sensors'
API_URL_SPL = f'{API_URL_BASE}/samples'


HTTP_OA_HEAD = {'accept': 'application/json',
                'Content-Type': 'application/json'}

parser = argparse.ArgumentParser(
    description='Queries SensorPus API and stores the temp and humidity\
                readings in InfluxDB')
parser.add_argument(
    '-s',
    '--start',
    dest='starttime',
    default='',
    type=str,
    help='start query at time (e.g. "2019-07-25T00:10:41+0200")')
parser.add_argument(
    '-p',
    '--stop',
    dest='stoptime',
    default='',
    type=str,
    help='Stop query at time (e.g. "2019-07-26T00:10:41+0200")')
parser.add_argument(
    '-b',
    '--backlog',
    dest='backlog',
    default='1440',
    type=int,
    help='Minutes back in time to fetch data (default 1440 minutes [24 h])')
parser.add_argument(
    '-t',
    '--timestep',
    dest='timestep',
    default='720',
    type=int,
    help='Time slice per query (in minutes) to fetch\
         (default 720 minutes [12 h])')
parser.add_argument(
    '-q',
    '--querylimit',
    dest='qlimit',
    default='0',
    type=int,
    help='Number of samples to return per sensor (default no limit)')
parser.add_argument('-d',
                    '--delay',
                    dest='delay',
                    default='60',
                    type=int,
                    help='Delay in seconds between queries')
parser.add_argument(
    '-l',
    '--listsensors',
    dest='listsensors',
    action='store_true',
    help='Show a list of sensors and exit')
parser.add_argument(
    '-g',
    '--listgateways',
    dest='listgateways',
    action='store_true',
    help='Show a list of gateways and exit')
parser.add_argument(
    '-i',
    '--sensorlist',
    dest='sensorlist',
    nargs='+',
    type=str,
    help='List of sensor IDs to query')
parser.add_argument(
    '-x',
    '--dryrun',
    dest='dryrun',
    action='store_true',
    help='Do not write anything to the database,\
        just print what would have been written')

args = parser.parse_args()

starttime = args.starttime
stoptime = args.stoptime
backlog = args.backlog
timesteps = args.timestep
qlimit = args.qlimit
delay = args.delay
listsensors = args.listsensors
listgateways = args.listgateways
sensorlist = args.sensorlist
dryrun = args.dryrun


def local_time_offset(t=None):
    """Return offset of local zone from GMT, either at present or at time t."""
    # python2.3 localtime() can't take None
    if t is None:
        t = time.time()

    if time.localtime(t).tm_isdst and time.daylight:
        return -time.altzone / 3600
    else:
        return -time.timezone / 3600


# Initiate the InfluxDB client ------------------------------------------------
ifdbc = InfluxDBClient(host=IFDB_IP,
                       port=IFDB_PORT,
                       username=IFDB_USER,
                       password=IFDB_PW,
                       database=IFDB_DB)


# Try to get the proper UTC time offseet --------------------------------------
mytz = datetime.timezone(datetime.timedelta(hours=local_time_offset()))
currenttime = datetime.datetime.now(tz=mytz)

if not starttime:
    starttime = currenttime - datetime.timedelta(minutes=int(backlog))
else:
    starttime = datetime.datetime.strptime(args.starttime, '%Y-%m-%dT%X%z')

if not stoptime:
    stoptime = currenttime
else:
    stoptime = datetime.datetime.strptime(args.stoptime, '%Y-%m-%dT%X%z')

starttimestr = 'Start: ' + datetime.date.strftime(starttime, '%Y-%m-%dT%X%z')
stoptimestr = 'Stop:  ' + datetime.date.strftime(stoptime, '%Y-%m-%dT%X%z')

timelist = []
while starttime <= stoptime:
    start = datetime.date.strftime(starttime, '%Y-%m-%dT%X%z')

    try:
        nextstop = newstartt + datetime.timedelta(minutes=int(timesteps))
    except BaseException:
        nextstop = starttime + datetime.timedelta(minutes=int(timesteps))

    stop = datetime.date.strftime(nextstop, '%Y-%m-%dT%X%z')

    # pprint(start)
    # pprint(stop)

    currenttime = datetime.datetime.now(tz=mytz)
    starttime = nextstop - datetime.timedelta(minutes=30)
    newstartt = nextstop

    # pprint(starttime)
    # pprint(stoptime)

    timelist.extend([[start, stop]])

    iterations = len(timelist)

# Set retries for requests ----------------------------------------------------
s = requests.Session()
s.mount(API_URL_BASE, HTTPAdapter(max_retries=10))


# get API oauth authorization string ------------------------------------------
pprint('Fetching API oauth authorization string')
HTTP_DATA = json.dumps({'email': LOGIN, 'password': PASSWD})
r = s.post(API_URL_OA_AUTH,
           headers=HTTP_OA_HEAD,
           data=HTTP_DATA)

if r.status_code == 200:
    auth = r.content.decode('utf-8')
else:
    pprint('Auth request failed')
    pprint(r)
    sys.exit()


# get API oauth access token --------------------------------------------------
pprint('Fetching API oauth access token')
HTTP_DATA = auth
r = s.post(API_URL_OA_ATOK,
           headers=HTTP_OA_HEAD,
           data=HTTP_DATA)

if r.status_code == 200:
    atok = json.loads(r.content.decode('utf-8'))['accesstoken']
else:
    pprint('Access token request failed')
    pprint(r)
    sys.exit()

# Create header for further requests:
HTTP_HEAD = {'accept': 'application/json',
             'Authorization': atok}

# Get a list of gateways ------------------------------------------------------
pprint('Fetching the list of gateways')
HTTP_DATA = json.dumps({})
r = s.post(API_URL_GW,
           headers=HTTP_HEAD,
           data=HTTP_DATA)

if r.status_code == 200:
    gateways = json.loads(r.content.decode('utf-8'))
else:
    pprint('Could not fetch the list of gateways')
    pprint(r)
    sys.exit()

if listgateways:
    for id in gateways.keys():
        # gwname = gateways[id]["name"].encode('utf-8')
        gwname = gateways[id]["name"]
        print(f'---------------{gwname}---------------')
        print(f'Last alert               : {gateways[id]["last_alert"]}')
        print(f'Last seen                : {gateways[id]["last_seen"]}')
        print(f'Message                  : {gateways[id]["message"]}')
        print(f'Paired                   : {gateways[id]["paired"]}')
        print(f'Version                  : {gateways[id]["version"]}')
        print('------------------------------------------------------------')
        print('')

    sys.exit(0)

# Get a list of sensors -------------------------------------------------------
pprint('Fetching the list of sensors')
HTTP_DATA = json.dumps({})
r = s.post(API_URL_SE,
           headers=HTTP_HEAD,
           data=HTTP_DATA)

if r.status_code == 200:
    sensors = json.loads(r.content.decode('utf-8'))
else:
    pprint('Could not fetch the list of sensors')
    pprint(r)
    sys.exit()

if listsensors:
    for id in sensors.keys():
        # sensorname = sensors[id]["name"].encode('utf-8')
        sensorname = sensors[id]["name"]
        print(
            f'---------------{sensorname}---------------')
        print(
            f'Id                       :\
            {sensors[id]["id"]}')
        print(
            f'DevId                    :\
            {sensors[id]["deviceId"]}')
        print(
            f'Address                  :\
            {sensors[id]["address"]}')
        print(
            f'Active                   :\
            {sensors[id]["active"]}')
        print(
            f'Battery voltage          :\
            {sensors[id]["battery_voltage"]}')
        print(
            f'Alert (humidity)         :\
            {sensors[id]["alerts"]["humidity"]["enabled"]}')
        print(
            f'Alert (temperature)      :\
            {sensors[id]["alerts"]["temperature"]["enabled"]}')
        print(
            f'Calibration (humidity)   :\
            {sensors[id]["calibration"]["humidity"]}')
        print(
            f'Calibration (temperature):\
            {sensors[id]["calibration"]["temperature"]}')
        print('------------------------------------------------------------')
        print('')

    sys.exit(0)
# names = [sensors[key]['name'] for key in sensors.keys()]

# Get samples -----------------------------------------------------------------
pprint('-------------------------------------------------------------------')
pprint(starttimestr)
pprint(stoptimestr)
pprint('-------------------------------------------------------------------')

pprint('Iterations required: ' + str(iterations))
pprint('-------------------------------------------------------------------')

iteration = 1
retrycount = 0

for item in timelist:
    failed = True

    while failed:
        try:
            pprint(f'Iteration {iteration}/{iterations}')

            query = {'startTime': item[0], 'stopTime': item[1]}

            if qlimit != 0:
                query['limit'] = qlimit

            if sensorlist:
                query['sensors'] = sensorlist

            HTTP_DATA = json.dumps(query)

            r = s.post(API_URL_SPL,
                       headers=HTTP_HEAD,
                       data=HTTP_DATA)

            if r.status_code == 200:
                samples = json.loads(r.content.decode('utf-8'))
                # pprint(samples)
            else:
                raise ValueError('Could not fetch samples')

            truncated = samples['truncated']
            numsamples = samples['total_samples']
            numsensosrs = samples['total_sensors']

            pprint('Request truncated: ' + str(truncated))

            if truncated:
                pprint('You might want to consider reducing the time slices')

            pprint('Number of samples fetched: ' + str(numsamples))
            pprint('Number of sensors queried: ' + str(numsensosrs))

            # Push data to influxdb -------------------------------------------
            measurement = []
            for key in samples['sensors'].keys():
                for item in samples['sensors'][key]:
                    celsius = float(
                        round(
                            (item['temperature'] - 32) * 5.0 / 9.0,
                            2))
                    measurement.extend([
                        {
                            'measurement': 'SensorPush',
                            'tags': {
                                'sensor_id': key,
                                'sensor_name': sensors[key]['name'],
                            },
                            'fields': {
                                'temperature': celsius,
                                'humidity': float(item['humidity']),
                            },
                            'time': item['observed']
                        }
                    ])
            # pprint(measurement)
            if dryrun:
                pprint(
                    '------------Data that would have been written---------')
                pprint(measurement)
                pprint(
                    '------------------------------------------------------')
            else:
                ifdbc.write_points(measurement)

            iteration += 1

            if iterations > 1:
                pprint(
                    '------------------------------------------------------')
                pprint(f'sleeping for {delay} seconds')
                pprint(
                    '------------------------------------------------------')

                time.sleep(delay)

        except Exception as e:
            retrycount += 1
            pprint('')
            pprint('##################Somthing went wrong################')
            pprint('~~~~~~~~~~~~Exception~~~~~~~~~~~~~')
            pprint(e)
            pprint('~~~~~~~~~~~~Request status code~~~~~~~~~~~~~')
            pprint(r.status_code)
            pprint('~~~~~~~~~~~~~~~~~~~~~~~~~')
            pprint(r.headers)
            pprint('~~~~~~~~~~~~Request content~~~~~~~~~~~~~')
            pprint(r.content.decode('utf-8'))
            pprint(
                '------------------------------------------------------')
            pprint(f'Retrying iteration {iteration}/{iterations}')
            pprint(f'Try {retrycount}/{MAXRETRY}')
            pprint(f'sleeping for {RETRYWAIT} seconds before next try')
            pprint('######################################################')
            pprint('')
            if retrycount >= MAXRETRY:
                pprint('Reached max retries ({MAXRETRY}) Stopping now!')
                sys.exit()
            time.sleep(RETRYWAIT)
            continue
        else:
            failed = False

