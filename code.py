# This code allows us to use the display
import board
import displayio
from digitalio import DigitalInOut, Direction
import terminalio
import time

# display library
from adafruit_display_text import label
import adafruit_displayio_sh1107

# for led
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
print("led initiation successful")

# file saving code from LS malaria device - removed file saving to check time
test_start = time.time()

# use for screen I2C
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
print("I2C successful")

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2
display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=0
)
print("display dimensions successful")

# make the display context
splash = displayio.Group()
display.show(splash)
print("display context successful")

text2 = "disp_success"
text_area2 = label.Label(
    terminalio.FONT, text=text2, scale=1, color=0xFFFFFF, x=9, y=44
)
display.show(text_area2)

time.sleep(2)
while True:
    temperature = 1
    rxntime = "%.3f" % (time.time() - test_start)
    print('Time: %s(s) Temp(C): %f Voltage(V): %f' % (rxntime, temperature, temperature))
    # draw temperature on screen
    temptext_area = label.Label(terminalio.FONT, text=rxntime, color=0xFFFFFF,
    x=8, y=8)
    # the append needs to be changed - right now it overwrites in same area
    display.show(temptext_area)

    # sleepy time
    led.value = True
    time.sleep(1)
    led.value = False
    time.sleep(2)
