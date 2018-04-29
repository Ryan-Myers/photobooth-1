#!/usr/bin/python
import pygame
pygame.init()
pygame.display.set_mode((100, 100), pygame.HWSURFACE | pygame.DOUBLEBUF)
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
done = False

while done==False:
  button_x = joystick.get_button(0)
  button_a = joystick.get_button(1)
  button_b = joystick.get_button(2)
  button_y = joystick.get_button(3)
  button_l = joystick.get_button(4)
  button_r = joystick.get_button(5)
  button_select = joystick.get_button(8)
  button_start = joystick.get_button(9)  
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT: # If user clicked close
      done=True # Flag that we are done so we exit this loop
    if event.type == pygame.JOYBUTTONDOWN:
      print("Joystick button pressed.")
      print(event.button)
    if event.type == pygame.JOYBUTTONUP:
      print("Joystick button released.")
      #done = True
      
  if button_x == 1:
    print("Button X pressed")
    done=True
  if button_a == 1:
    print("Button A pressed")
  
  # Limit to 20 frames per second
  clock.tick(20)
pygame.quit()