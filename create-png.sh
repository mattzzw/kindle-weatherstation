#!/bin/sh

PWD=$(pwd)
export LD_LIBRARY_PATH=$PWD/lib

$PWD/weather2svg.py
$PWD/bin/rsvg-convert --background-color=white -o out.png weather-script-output.svg
$PWD/bin/pngcrush -q -c 0 out.png kindle-weather.png
