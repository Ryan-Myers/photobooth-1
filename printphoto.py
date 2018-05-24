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
import subprocess, os

def print_photo(SCRIPT_PATH, imagefile, copies_to_print):
  for i in range(0, copies_to_print):
    print 'Printing: ' + imagefile
    #sub = subprocess.Popen([os.path.join(SCRIPT_PATH, 'print-selphy') + ' -P Canon_SELPHY_CP1300 postcard ' + imagefile], shell=True)
    sub = subprocess.Popen(['lpr -P Canon_SELPHY_CP1300 ' + imagefile], shell=True)
    
def print_all():
  path = 'results'
  files = glob.glob(path + '/*.jpg')
  for f in files:
    print 'Printing: ' + f
    #sub = subprocess.Popen(['./print-selphy -P Canon_SELPHY_CP1300 postcard ' + f], shell=True)