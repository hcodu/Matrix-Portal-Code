# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

from msilib.schema import Error
import time
import board
import displayio
import terminalio
import busio

import rtc

# import adafruit_oauth2 as OAUTH2


from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer

from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix

import adafruit_requests as requests
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager

import adafruit_esp32spi.adafruit_esp32spi_socket as socket

import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT




BLINK = False
DEBUG = False
CLOCK_ON = True

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print("    Metro Minimal Clock")
print("Time will be set for {}".format(secrets["timezone"]))

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

#status_light = board.NEOPIXEL()

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

requests.set_socket(socket, esp)


# --- Display setup ---
matrix = Matrix()
display = matrix.display

# --- Button setup ---
# pin_down = DigitalInOut(board.BUTTON_DOWN)
# pin_down.switch_to_input(pull=Pull.UP)
# button_down = Debouncer(pin_down)
# pin_up = DigitalInOut(board.BUTTON_UP)
# pin_up.switch_to_input(pull=Pull.UP)
# button_up = Debouncer(pin_up)

# --- Drawing setup ---
group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0x6A0DAD  # BLUE
color[2] = 0x6A0DAD  # BLUE
color[3] = 0x6A0DAD  # BLUE
           
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print("Connected to Adafruit IO!  Listening for DemoFeed changes...")

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))
# pylint: disable=unused-argument
def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")
# pylint: disable=unused-argument
def on_message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    global CLOCK_ON

    if feed_id == "welcome-feed":
        if payload[0:4] == 'True':
            CLOCK_ON = True
        if payload[0:5] == "False":
            CLOCK_ON = False
    elif feed_id == "color-feed":
        payload = "0x" + payload[1:7]

        hex_int = int(payload, 16)
        color[1] = hex_int


    print("Feed {0} received new value: {1}".format(feed_id, payload))

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.show(group)

if not DEBUG:
    font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
else:
    font = terminalio.FONT

clock_label = Label(font)

def update_time(*, hours=None, minutes=None, show_colon=False):
    now = time.localtime()  # Get the time values we need
    if hours is None:
        hours = now[3]
    if hours >= 18 or hours < 6:  # evening hours to morning
        if CLOCK_ON:
            clock_label.color = color[1]
        else:
            clock_label.color = color[0]
    else:
        if CLOCK_ON:
            clock_label.color = color[1]
        else:
            clock_label.color = color[0] # daylight hours
    if hours > 12:  # Handle times later than 12:59
        hours -= 12
    elif not hours:  # Handle times between 0:00 and 0:59
        hours = 12

    if minutes is None:
        minutes = now[4]

    if BLINK:
        colon = ":" if show_colon or now[5] % 2 else " "
    else:
        colon = ":"

    clock_label.text = "{hours}{colon}{minutes:02d}".format(
        hours=hours, minutes=minutes, colon=colon
    )
    
    bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # Center the label
    clock_label.x = round(display.width / 2 - bbwidth / 2)
    clock_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
        print("Label x: {} y: {}".format(clock_label.x, clock_label.y))


last_check = None
update_time(show_colon=True)  # Display whatever time is on the board
group.append(clock_label)  # add the clock label to the group

wifi.connect()
MQTT.set_socket(socket, esp)

mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
)

io = IO_MQTT(mqtt_client)

io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_message = on_message

io.connect()

io.subscribe("welcome-feed")
io.subscribe("color-feed")

r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

current_time = r.datetime
print(current_time) 

current_UTC = ""

while True:

    try:
        io.loop()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        io.reconnect()
        continue

    # current_time = r.datetime
    # print(current_time)
    # print(time.localtime())




    if last_check is None or time.monotonic() > last_check + 60:
        try:
            response = requests.get("https://www.timeapi.io/api/TimeZone/zone?timeZone=America/New_York")
            current_UTC = response.json()["currentLocalTime"]
        except Error as e:
            print("Some error occured, retrying! -", e)


        current_hour = int(current_UTC[11:13])
        current_minute = int(current_UTC[14:16])

        try:
            update_time(
                show_colon=True,
                hours = current_hour,
                minutes = current_minute

            )  # Make sure a colon is displayed while updating


            print("Current Time: " + str(current_hour) + " : " + str(current_minute))


            #network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    update_time(    
        hours = current_hour,
        minutes = current_minute
    )
    time.sleep(1)
