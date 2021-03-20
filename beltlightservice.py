import time
import signal
import board
import neopixel
import random
import paho.mqtt.client as mqtt
import pickle

# sudo ./deploy_local.sh

# sudo systemctl start beltlight
# sudo systemctl stop beltlight
# sudo systemctl restart beltlight

# systemctl status beltlight
# journalctl -u beltlight -f

# sudo systemctl disable beltlight
# sudo cp beltlight.service /etc/systemd/system/
# sudo systemctl enable beltlight

MQTT_HOST = "pihome.local"
MQTT_PORT = 1883

MQTT_SETON_PATH = "home/office/lights/beltlight/setOn"
MQTT_GETON_PATH = "home/office/lights/beltlight/getOn"

ON_VALUE = "ON"
OFF_VALUE = "OFF"

PICKLE_FILE_LOCATION = "/home/pi/beltlight/beltlight.pickle"

last_time_status_check_in = 0
status_checkin_delay = 5.0

belt_light_state = {'belt_light_is_on': False}

# On a Raspberry pi, use this instead, not all pins are supported
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 121
pixels_per_strip = 11

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
YELLOW = (255, 255, 0, 0)
OFF = (0, 0, 0, 0)


class exit_monitor_setup:
    exit_now_flag_raised = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.exit_now_flag_raised = True

# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
    print("MQTT: Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    client.subscribe(MQTT_SETON_PATH)


def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))

# The callback for when a PUBLISH message is received from the server.


def on_message(client, userdata, message):
    global last_time_status_check_in

    if message.topic == MQTT_SETON_PATH:
        last_time_status_check_in = time.monotonic()

        if str(message.payload.decode("utf-8")) == ON_VALUE:
            turnOnLights()
            client.publish(MQTT_GETON_PATH, ON_VALUE)
        elif str(message.payload.decode("utf-8")) == OFF_VALUE:
            turnOffLights()
            client.publish(MQTT_GETON_PATH, OFF_VALUE)


def turnOffLights(change_state=True):
    global belt_light_state
    belt_light_state['belt_light_is_on'] = False

    if change_state:
        print("turning lights OFF ....")
        try:
            with open(PICKLE_FILE_LOCATION, 'wb') as datafile:
                pickle.dump(belt_light_state, datafile)
                print(
                    f"saved beltlight state={belt_light_state['belt_light_is_on']}")
        except:
            pass
    
    pixels.fill((0, 0, 0, 0))
    pixels.show()


def turnOnLights(change_state=True):
    global belt_light_state
    belt_light_state['belt_light_is_on'] = True

    if change_state:
        print("turning lights ON ....")
        try:
            with open(PICKLE_FILE_LOCATION, 'wb') as datafile:
                pickle.dump(belt_light_state, datafile)
                print(
                    f"saved beltlight state={belt_light_state['belt_light_is_on']}")
        except:
            pass

    # white
    pixels[0:11] = [WHITE] * pixels_per_strip
    # yellow
    pixels[11:22] = [YELLOW] * pixels_per_strip
    # green stripe
    pixels[22:33] = [YELLOW] * pixels_per_strip
    # green
    pixels[33:44] = [GREEN] * pixels_per_strip
    # blue stripe
    pixels[44:55] = [GREEN] * pixels_per_strip
    # blue
    pixels[55:66] = [BLUE] * pixels_per_strip
    # red stripe
    pixels[66:77] = [BLUE] * pixels_per_strip
    # red
    pixels[77:88] = [OFF] * pixels_per_strip
    # black stripe
    pixels[88:99] = [OFF] * pixels_per_strip
    # double black stripe
    pixels[99:110] = [OFF] * pixels_per_strip
    # poom/black belt
    pixels[110:121] = [OFF] * pixels_per_strip

    pixels.show()


if __name__ == '__main__':
    exit_monitor = exit_monitor_setup()
    
    try:
        with open(PICKLE_FILE_LOCATION, 'rb') as datafile:
            belt_light_state = pickle.load(datafile)
            print(f"loaded beltlight state={belt_light_state['belt_light_is_on']}")
    except (FileNotFoundError, pickle.UnpicklingError):
        print("failed to load beltlight state, default=OFF")
        belt_light_state['belt_light_is_on'] = False
        pass
	
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    # see below, not sure if sleep is needed here, probably not
    time.sleep(0.001)

    print("started belt light service...")
    last_time_status_check_in = time.monotonic()

    if belt_light_state['belt_light_is_on']:
        turnOnLights()
    else:
        turnOffLights()

    while not exit_monitor.exit_now_flag_raised:
        # added time.sleep 1 ms after seeing 100% CPU usage
        # found this solution https://stackoverflow.com/a/41749754
        time.sleep(0.001)
        current_seconds_count = time.monotonic()

        if current_seconds_count - last_time_status_check_in > status_checkin_delay:
            last_time_status_check_in = current_seconds_count

            if belt_light_state['belt_light_is_on']:
                client.publish(MQTT_GETON_PATH, ON_VALUE)
            else:
                client.publish(MQTT_GETON_PATH, OFF_VALUE)

    client.loop_stop()
    client.disconnect()
    pixels.deinit()
    print("belt light noise service ended")
