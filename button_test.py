import time
import board
from digitalio import DigitalInOut, Direction, Pull

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

button_b = DigitalInOut(board.D6)
button_b.direction = Direction.INPUT
button_b.pull=Pull.UP

debounce_time = 0.2
last_button_press = 0.0
button_counter = 0
while True:
    if not button_b.value and time.time() - last_button_press > debounce_time:
        led.value = not led.value
        print(button_counter)
        last_button_press = time.time()
        button_counter += 1
