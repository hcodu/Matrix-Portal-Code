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

import adafruit_imageload

from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix


# import adafruit_requests as requests
# import adafruit_esp32spi.adafruit_esp32spi_socket as socket

BLINK = True
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

# esp32_cs = DigitalInOut(board.ESP_CS)
# esp32_ready = DigitalInOut(board.ESP_BUSY)
# esp32_reset = DigitalInOut(board.ESP_RESET)

# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
# esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

# requests.set_socket(socket, esp)




# --- Display setup ---
matrix = Matrix(
    # esp = esp
)
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# --- Bitmap setup ---
group = displayio.Group()  # Create a Group
bitmap, palette = adafruit_imageload.load(
    'test1.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)

tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.show(group)







# r = requests.get('http://wifitest.adafruit.com/testwifi/index.html')
# print(r)


pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)





