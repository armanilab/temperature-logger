from digitalio import DigitalInOut, Direction
import time

# imports for OLED board
import board
import displayio
import terminalio
# display library
from adafruit_display_text import label
import adafruit_displayio_sh1107

# setup display
displayio.release_displays() # reset displays that may have already been attached
i2c = board.I2C() # setup I2C
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C) # default address
print("I2C successful")

# display parameters: SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2
display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=0
)
print("display setup successful")

recording_label = label.Label(terminalio.FONT, text="*REC",
    anchor_point = (1.0, 1.0), anchored_position = (128, 64))
display.show(recording_label)

while True:
    pass
