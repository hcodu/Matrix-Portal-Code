# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import busio
import terminalio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi

from adafruit_debouncer import Debouncer
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_portalbase import PortalBase
from adafruit_matrixportal.graphics import Graphics
from adafruit_matrixportal.network import Network
# import adafruit_portalbase.wifi_esp32s2.WiFi as WiFi 

# from adafruit_matrixportal.network import Network

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("ESP32 SPI webclient test")

# TEXT_URL = "https://fortnite-api.com/v2/stats/br/v2?name=swerve_forkknife"
TEXT_URL = "https://catfact.ninja/fact"
JSON_URL = "http://api.coindesk.com/v1/bpi/currentprice/USD.json"

matrixportal = MatrixPortal()

portalbase = PortalBase(
    network = matrixportal.network,
    graphics = matrixportal.graphics,
    url = TEXT_URL,
    # headers = {'Authorization': 'a937a56f-ec6d-4987-8adc-19ddc7338938'}

)


portalbase.add_text(
    text_font=terminalio.FONT,
    text_position=(5,7),
    text_color=0x804000,
    text_scale = 2,
    text = 'test',
)


value = portalbase.fetch()
print(value)


while True:
    
    continue


