import time
import board
from digitalio import DigitalInOut, Direction, Pull

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

button_b = DigitalInOut(board.D6)
button_b.direction = Direction.INPUT
button_b.pull=Pull.UP

while True:
    if button_b.value:
        led.value = False
    else:
        led.value = True

    time.sleep(0.01) # debounce delay
