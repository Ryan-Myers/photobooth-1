#-------------------------------------------------------------------------------
# Name:        print
# Purpose:     Functions for printing picture
#
# Author:      Ryan Myers
#
# Created:     2018-01-25
# Copyright:   (c) Ryan Myers 2017
# Licence:     MIT
#-------------------------------------------------------------------------------
import subprocess

def print_photo(imagefile, copies_to_print):
  print 'Print photo'
  #./print-selphy -P Canon_SELPHY_CP1300 postcard ~/Downloads/IMG_20171111_161534.jpg
  #summary = subprocess.Popen(['fswebcam -r 640x480 --device /dev/video0 --input 0 --no-banner -q tmp/capture' + str(capturenumber) +'.jpg'], shell=True)
  for i in range(0, copies_to_print):
    print 'Printing: ' + imagefile
    sub = subprocess.Popen(['./print-selphy -P Canon_SELPHY_CP1300 postcard ' + imagefile], shell=True)
  
def print_all():
  path = 'results'
  files = glob.glob(path + '/*.jpg')
  for f in files:
    print 'Printing: ' + f
    #sub = subprocess.Popen(['./print-selphy -P Canon_SELPHY_CP1300 postcard ' + f], shell=True)