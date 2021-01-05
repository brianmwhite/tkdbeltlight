import time
import board
import neopixel
import random

# On a Raspberry pi, use this instead, not all pins are supported
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 121

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRBW

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=.50, auto_write=False, pixel_order=ORDER
)


while True:
	WHITE = (0, 0, 0, 255)
	RED = (255, 0, 0, 0)
	BLUE = (0, 0, 255, 0)
	GREEN = (0, 255, 0, 0)
	YELLOW = (255, 255, 0 ,0)
	OFF = (0, 0, 0, 0)

	pixels_per_strip = 11

	#white
	pixels[0:11] = [WHITE] * pixels_per_strip
	#yellow
	pixels[11:22] = [YELLOW] * pixels_per_strip
	#green stripe
	pixels[22:33] = [YELLOW] * pixels_per_strip
	#green
	pixels[33:44] = [GREEN] * pixels_per_strip
	#blue stripe
	pixels[44:55] = [GREEN] * pixels_per_strip
	#blue
	pixels[55:66] = [BLUE] * pixels_per_strip
	#red stripe
	pixels[66:77] = [OFF] * pixels_per_strip
	#red
	pixels[77:88] = [OFF] * pixels_per_strip
	#black stripe
	pixels[88:99] = [OFF] * pixels_per_strip	
	#double black stripe
	pixels[99:110] = [OFF] * pixels_per_strip	
	#poom/black belt
	pixels[110:121] = [OFF] * pixels_per_strip


	pixels.show()
	time.sleep(60)