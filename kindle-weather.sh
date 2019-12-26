#!/bin/sh

PWD=$(pwd)
LOG="Weatherstation.log"
SLEEP_MINUTES=60

wait_wlan() {
  return `lipc-get-prop com.lab126.wifid cmState | grep CONNECTED | wc -l`
}

eips -c
eips 10 10 "Starting weatherstation"

### Prepare Kindle, shutdown framework etc.
echo "------------------------------------------------------------------------" >> $LOG
echo "`date '+%Y-%m-%d_%H:%M:%S'`: Starting up, killing framework et. al." >> $LOG
#/sbin/initctl stop framework
lipc-set-prop com.lab126.pillow disableEnablePillow disable
if [ -f /usr/sbin/wancontrol ]
then
    wancontrol wanoffkill
fi

echo "`date '+%Y-%m-%d_%H:%M:%S'`: Entering main loop..." >> $LOG

while true; do

	NOW=$(date +%s)

	let SLEEP_SECONDS=60*SLEEP_MINUTES
	let WAKEUP_TIME=$NOW+SLEEP_SECONDS
	echo `date '+%Y-%m-%d_%H:%M:%S'`: Wake-up time set for  `date -d @${WAKEUP_TIME}` >> $LOG

	### Enable CPU Powersave
	echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
	### Disable Screensaver
	lipc-set-prop com.lab126.powerd preventScreenSaver 1

	### Enable WIFI
	#lipc-set-prop com.lab126.wifid enable 1
	lipc-set-prop com.lab126.cmd wirelessEnable 1
	while wait_wlan; do
	  sleep 1
	done

	echo `date '+%Y-%m-%d_%H:%M:%S'`: WIFI enabled! >> $LOG

	### Get Weatherdata
	#echo `date '+%Y-%m-%d_%H:%M:%S'`: getting weatherdata >> $LOG
	rm -f $PWD/kindle-weather.png

	if $PWD/create-png.sh; then
	  eips -f -g $PWD/kindle-weather.png
	else
	  eips -f -g $PWD/error.png
      sleep 60
	fi

	#echo `date -d @${WAKEUP_TIME}` | xargs -0 eips
	BAT=$(gasgauge-info -s | sed s/%//)
#	echo $BAT | xargs -0 eips -f 1 1
	echo `date '+%Y-%m-%d_%H:%M:%S'`: battery level: $BAT >> $LOG

    # let screen update...
	sleep 2

	### Disable WIFI
#	lipc-set-prop com.lab126.cmd wirelessEnable 0

	### Set Wakeuptimer
#	echo 0 > /sys/class/rtc/rtc1/wakealarm
#	echo ${WAKEUP_TIME} > /sys/class/rtc/rtc1/wakealarm

    # set wake up time to one hour
	rtcwake -d /dev/rtc1 -m no -s $SLEEP_SECONDS
	### Go into Suspend to Memory (STR)
	echo `date '+%Y-%m-%d_%H:%M:%S'`: Sleeping now... >> $LOG
	echo "mem" > /sys/power/state
done
