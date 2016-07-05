import RPi.GPIO as GPIO
import importlib
import time
import sys

# BOARD pin numbering
LedR	=	11
LedG	=	12
LedB	=	13
Buzz	=	15

#ds18b20 = '28-031467805fff'
#location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'

joystick	=	importlib.import_module('15_joystick_PS2')
ds18b20		=	importlib.import_module('26_ds18b20')
beep		=	importlib.import_module('10_active_buzzer')
rgb		=	importlib.import_module('02_rgb_led')

joystick.setup()
ds18b20.setup()
beep.setup(Buzz)
rgb.setup(LedR, LedG, LedB)

# Define LED colors for later use
color = {'Red':0xFF0000, 'Green':0x00FF00, 'Blue':0x0000FF}

def setup():
	global lowl, highl
	# Initialize the low and high temperature thresholds
	lowl = 29
	highl = 31

def edge():
	# Adjust temperature threshholds by using the joystick
	global lowl, highl
	action = joystick.direction()
	# Pressing the joystick button caused the code to terminate
	if action == 'Pressed':
		destroy()
		quit()
	# Up/Down decrease/increase the high temperature threshold
	if action == 'up' and highl <= 125:
		highl += 1
	if action == 'down' and lowl < highl-1:
		highl -= 1
	# Left/Right decrease/increase the low temperature threshold
	if action == 'right' and lowl < highl-1:
		lowl += 1
	if action == 'left' and lowl >= -5:
		lowl -= 1

def loop():
	while True:
		edge()
		temp = ds18b20.read()
		# Display the low, high and current temperatures in Celsius
		print 'The lower limit of temperature : %0.3f C', % lowl
		print 'The upper limit of temperature : %0.3f C', % highl
		print 'Current temperature : %0.3f C', % temp
		# Check to see if lower or upper temperature threshholds have been breached
		# Color code LED and play buzzer tone as follows:
		# - below lower threshhold: blue LED, buzzer sounds 3 times
		# - within limits: green LED, buzzer silent
		# - above upper threshhold: red LED, buzzer sounds 3 times
		if float(temp) < float(lowl):
			# Temperature is below lower threshold
			rgb.setColor(color['Blue'])
			for i in range(0, 3):
				beep.beep(0.5)
		if temp >= float(lowl) and temp <= float(highl):
			# Temperature is within thresholds
			rgb.setColor(color['Green'])
		if temp > float(highl):
			# Temperature is above higher threshold
			rgb.setColor(color['Red'])
			for i in range(0, 3):
				beep.beep(0.1)

def destroy():
	# Clean up before exiting
	beep.destroy()
	joystick.destroy()
	ds18b20.destroy()
	rgb.destroy()
	GPIO.cleanup()

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()
