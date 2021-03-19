import board
import neopixel
import time

pixel_pin = board.D18
num_pixels = 121
ORDER = neopixel.GRBW

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER
)

repeat_command_last_timestamp = 0
repeat_command_last_timestamp_delay = 1.0

def turnOnLights(pixelLedsToControl, showPrint = False):
	pixelLedsToControl.fill((0, 0, 0, 0))
	pixelLedsToControl.show()
	if showPrint:
		print("turning off lights...")

turnOnLights(pixels, showPrint=True)
while True:
	current_elapsed_time = time.monotonic()

	if current_elapsed_time - repeat_command_last_timestamp > repeat_command_last_timestamp_delay:
		repeat_command_last_timestamp = current_elapsed_time
		turnOnLights(pixels, showPrint=False)