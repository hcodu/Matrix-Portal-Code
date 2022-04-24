# Write your code here :-)
import time
import board
import displayio
import busio
import terminalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from adafruit_matrixportal.matrixportal import MatrixPortal


import adafruit_requests as requests




pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)


# 1: harry, 2: hieu, 3: luke
program = 1

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)

# matrixportal = MatrixPortal(
#     url="https://catfact.ninja/fact",
# )
# network = matrixportal.network

# Create a new label with the color and text selected
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(20,7),
    text_color=0x800000,
    scrolling=False,
)

matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(20,15),
    text_color='#00FF00',
    scrolling=False,

)

SCROLL_DELAY = 0.03

contents = [
    { 'text': 'THIS IS RED',  'color': '#cf2727'},

]

matrixportal.set_text('HARRY', 0)
#matrixportal.set_text('TEST', 1)


while True:
        button_up.update()
        if button_up.fell & (program < 3):
            if program < 3:
                program += 1
                if program == 2:
                    matrixportal.set_text('LUKE', 0)
                if program == 3:
                    matrixportal.set_text('RICECHIGGA420', 0)

        button_down.update()
        if button_down.fell:
            if program > 1:
                program -= 1
                if program == 1:
                    matrixportal.set_text('HARRY', 0)
                if program == 2:
                    matrixportal.set_text('LUKE', 0)
                if program == 3:
                    matrixportal.set_text('RICECHIGGA420', 0)





        # Set the text color
        ##matrixportal.set_text_color('#cf2727')

        # Scroll it
        matrixportal.scroll_text(SCROLL_DELAY)


