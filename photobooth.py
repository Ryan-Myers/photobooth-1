#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        photobooth
# Purpose:     Program for photoboxes
#
# Author:      VoRoN
#
# Created:     03.10.2017
# Copyright:   (c) VoRoN 2017
# Licence:     MIT
#-------------------------------------------------------------------------------

import os, glob, sys
os.environ['PYGAME_FREETYPE'] = ''
import pygame
import widgets
import json
from PIL import Image, ImageDraw, ImageFont
import threading, thread
import datetime
import camera
import printphoto
import subprocess
from shutil import copy
import re

WIN32 = (os.name != 'posix')
SCRIPT_PATH = os.path.dirname(sys.argv[0]) #Get's the path from the run command
TMP_FOLDER = 'tmp'
  
SETTINGS = {}
SCENES = []
PHOTO_FORMAT = []
screens = []
current_screen = 0
result_file_name = ''
TAKE_PHOTO = 4
photo_count = 1
thread_take_photo = None

delayScreen = 'Screen5'

done = False
COLLAGE = None
py_image = None

def getFilePath(filename):
  in_tmp_folder = os.path.join(SCRIPT_PATH, TMP_FOLDER, filename)
  in_img_folder = os.path.join(SCRIPT_PATH, 'img', filename)
  in_formats_folder = os.path.join(SCRIPT_PATH, 'formats', filename)
  if os.path.exists(in_img_folder):
    return in_img_folder
  if os.path.exists(in_tmp_folder):
    return in_tmp_folder
  if os.path.exists(in_formats_folder):
    return in_formats_folder

def current_screen_is(name):
  if current_screen >= len(screens):
    return False
  return screens[current_screen].name == name

def previous_screen_is(name):
  if current_screen >= len(screens) or\
    current_screen - 1 < 0:
    return False
  return screens[current_screen - 1].name == name

def set_current_screen(name):
  global current_screen
  for x in xrange(len(screens)):
    if screens[x].name == name:
      current_screen = x
      break

def get_screen_by_name(name):
  for x in xrange(len(screens)):
    if screens[x].name == name:
      return screens[x]
  return None

def next_screen():
  global current_screen
  current_screen += 1

def create_photo(photo_config):    
  scale = 2
  photo_format = tuple(map(lambda x: photo_config['dpi'] * x * scale,
                          photo_config['format']))
  
  image = Image.new('RGB', photo_format,
                  tuple(photo_config['background_color']))
  
  for item in photo_config['components']:
    item_type = item['type']
    
    if item_type == 'image':
      picture = item
      photo_name = getFilePath(picture['file'])
      photo = Image.open(photo_name)
      photo = photo.resize((picture['size'][0] * scale,
                  picture['size'][1] * scale))
      photo = photo.convert('RGBA')
      photo = photo.rotate(picture['angle'], expand=True)
      image.paste(photo, (picture['position'][0] * scale,
                picture['position'][1] * scale), photo)
      del photo
    
    if item_type == 'background-image':
      picture = item
      photo_name = getFilePath(picture['file'])
      photo = Image.open(photo_name)
      photo = photo.rotate(picture['angle'], expand=True)
      photo = photo.convert('RGBA')
      image.paste(photo)
      del photo
      
    if item_type == 'label':
      text_line = item['text']
      font = ImageFont.truetype(os.path.join(SCRIPT_PATH, item['font']), item['font_size'] * scale)
      d = ImageDraw.Draw(image)
      size = d.textsize(text_line, font)
      
      text = Image.new('RGBA', size, (255, 255, 255, 0))
      dt = ImageDraw.Draw(text)
      dt.text((0, 0), text_line, tuple(item['text_color']), font)
      text = text.rotate(item['angle'], expand=True)
      
      x, y = item['position'][0] * scale, item['position'][1] * scale
      width, height = photo_format
      textWidth, textHeight = text.size
      
      if item['vertical_center']:
        if item.has_key('size'):
          y = y + (item['size'][1] * 2 / 2 - textHeight / 2)
        else:
          y = height / 2 - textHeight / 2
      if item['horizontal_center']:
        if item.has_key('size'):
          x = x + (item['size'][0] * 2 / 2 - textWidth / 2)
        else:
          x = width / 2 - textWidth / 2
      
      image.paste(text, (x, y), text)
      del d
      del dt
  
  today = datetime.datetime.today()
  path = os.path.join(SCRIPT_PATH, 'results')
  
  if not os.path.exists(path):
    os.mkdir(path)
  filename = os.path.join(path, 'result_%s_%s.jpg' %
        (today.date().isoformat(), today.time().strftime('%H-%M-%S')))
  image.save(filename)
  global result_file_name
  print 'created: ' + filename
  result_file_name = filename
  
  if SETTINGS['preview_screen']:
    screen = get_screen_by_name('PreviewScreen')
    preview_picture = screen.getControlByName('preview')
    return image.resize(tuple(preview_picture.size)).transpose(Image.ROTATE_90)
  else:
    return None
      
def capture_photo(number):
  camera.trigger_capture(SCRIPT_PATH, number)    
        
def main():
  global WIN32, TMP_FOLDER, SETTINGS, SCENES, PHOTO_FORMAT, screens,\
    current_screen, result_file_name, TAKE_PHOTO, photo_count,\
    thread_take_photo, delayScreen, done, COLLAGE, py_image
  
  with open(os.path.join(SCRIPT_PATH, 'config.json'), 'r') as f:
    SCENES = json.loads(f.read())
  with open(os.path.join(SCRIPT_PATH, 'settings.json'), 'r') as f:
    SETTINGS = json.loads(f.read())
  for fileName in os.listdir(os.path.join(SCRIPT_PATH, 'formats')):
    with open(getFilePath(fileName), 'r') as f:
      frmt = json.loads(f.read())
      if isinstance(frmt, list):
        PHOTO_FORMAT += frmt
      else:
        PHOTO_FORMAT.append(frmt)
      
  
  pygame.init()
  pygame.joystick.init()
  pygame.mouse.set_visible(SETTINGS['show_mouse'])
  snes_pad = pygame.joystick.Joystick(0)
  snes_pad.init()
  
  selected_format = PHOTO_FORMAT[0]

  for frmt in PHOTO_FORMAT:
    if frmt['name'] == SETTINGS['print_format']:
      selected_format = frmt
      
  for component in selected_format['components']:
    if component.has_key('text') and\
       component['text'] == 'custom text':
       component['text'] = SETTINGS['custom_text']
  
  font_cache = widgets.FontCache()
  image_cache = widgets.ImageCache()
  for scene_item in SCENES:
    #Replace all relative paths with relative paths to the current execution path
    for scene_item_key, scene_item_value in scene_item.iteritems() :
      if isinstance(scene_item_value, list):
        for i in range(0, len(scene_item_value)):
          if type(scene_item_value[i]) is dict:
            if u'font' in scene_item_value[i]:
              scene_item[scene_item_key][i]['font'] = os.path.join(SCRIPT_PATH, scene_item_value[i]['font'])
            if u'image' in scene_item_value[i]:
              scene_item[scene_item_key][i]['image'] = os.path.join(SCRIPT_PATH, scene_item_value[i]['image'])
            if u'file' in scene_item_value[i]:
              scene_item[scene_item_key][i]['file'] = os.path.join(SCRIPT_PATH, scene_item_value[i]['file'])
    screens.append(widgets.Screen(scene_item, font_cache, image_cache))
  
  window_prop = pygame.HWSURFACE
  if not WIN32:
    window_prop |= pygame.FULLSCREEN
  
  window = pygame.display.set_mode((1280, 720), window_prop, 32)
  clock = pygame.time.Clock()
  
  delayScreen = SETTINGS['delay_screens']
  set_current_screen('MainScreen')
  while done == False:
    #button_x = snes_pad.get_button(0)
    #button_a = snes_pad.get_button(1)
    #button_b = snes_pad.get_button(2)
    #button_y = snes_pad.get_button(3)
    #button_l = snes_pad.get_button(4)
    #button_r = snes_pad.get_button(5)
    #button_select = snes_pad.get_button(8)
    #button_start = snes_pad.get_button(9)  
    
    for event in pygame.event.get():
      screens[current_screen].onevent(event)
      
      if event.type == pygame.KEYUP:
        if event.key == pygame.K_ESCAPE:
          done = True
      if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
        if event.button == 8: #SELECT button pressed
          done = True
          continue
      if event.type == pygame.QUIT:
        done = True
      if (event.type == pygame.MOUSEBUTTONUP or event.type == pygame.JOYBUTTONUP) and current_screen_is('PreviewScreen')\
        and SETTINGS['preview_screen_delay'] == 0 and (event.type == pygame.MOUSEBUTTONUP or event.button == 1):
        set_current_screen('EndScreen')
        pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
  
      if event.type == pygame.USEREVENT + 1:
        next_screen()
        
        if current_screen_is('StrikeAPoseScreen'):
          if thread_take_photo != None:
            thread_take_photo.join()
          t = threading.Thread(target=capture_photo, args=(photo_count, ))
          thread_take_photo = t
          t.start()
          pygame.time.set_timer(pygame.USEREVENT + 1, 
                      SETTINGS['strike_a_pose_delay'])
        
        if current_screen_is('PreviewScreen') and photo_count < TAKE_PHOTO:
          photo_count += 1
          if photo_count <= TAKE_PHOTO:
            set_current_screen(delayScreen)
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
            
        if previous_screen_is('WorkInProgress') and COLLAGE == None:
          pygame.time.set_timer(pygame.USEREVENT + 1, 0)
          if thread_take_photo != None:
            thread_take_photo.join()
          COLLAGE = create_photo(selected_format)
          
          py_image = None
          if COLLAGE != None:
            mode = COLLAGE.mode
            size = COLLAGE.size
            data = COLLAGE.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
          
          if SETTINGS['preview_screen']:
            set_current_screen('PreviewScreen')
          else:
            set_current_screen('EndScreen')
            
          if SETTINGS['preview_screen_delay'] != 0\
            and SETTINGS['preview_screen']:
            pygame.time.set_timer(pygame.USEREVENT + 1,
                        SETTINGS['preview_screen_delay'])
                        
        if current_screen_is('WorkInProgress') and py_image == None\
          and COLLAGE != None:
            set_current_screen('EndScreen')
  
        if current_screen_is('PreviewScreen') and photo_count >= TAKE_PHOTO:
          if COLLAGE != None:
            picture = screens[current_screen].getControlByName('preview')
            picture.image = py_image
            py_image = None
          else:
            pygame.time.set_timer(pygame.USEREVENT + 1, 100)
            set_current_screen('WorkInProgress')
  
        if current_screen_is('EndScreen') or current_screen_is('EndScreenCancelled'):
          pygame.time.set_timer(pygame.USEREVENT + 1,
                      SETTINGS['end_screen_delay'])
  
        if current_screen == len(screens):
          pygame.time.set_timer(pygame.USEREVENT + 1, 0)
          set_current_screen('MainScreen')
          
      if event.type == widgets.Button.EVENT_BUTTONCLICK:
        if event.name == 'btnStartClick':
          set_current_screen(delayScreen)
          pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
          photo_count = 1
          thread_take_photo = None
          COLLAGE = None
          py_image = None
          result_file_name = ''
          
        if event.name == 'btnPrintClick':
          printphoto.print_photo(SCRIPT_PATH, result_file_name, int(SETTINGS['print_copies']))
        
        if event.name == 'btnPrintCancelClick':
          set_current_screen('EndScreenCancelled')
          pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
          
        if event.name == 'btnPrintAllClick':
          printphoto.print_all()
        
        if event.name == 'btnOptionsClick':
          if current_screen_is('OptionsScreen'):
            updown = screens[current_screen].getControlByName("txtUpDown")
            SETTINGS['print_copies'] = int(updown.getText())
            caption = screens[current_screen].getControlByName("txtCaption")
            SETTINGS['custom_text'] = caption.getText()
            for component in selected_format['components']:
              if component.has_key('text') and\
                 component['text'] == 'custom text':
                component['text'] = SETTINGS['custom_text']
            with open('settings.json', 'w') as f:
              f.write(json.dumps(SETTINGS, indent=4))
            set_current_screen('MainScreen')
        
        if event.name == 'btnUpClick':
          ctrl = screens[current_screen].getControlByName("txtUpDown")
          value = int(ctrl.getText())
          ctrl.setText(str(value + 1))
          
        if event.name == 'btnDownClick':
          ctrl = screens[current_screen].getControlByName("txtUpDown")
          value = int(ctrl.getText())
          if value > 1:
            ctrl.setText(str(value - 1))
        
        if event.name == 'btnSaveClick':
          reg = re.compile('sda\d')
          dev = ''
          with open('/proc/partitions') as f:
            parts = f.readlines()
            parts = parts[2:]
            for part in parts:
              rows = part.split()
              if reg.search(rows[3]):
                dev = rows[3]
                break
          dest = ''
          regmt = re.compile(dev)
          mount = subprocess.Popen(['mount'], stdout=subprocess.PIPE,
                  shell=False)
          mounts = mount.stdout.readlines()
          for mpoint in mounts:
            points = mpoint.split()
            if regmt.search(points[0]):
              dest = points[2]

          if dest != '':
            path = 'results'
            lblSaved = screens[current_screen].getControlByName("lblSaved")
            files = glob.glob(path + '/*.jpg')
            numfiles = len(files)
            saved = 0
            i = 0
            while i != numfiles:
              f = files[i]
              try:
                copy(f, dest)
              except OSError as err:
                mount = subprocess.Popen(['sudo', 'mount',
                  '/dev/sda1', '-o', 'remount,rw'],
                  stdout=subprocess.PIPE,
                  shell=False)
                continue
              i += 1
              saved += 1
              lblSaved.setText('Saved: %d\\%d' % (saved, numfiles))
              ## hack, update screen
              screens[current_screen].render(window)
              pygame.display.flip()
          
    screens[current_screen].render(window)
      
    pygame.display.flip()
    clock.tick(60)
  pygame.quit()
  
if __name__ == '__main__':
    main()
