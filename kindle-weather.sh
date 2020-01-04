#!/bin/sh

PWD=$(pwd)
LOG="/mnt/us/weatherstation.log"
SLEEP_MINUTES=60
FBINK="/mnt/us/extensions/MRInstaller/bin/K5/fbink -q"
FONT="regular=/usr/java/lib/fonts/Palatino-Regular.ttf"

wait_wlan() {
  return `lipc-get-prop com.lab126.wifid cmState | grep CONNECTED | wc -l`
}

### Prepare Kindle, shutdown framework etc.
echo "------------------------------------------------------------------------" >> $LOG
echo "`date '+%Y-%m-%d_%H:%M:%S'`: Starting up, killing framework et. al." >> $LOG

echo 0 > /sys/devices/platform/mxc_epdc_fb/graphics/fb0/rotate
$FBINK -w -c -f -m -t $FONT,size=20,top=410,bottom=0,left=0,right=0 "Starting weatherstation..." > /dev/null 2>&1
echo 3 > /sys/devices/platform/mxc_epdc_fb/graphics/fb0/rotate
sleep 1

### stop processes that we don't need
stop lab126_gui
stop otaupd
stop phd
stop tmd
stop x
stop todo
stop mcsd
sleep 2

### If we have a wan module installed...
#if [ -f /usr/sbin/wancontrol ]
#then
#    wancontrol wanoffkill
#fi

### Disable Screensaver
lipc-set-prop com.lab126.powerd preventScreenSaver 1

echo "`date '+%Y-%m-%d_%H:%M:%S'`: Entering main loop..." >> $LOG

while true; do

	NOW=$(date +%s)

	let SLEEP_SECONDS=60*SLEEP_MINUTES
	let WAKEUP_TIME=$NOW+SLEEP_SECONDS
	echo `date '+%Y-%m-%d_%H:%M:%S'`: Wake-up time set for  `date -d @${WAKEUP_TIME}` >> $LOG

    ### Dim Backlight
    echo -n 0 > /sys/devices/system/fl_tps6116x/fl_tps6116x0/fl_intensity

	### Enable CPU Powersave
	echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

	### Wait for WIFI
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

    # set wake up time to one hour
	rtcwake -d /dev/rtc1 -m no -s $SLEEP_SECONDS
	### Go into Suspend to Memory (STR)
	echo `date '+%Y-%m-%d_%H:%M:%S'`: Sleeping now... >> $LOG
	echo "mem" > /sys/power/state
done
