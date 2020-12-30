#!/usr/bin/env python3

import requests
from datetime import datetime
import json
import codecs
import subprocess
import config


api_url = config.api_url + config.api_param + '&appid=' + config.api_key

try:
    r = requests.get(api_url)
    r.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print ("Http Error: ",errh)
    exit(-1)
except requests.exceptions.RequestException as e:
    print ("Problem getting data: " + str(e))
    exit(-1)

# read the data from the URL and print it
weather = r.json()

# process SVG
output = codecs.open('weather-preprocess.svg', 'r', encoding='utf-8').read()

output = output.replace('#NOW', datetime.fromtimestamp(weather['current']['dt']).strftime('%d %b %Y, %H:%M:%S'))

# current weather
output = output.replace('#IC00',weather['current']['weather'][0]['icon'])
output = output.replace('#TN','{:.0f}'.format(weather['current']['temp']))
output = output.replace('#HI00','{:.0f}'.format(weather['daily'][0]['temp']['max']))
output = output.replace('#LO00','{:.0f}'.format(weather['daily'][0]['temp']['min']))
output = output.replace('#SUMNOW', weather['current']['weather'][0]['description'])
# output = output.replace('#SUMHR', weather['hourly'][0]['weather'][0]['description'])
output = output.replace('#DP0', '{:.0f}'.format(weather['daily'][0]['pop'] * 100))
output = output.replace('#DM0', '{:.2f}'.format(weather['daily'][0]['rain']))
output = output.replace('#DBP', '{:.0f}'.format(weather['daily'][0]['pressure']))
output = output.replace('#DHU', '{:.0f}'.format(weather['daily'][0]['humidity']))

output = output.replace('#SR', datetime.fromtimestamp(weather['daily'][0]['sunrise']).strftime('%H:%M'))
output = output.replace('#SS', datetime.fromtimestamp(weather['daily'][0]['sunset']).strftime('%H:%M'))


# battery
# depending on board type
# could also be e.g. /sys/devices/system/yoshi_battery/yoshi_battery0/battery_capacity
'''
proc_out = subprocess.Popen("gasgauge-info -s".split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
battery_capacity,stderr = proc_out.communicate()
output = output.replace('#BAT', battery_capacity.decode("utf-8"))
'''
# next 12 hours
for i in range(1, 13):
    istr = "{:02d}".format(i)
    output = output.replace('#IC'+istr, weather['hourly'][i]['weather'][0]['icon'])
    output = output.replace('#TM'+istr, str(datetime.fromtimestamp(weather['hourly'][i]['dt']).strftime('%H:%M')))
    output = output.replace('#TE'+istr, '{:.0f}'.format(weather['hourly'][i]['temp']))
    output = output.replace('#PP'+istr, '{:.0f}'.format(weather['hourly'][i]['pop']))
    precip = 0
    if 'rain' in weather['hourly'][i]:
        precip = weather['hourly'][i]['rain']
    if 'snow' in weather['hourly'][i]:
        precip += weather['hourly'][i]['snow']
    output = output.replace('#PA'+istr, '{:.0f}'.format(precip))

#next 7 days
for i in range (1, 8):
    istr = str(i)
    output = output.replace('#DA'+istr, str(datetime.fromtimestamp(weather['daily'][i]['dt']).strftime('%a %d.%-m.')))
    output = output.replace('#DI'+istr, weather['daily'][i]['weather'][0]['icon'])
    output = output.replace('#DH'+istr, '{:.0f}'.format(weather['daily'][i]['temp']['max']))
    output = output.replace('#DL'+istr, '{:.0f}'.format(weather['daily'][i]['temp']['min']))
    output = output.replace('#DP'+istr, '{:.0f}'.format(weather['daily'][i]['pop'] * 100))
    precip = 0
    if 'rain' in weather['daily'][i]:
        precip = weather['daily'][i]['rain']
    if 'snow' in weather['daily'][i]:
        precip += weather['daily'][i]['snow']
    output = output.replace('#DM'+istr, '{:.2f}'.format(precip))

#output = output.replace('#SUMDAILY', weather['daily']['summary'])

codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
