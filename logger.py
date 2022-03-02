#TODO: how to name files? just numbering them? rtc doesn't work like on RPi
# and we didn't put a battery in the logger.
# TODO: measurements aren't appearing during the test

import time
import board
# imports for OLED board & display library
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1107
# imports for I/O
from digitalio import DigitalInOut, Direction, Pull
import analogio
# needed for SD card logging
import digitalio
import busio
import adafruit_sdcard
import storage

# --- TESTING PARAMETERS -----------------------------------------------------
# seconds between measurements
MEASUREMENT_INTERVAL = 2

# --- SETUP ------------------------------------------------------------------
NS_TO_SEC = 1e-9 # conversion for times from ns to s

# setup temperature sensor
temp_sensor = analogio.AnalogIn(board.A5)

# setup LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

# setup button
button_a = DigitalInOut(board.D9) # start test
button_a.direction = Direction.INPUT
button_a.pull = Pull.UP
button_b = DigitalInOut(board.D6) # end test
button_b.direction = Direction.INPUT
button_b.pull = Pull.UP
button_c = DigitalInOut (board.D5) # take measurement
button_c.direction = Direction.INPUT
button_c.pull = Pull.UP

a_pressed = False
b_pressed = False
c_pressed = False
last_a_press = 0
last_b_press = 0
last_c_press = 0
DEBOUNCE_TIME = 0.1

# setup display
displayio.release_displays() # reset displays that may have been attached
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

# setup SD card
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# create chip selection (CS) line
cs = digitalio.DigitalInOut(board.D10)
# create microSD card object
sd_card = adafruit_sdcard.SDCard(spi, cs)
# create filesystem object
vfs = storage.VfsFat(sd_card)
# mount the microSD card filesystem into the CircuitPython file system
storage.mount(vfs, "/sd") # /sd/ now used as location for sd card files

# --- DEFINE DISPLAY SCREENS -------------------------------------------------
# initialization screen
clear_text =            "                     "
title_text =            "Temperature Logger   "
next_test_text =        "Next test: #"
ready_text =            "         Ready to go!"
pretest_button_text =   "[A] START   [C] MEAS "
test_button_text =      "[B] END [C] MEAS *REC"
time_text =             "Time:                "
temp_text =             "Temp:                "
end_test_text =         "Test ended: "
total_time =            "Total time: "
single_meas_text =      "Temp:                "

non_test_group = displayio.Group()
line1 = label.Label(terminalio.FONT, text = title_text, x = 0,
    y = 8)
line2 = label.Label(terminalio.FONT, text = clear_text, x = 0, y = 24)
line3 = label.Label(terminalio.FONT, text = ready_text,
    anchor_point = (1.0, 0.5), anchored_position = (128, 40))
line4 = label.Label(terminalio.FONT, text = pretest_button_text,
    anchor_point = (0.0, 1.0), anchored_position = (0, 64))
big_line12 = label.Label(terminalio.FONT, text = clear_text, scale = 2,
    anchor_point = (0.0, 0.0), anchored_position = (0, 0))
non_test_group.append(line1)
non_test_group.append(line2)
non_test_group.append(line3)
non_test_group.append(line4)
non_test_group.append(big_line12)


# logging screen
test_group = displayio.Group()
time_label = label.Label(terminalio.FONT,
    text = time_text, x = 0, y = 8)
temp_label = label.Label(terminalio.FONT, scale = 2,
    text = temp_text, x = 0, y = 24)
buttons_label = label.Label(terminalio.FONT, text = test_button_text,
    anchor_point = (0.0, 1.0), anchored_position = (0, 64))
    # need to test this to see if this works, otherwise anchor_point
    # and anchored_position may need to be set afterwards
test_group.append(time_label)
test_group.append(temp_label)
test_group.append(buttons_label)

# end screen
# msg_label = label.Label(terminalio.FONT, text = end_test_text,
#     x = 0, y = 8)
# length_label = label.Label(terminalio.FONT, text = total_time_text,
#     x = 0, y = 24)
# ready_label = label.Label(terminalio.FONT, text = ready_text, x = 0, y = 40)
# button_label = label.Label(terminalio.FONT, text = pretest_button_text,
#     anchor_point = (0.0, 1.0), anchored_position = (0, 64))
# final_group = displayio.Group()
# final_group.append(msg_label)
# final_group.append(length_label)
# final_group.append(ready_label)
# final_group.append(button_label)

def measure_temp(): # TODO: check if we need to pass in the pin as an argument
    # read analog input pin and convert it using equations given by Adafruit
    # convert thermocouple raw data into voltage
    voltage = (temp_sensor.value * 3.3) / 65536
    return (voltage - 1.25) / 0.005 # convert to temperature in C

def get_test_num():
    try:
        with open("/sd/num_file.txt", "r") as num_file:
            return int(num_file.readline())
    except:
        print("error getting test number")
        return 0

def update_test_num(new_test_num):
    try:
        with open("/sd/num_file.txt", "w") as num_file:
            num_file.write(new_test_num)
    except:
        print("error writing new test number")

# --- START PROGRAM ----------------------------------------------------------
#TODO: get next test_num and replace it in the text string next_test_text
test_num = get_test_num()
line2.text = next_test_text + str(test_num)

display.show(non_test_group)

while True:
    # check for inputs
    if not button_a.value and time.time() - last_a_press > DEBOUNCE_TIME:
        a_pressed = True
        last_a_press = time.time()
    if not button_b.value and time.time() - last_b_press > DEBOUNCE_TIME:
        b_pressed = True
        last_b_press = time.time()
    if not button_c.value and time.time() - last_c_press > DEBOUNCE_TIME:
        c_pressed = True
        last_c_press = time.time()

    if c_pressed:
        # take a single measurement - only display it on the screen
        print("c button pressed")
        temperature = measure_temp()
        # TODO: display measured temperature
        line1.text = clear_text
        line2.text = clear_text
        big_line12.text = "Temp:{temp:.1f}".format(temp = temperature)
        display.show(non_test_group)


    if (a_pressed): # start logging now
        print("a button pressed")

        test_num = get_test_num()

        file_name = "/sd/test{n}.txt".format(n = test_num)
        display.show(test_group)
        led.value = True
        print("logging starting...")

        # actually start logging
        with open(file_name, "w") as file:
            # initialize file with headers
            file.write("Time(s)\tTemp(deg C)\n")

            # define test start time
            time_elapsed = 0
            test_start = time.monotonic_ns() * NS_TO_SEC # in nanoseconds
            last_measurement = test_start - MEASUREMENT_INTERVAL

            while True:
                # check for inputs
                #a_pressed = not button_a.value # don't actually care about a button
                if not button_b.value and time.monotonic_ns() * NS_TO_SEC - last_b_press > DEBOUNCE_TIME:
                    b_pressed = True
                    last_b_press = time.monotonic_ns() * NS_TO_SEC
                    print("b_pressed - in logging")
                if not button_c.value and time.monotonic_ns() * NS_TO_SEC - last_c_press > DEBOUNCE_TIME:
                    c_pressed = True
                    last_c_press = time.monotonic_ns() * NS_TO_SEC
                    print("c_pressed - in logging")

                time_elapsed = time.monotonic_ns() * NS_TO_SEC - test_start
                # ONLY log measurements at the measurement interval
                if time_elapsed - last_measurement >= MEASUREMENT_INTERVAL or c_pressed:
                    # TODO: take measurement
                    temperature = measure_temp() # FIX with analog reading + conversion

                    # TODO: log time and temperature
                    # format the time
                    time_str = "{t:.4f}".format(t = time_elapsed)
                    temp_str = "{temp:.6f}".format(temp = temperature)
                    file.write(time_str + "\t" + temp_str + "\n")

                    # TODO: print time and temperature to the display
                    temp_label.text = "Temp:{temp:.1f}".format(temp = temperature)
                    time_label.text = "Time:{t:.2f}".format(t = time_elapsed)
                    display.show(test_group)

                    if not c_pressed:
                        last_measurement = time_elapsed

                # check for button press -> if so, end test
                if (b_pressed):
                    print("end test")
                    file.flush()
                    break
                # reset buttons
                b_pressed = False
                c_pressed = False

        # reset system
        led.value = False
        line1.text = end_test_text + "#" + str(test_num)
        line2.text = "Total time: {t}".format(int(t = time_elapsed))
        update_test_num(test_num + 1) # update test number
        display.show(final_group)
    a_pressed = False
    b_pressed = False
    c_pressed = False
# check for button presses ->
# if pressed & not already logging ->
    # start test
    # initialize text file w/ time + date (name of file)
    # add headers to top of file
    # log every t seconds
    # LED stays on while recording
    # on screen:
        # time elapsed
        # current temp
        # logging indicator

# else if pressed & logging ->
    # end test, save file
    # print saved file

# IF ERROR: screen prints AND LED blinks
