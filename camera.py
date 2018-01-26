#-------------------------------------------------------------------------------
# Name:        camera
# Purpose:     Functions for get and set camera state, capture photo
#
# Author:      VoRoN
#
# Created:     06.10.2017
# Copyright:   (c) VoRoN 2017
# Licence:     MIT
#-------------------------------------------------------------------------------
import subprocess

def trigger_capture(capturenumber):
	summary = subprocess.Popen(['fswebcam -r 640x480 --device /dev/video0 --input 0 --no-banner -q tmp/capture' + str(capturenumber) +'.jpg'], shell=True)