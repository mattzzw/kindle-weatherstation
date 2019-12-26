#!/usr/bin/env python3

import urllib.request
import ssl
from datetime import datetime
import json
import codecs
import subprocess
import config


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
try:
    darksky_url = urllib.request.urlopen(config.darksky_url + config.darksky_key + '/' +
                                        str(config.latitude) + ',' + str(config.longitude) +
                                        config.darksky_prm, context=ssl_context)
except Exception as e:
    print ("Problem getting data: " + str(e))
    exit(-1)

# read the data from the URL and print it
data = darksky_url.read()
weather = json.loads(data.decode('utf-8'))

# process SVG

output = codecs.open('weather-preprocess.svg', 'r', encoding='utf-8').read()

output = output.replace('#NOW', datetime.fromtimestamp(weather['currently']['time']).strftime('%d %b %Y, %H:%M:%S'))

# current weather
output = output.replace('#IC00',weather['currently']['icon'])
output = output.replace('#TN','{:.0f}'.format(weather['currently']['temperature']))
output = output.replace('#HI00','{:.0f}'.format(weather['daily']['data'][0]['temperatureHigh']))
output = output.replace('#LO00','{:.0f}'.format(weather['daily']['data'][0]['temperatureLow']))
output = output.replace('#SUMNOW', weather['currently']['summary'])
output = output.replace('#SUMHR', weather['hourly']['summary'])
output = output.replace('#DP0', '{:.0f}'.format(weather['daily']['data'][0]['precipProbability'] * 100))
output = output.replace('#DM0', '{:.2f}'.format(weather['daily']['data'][0]['precipIntensity'], 2))
output = output.replace('#DBP', '{:.0f}'.format(weather['daily']['data'][0]['pressure'], 2))

output = output.replace('#SR', datetime.fromtimestamp(weather['daily']['data'][0]['sunriseTime']).strftime('%H:%M'))
output = output.replace('#SS', datetime.fromtimestamp(weather['daily']['data'][0]['sunsetTime']).strftime('%H:%M'))

# battery
# depending on board type
# could also be e.g. /sys/devices/system/yoshi_battery/yoshi_battery0/battery_capacity
proc_out = subprocess.Popen("gasgauge-info -s".split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
battery_capacity,stderr = proc_out.communicate()
output = output.replace('#BAT', battery_capacity.decode("utf-8"))


# next 12 hours
for i in range(1, 13):
    istr = "{:02d}".format(i)
    output = output.replace('#IC'+istr, weather['hourly']['data'][i]['icon'])
    output = output.replace('#TM'+istr, str(datetime.fromtimestamp(weather['hourly']['data'][i]['time']).strftime('%H:%M')))
    output = output.replace('#TE'+istr, '{:.0f}'.format(weather['hourly']['data'][i]['temperature']))
    output = output.replace('#PP'+istr, '{:.0f}'.format(weather['hourly']['data'][i]['precipProbability'] * 100))
    output = output.replace('#PA'+istr, '{:.2f}'.format(weather['hourly']['data'][i]['precipIntensity'], 2))

#next 7 days
for i in range (1, 8):
    istr = str(i)
    output = output.replace('#DA'+istr, str(datetime.fromtimestamp(weather['daily']['data'][i]['time']).strftime('%a %d.%-m.')))
    output = output.replace('#DI'+istr, weather['daily']['data'][i]['icon'])
    output = output.replace('#DH'+istr, '{:.0f}'.format(weather['daily']['data'][i]['temperatureHigh']))
    output = output.replace('#DL'+istr, '{:.0f}'.format(weather['daily']['data'][i]['temperatureLow']))
    output = output.replace('#DP'+istr, '{:.0f}'.format(weather['daily']['data'][i]['precipProbability'] * 100))
    output = output.replace('#DM'+istr, '{:.2f}'.format(weather['daily']['data'][i]['precipIntensity'], 2))



output = output.replace('#SUMDAILY', weather['daily']['summary'])

codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
