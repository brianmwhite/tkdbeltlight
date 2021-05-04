import configparser
import pickle
import signal
import time

import board
import neopixel
import paho.mqtt.client as mqtt

# ./deploy_local.sh
# ./svcmenu.py

# sudo systemctl start beltlight
# sudo systemctl stop beltlight
# sudo systemctl restart beltlight

# systemctl status beltlight
# journalctl -u beltlight -f

# sudo systemctl disable beltlight
# sudo cp beltlight.service /etc/systemd/system/
# sudo systemctl enable beltlight

# git commands to ignore changes specific file
# git update-index config.ini
# git update-index --skip-worktree config.ini
# git update-index --no-skip-worktree config.ini
# git ls-files -v|grep '^S'

config = configparser.ConfigParser()
config.read('/home/pi/beltlight/config.ini')

config_settings = config['SETTINGS']

MQTT_HOST = config_settings.get('MQTT_HOST')
MQTT_PORT = config_settings.getint('MQTT_PORT')

MQTT_SETON_PATH = config_settings.get("MQTT_SETON_PATH")
MQTT_GETON_PATH = config_settings.get("MQTT_GETON_PATH")

ON_VALUE = config_settings.get("ON_VALUE")
OFF_VALUE = config_settings.get("OFF_VALUE")

PICKLE_FILE_LOCATION = config_settings.get("PICKLE_FILE_LOCATION")
DEVICE_STATE = {'light_is_on': False}

status_checkin_delay = config_settings.getfloat("status_checkin_delay")
last_time_status_check_in = 0.0

# python conversion
# tuple(bytes.fromhex("ffff0000")
# bytes((255, 255, 0, 0)).hex()

row_colors = config['ROW_COLORS']

ROW_11 = tuple(bytes.fromhex(row_colors.get("ROW_11")))
ROW_10 = tuple(bytes.fromhex(row_colors.get("ROW_10")))
ROW_09 = tuple(bytes.fromhex(row_colors.get("ROW_09")))
ROW_08 = tuple(bytes.fromhex(row_colors.get("ROW_08")))
ROW_07 = tuple(bytes.fromhex(row_colors.get("ROW_07")))
ROW_06 = tuple(bytes.fromhex(row_colors.get("ROW_06")))
ROW_05 = tuple(bytes.fromhex(row_colors.get("ROW_05")))
ROW_04 = tuple(bytes.fromhex(row_colors.get("ROW_04")))
ROW_03 = tuple(bytes.fromhex(row_colors.get("ROW_03")))
ROW_02 = tuple(bytes.fromhex(row_colors.get("ROW_02")))
ROW_01 = tuple(bytes.fromhex(row_colors.get("ROW_01")))


# neopixel setup
PIXEL_DATA_PIN = board.D18
NUMBER_OF_TOTAL_LINKED_PIXELS = 121
PIXELS_PER_UNIT = 11

ORDER = neopixel.GRBW

pixels = neopixel.NeoPixel(
    PIXEL_DATA_PIN, NUMBER_OF_TOTAL_LINKED_PIXELS, brightness=1.0, auto_write=False, pixel_order=ORDER
)


class exit_monitor_setup:
    exit_now_flag_raised = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.exit_now_flag_raised = True


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("MQTT: Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    client.subscribe(MQTT_SETON_PATH)


# The callback for when a DISCONNECT message is received from the server.
def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    global last_time_status_check_in

    if message.topic == MQTT_SETON_PATH:
        last_time_status_check_in = time.monotonic()

        if str(message.payload.decode("utf-8")) == ON_VALUE:
            turn_on_lights()
            client.publish(MQTT_GETON_PATH, ON_VALUE)
        elif str(message.payload.decode("utf-8")) == OFF_VALUE:
            turn_off_lights()
            client.publish(MQTT_GETON_PATH, OFF_VALUE)


def turn_off_lights(change_state=True):
    global DEVICE_STATE
    DEVICE_STATE['light_is_on'] = False

    if change_state:
        print("turning lights OFF ....")
        try:
            with open(PICKLE_FILE_LOCATION, 'wb') as datafile:
                pickle.dump(DEVICE_STATE, datafile)
                print(
                    f"saved light state={DEVICE_STATE['light_is_on']}")
        except pickle.UnpicklingError as e:
            print(e)
            pass
        except (AttributeError, EOFError, ImportError, IndexError) as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            pass

    pixels.fill((0, 0, 0, 0))
    pixels.show()


def turn_on_lights(change_state=True):
    global DEVICE_STATE
    DEVICE_STATE['light_is_on'] = True

    if change_state:
        print("turning lights ON ....")
        try:
            with open(PICKLE_FILE_LOCATION, 'wb') as datafile:
                pickle.dump(DEVICE_STATE, datafile)
                print(
                    f"saved light state={DEVICE_STATE['light_is_on']}")
        except pickle.UnpicklingError as e:
            print(e)
            pass
        except (AttributeError, EOFError, ImportError, IndexError) as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            pass

    # white
    pixels[0:11] = [ROW_01] * PIXELS_PER_UNIT
    # yellow
    pixels[11:22] = [ROW_02] * PIXELS_PER_UNIT
    # green stripe
    pixels[22:33] = [ROW_03] * PIXELS_PER_UNIT
    # green
    pixels[33:44] = [ROW_04] * PIXELS_PER_UNIT
    # blue stripe
    pixels[44:55] = [ROW_05] * PIXELS_PER_UNIT
    # blue
    pixels[55:66] = [ROW_06] * PIXELS_PER_UNIT
    # red stripe
    pixels[66:77] = [ROW_07] * PIXELS_PER_UNIT
    # red
    pixels[77:88] = [ROW_08] * PIXELS_PER_UNIT
    # black stripe
    pixels[88:99] = [ROW_09] * PIXELS_PER_UNIT
    # double black stripe
    pixels[99:110] = [ROW_10] * PIXELS_PER_UNIT
    # poom/black belt
    pixels[110:121] = [ROW_11] * PIXELS_PER_UNIT

    pixels.show()


if __name__ == '__main__':
    exit_monitor = exit_monitor_setup()

    try:
        with open(PICKLE_FILE_LOCATION, 'rb') as datafile:
            DEVICE_STATE = pickle.load(datafile)
            print(f"loaded light state={DEVICE_STATE['light_is_on']}")
    except (FileNotFoundError, pickle.UnpicklingError):
        print("failed to load light state, default=OFF")
        DEVICE_STATE['light_is_on'] = False
        pass

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    # see below, not sure if sleep is needed here, probably not
    time.sleep(0.001)

    print("started light service...")
    last_time_status_check_in = time.monotonic()

    if DEVICE_STATE['light_is_on']:
        turn_on_lights()
    else:
        turn_off_lights()

    while not exit_monitor.exit_now_flag_raised:
        # added time.sleep 1 ms after seeing 100% CPU usage
        # found this solution https://stackoverflow.com/a/41749754
        time.sleep(0.001)
        current_seconds_count = time.monotonic()

        if current_seconds_count - last_time_status_check_in > status_checkin_delay:
            last_time_status_check_in = current_seconds_count

            if DEVICE_STATE['light_is_on']:
                client.publish(MQTT_GETON_PATH, ON_VALUE)
            else:
                client.publish(MQTT_GETON_PATH, OFF_VALUE)

    client.loop_stop()
    client.disconnect()
    pixels.deinit()
    print("light service ended")
