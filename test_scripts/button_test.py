import time
import board
from digitalio import DigitalInOut, Direction, Pull

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

a = DigitalInOut(board.D9)
a.direction = Direction.INPUT
a.pull = Pull.UP

b = DigitalInOut(board.D6)
b.direction = Direction.INPUT
b.pull=Pull.UP

c = DigitalInOut (board.D5)
c.direction = Direction.INPUT
c.pull = Pull.UP

debounce_time = 0.2
last_button_press = 0.0
button_counter = 0

def press_button(button):
    led.value = not led.value # switch LED on/off
    print(button + str(button_counter))
    last_button_press = time.time()
    button_counter += 1

while True:
    if not a.value and time.time() - last_button_press > debounce_time:
        press_button('a')
    if not b.value and time.time() - last_button_press > debounce_time:
        press_button('b')
    if not c.value and time.time() - last_button_press > debounce_time:
        press_button('c')
