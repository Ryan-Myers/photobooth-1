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
	summary = subprocess.Popen(['raspistill -vf -hf --timeout 1 -o tmp/capture' + str(capturenumber) +'.jpg'], shell=True)