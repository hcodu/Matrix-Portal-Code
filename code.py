# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

import time
import board
import displayio
import terminalio

from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer

from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix


import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

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

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)





# --- Button setup ---
pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)





# --- Drawing setup ---
group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0x6A0DAD  # BLUE
color[2] = 0x6A0DAD  # BLUE
color[3] = 0x6A0DAD # BLUE
           


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

while True:

    # print(network.get_local_time())
    clock_feed_response = network.fetch_data(
        url = 'https://io.adafruit.com/api/v2/hcodu/feeds/welcome-feed/data/retain', 
        headers = {'Access-Control-Request-Method' : 'GET'},
        timeout = 5
    )
    time.sleep(3)

    color_feed_response = network.fetch_data(
        url = 'https://io.adafruit.com/api/v2/hcodu/feeds/color-feed/data/retain', 
        headers = {'Access-Control-Request-Method' : 'GET'},
        timeout = 5
    )

    color_feed_response = "0x" + color_feed_response[1:7]
    
    hex_int = int(color_feed_response, 16)
    color[1] = hex_int

    if clock_feed_response[0:4] == 'True':
        CLOCK_ON = True
    if clock_feed_response[0:5] == "False":
        CLOCK_ON = False

    
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True
            )  # Make sure a colon is displayed while updating
            network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    update_time()
    time.sleep(1)
