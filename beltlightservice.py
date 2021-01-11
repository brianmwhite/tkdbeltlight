import time
import board
import neopixel
import random
import paho.mqtt.client as mqtt

# On a Raspberry pi, use this instead, not all pins are supported
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 121
beltLightIsOn = False

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRBW

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=.50, auto_write=False, pixel_order=ORDER
)

WHITE = (0, 0, 0, 255)
RED = (255, 0, 0, 0)
BLUE = (0, 0, 255, 0)
GREEN = (0, 255, 0, 0)
YELLOW = (255, 255, 0 ,0)
OFF = (0, 0, 0, 0)

pixels_per_strip = 11

last_time_status_check_in = 0
status_checkin_delay = 5.0

repeat_command_last_timestamp = 0
repeat_command_last_timestamp_delay = 60.0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("MQTT: Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("$SYS/#")
	client.subscribe("home/office/lights/beltlight/setOn")

def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
	global last_time_status_check_in
	global repeat_command_last_timestamp
	# print("message received ", str(message.payload.decode("utf-8")))
	# print("message topic=", message.topic)
	# print("message qos=", message.qos)
	# print("message retain flag=", message.retain)

	if message.topic == "home/office/lights/beltlight/setOn":
		repeat_command_last_timestamp = time.monotonic() + 5
		last_time_status_check_in = time.monotonic()

		if str(message.payload.decode("utf-8")) == "ON":
			turnOnLights(showPrint=True)
			client.publish("home/office/lights/beltlight/getOn","ON")
		elif str(message.payload.decode("utf-8")) == "OFF":
			turnOffLights(showPrint=True)
			client.publish("home/office/lights/beltlight/getOn","OFF")

def turnOffLights(showPrint = False):
	global beltLightIsOn
	pixels.fill((0, 0, 0, 0))
	pixels.show()
	beltLightIsOn = False
	if showPrint:
		print("turning lights OFF ....")

def turnOnLights(showPrint = False):
	global beltLightIsOn
	beltLightIsOn = True
	if showPrint:
		print("turning lights ON ....")

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
	pixels[66:77] = [BLUE] * pixels_per_strip
	#red
	pixels[77:88] = [OFF] * pixels_per_strip
	#black stripe
	pixels[88:99] = [OFF] * pixels_per_strip
	#double black stripe
	pixels[99:110] = [OFF] * pixels_per_strip
	#poom/black belt
	pixels[110:121] = [OFF] * pixels_per_strip

	pixels.show()

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect("pihome.local", 1883, 60)
client.publish("home/office/lights/beltlight/getOn","OFF")
turnOffLights()
last_time_status_check_in = time.monotonic()

client.loop_start()
# see below, not sure if sleep is needed here, probably not
time.sleep(0.001)

try:

	while True:
		# added time.sleep 1 ms after seeing 100% CPU usage
		# found this solution https://stackoverflow.com/a/41749754
		time.sleep(0.001)
		current_seconds_count = time.monotonic()
		if current_seconds_count - last_time_status_check_in > status_checkin_delay:
			last_time_status_check_in = current_seconds_count
			if beltLightIsOn:
				client.publish("home/office/lights/beltlight/getOn","ON")
			else:
				client.publish("home/office/lights/beltlight/getOn","OFF")
		if current_seconds_count - repeat_command_last_timestamp > repeat_command_last_timestamp_delay:
			repeat_command_last_timestamp = current_seconds_count
			if beltLightIsOn:
				turnOnLights(showPrint=False)
			else:
				turnOffLights(showPrint=False)

except KeyboardInterrupt:
	pass

client.loop_stop()
client.disconnect()
pixels.deinit()