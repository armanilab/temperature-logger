# Temperature logger
# written by Lexie Scholtz
# last updated: 03.01.2022

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
MEASUREMENT_INTERVAL = 10

# --- SETUP ------------------------------------------------------------------
NS_TO_SEC = 1e-9 # conversion for times from ns to s

# setup temperature sensor
temp_sensor = analogio.AnalogIn(board.A5)

# setup LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

# setup buttons
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

# display parameters: SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2
display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=0
)

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
# texts to be used in display
clear_text =            "                     "
title_text =            "Temperature Logger   "
next_test_text =        "Next test: #"
ready_text =            "         Ready to go!"
pretest_button_text =   "[A] START   [C] MEAS "
test_button_text =      "[B] END     [C] MEAS "
test_header_text =      "#               "
rec_text =              "**REC"
time_text =             "Time:                "
temp_text =             "Temp:                "
end_test_text =         "Test ended: "
total_time =            "Total time: "
single_meas_text =      "Temp:                "
error_text =            "ERROR:               "
file_error_text =       "Write to file failed."

# screen for use when tests are not in progress
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
test_title_label = label.Label(terminalio.FONT, text = test_header_text,
    x = 0, y = 6)
rec_label = label.Label(terminalio.FONT, text = rec_text,
    anchor_point = (1.0, 0.5), anchored_position = (128, 6))
time_label = label.Label(terminalio.FONT,
    text = time_text, x = 0, y = 18)
temp_label = label.Label(terminalio.FONT, scale = 2,
    text = temp_text, x = 0, y = 36)
buttons_label = label.Label(terminalio.FONT, text = test_button_text,
    anchor_point = (0.0, 1.0), anchored_position = (0, 64))
test_group.append(test_title_label)
test_group.append(rec_label)
test_group.append(time_label)
test_group.append(temp_label)
test_group.append(buttons_label)

# error screen
error_group = displayio.Group()
error_label = label.Label(terminalio.FONT, text = error_text, scale = 2,
    x = 0, y = 8)
error_msg_label1 = label.Label(terminalio.FONT, text = clear_text, x = 0,
    y = 30)
error_msg_label2 = label.Label(terminalio.FONT, text = clear_text, x = 0,
    y = 44)
error_group.append(error_label)
error_group.append(error_msg_label1)
error_group.append(error_msg_label2)

# --- DEFINE HELPER FUNCTIONS ------------------------------------------------

# take a temperature measurement, based on Adafruit's equations for their
# AD8495 thermocouple amplifier
def measure_temp():
    # convert thermocouple raw data into voltage
    voltage = (temp_sensor.value * 3.3) / 65536
    # convert to temperature in deg C
    return (voltage - 1.25) / 0.005

# reads the new test number from the specified file
def get_test_num():
    try:
        with open("/sd/num_file.txt", "r") as num_file:
            num_file = int(num_file.readline())
    except OSError:
        print("Error getting test number - file error")
        return 0
    return num_file

# updates the file that contains the test number with a new value
def update_test_num(new_test_num):
    try:
        with open("/sd/num_file.txt", "w") as num_file:
            num_file.write(str(new_test_num))
    except OSError:
        print("Error writing new test number - file error")

# updates the display to indicate that a file recording error has occurred
# file recording errors make this program useless, so putting the logger
# into an endless loop to blink the LED is fine - the user will need
# to reset the file writing system anyways
def throw_fatal_file_error(test_num):
    error_msg_label1.text = file_error_text
    error_msg_label2.text = "File: test{n}.txt".format(n = test_num)
    display.show(error_group)

    while True:
        led.value = True
        time.sleep(1)
        led.value = False
        time.sleep(1)

# --- START PROGRAM ----------------------------------------------------------
# display the initial logger screen, updated to the current test number
test_num = get_test_num()
line2.text = next_test_text + str(test_num)
display.show(non_test_group)

while True:
    # update the current time variable
    current_time = time.monotonic_ns() * NS_TO_SEC

    # check for inputs
    if (not button_a.value and current_time - last_a_press >= DEBOUNCE_TIME):
        a_pressed = True
        last_a_press = current_time
    if (not button_b.value and current_time - last_b_press >= DEBOUNCE_TIME):
        b_pressed = True
        last_b_press = current_time
    if (not button_c.value and current_time - last_c_press >= DEBOUNCE_TIME):
        c_pressed = True
        last_c_press = current_time

    if c_pressed: # take a single measurement - only display it, not logged
        # measure the temperature
        temperature = measure_temp()

        # display measured temperature
        line1.text = clear_text
        line2.text = clear_text
        big_line12.text = "Temp:{temp:.1f}".format(temp = temperature)
        display.show(non_test_group)

    if (a_pressed): # start logging now
        # determine the file name, based on the test number
        test_num = get_test_num()
        file_name = "/sd/test{n}.txt".format(n = test_num)

        # update the display with test details
        test_title_label.text = "#" + str(test_num)
        display.show(test_group)
        led.value = True # turn LED on to indicate test is occurring
        print("logging starting...")

        # actually start logging
        try:
            with open(file_name, "w") as file: # CHANGE BACK TO "W"
                # initialize file with headers
                file.write("Time(s)\tTemp(deg C)\n")

                # define test start time
                time_elapsed = 0
                test_start = time.monotonic_ns() * NS_TO_SEC # in nanoseconds
                last_measurement = test_start - MEASUREMENT_INTERVAL

                while True:
                    # update the time variables
                    current_time = time.monotonic_ns() * NS_TO_SEC
                    time_elapsed = current_time - test_start

                    # check for inputs - note that A doesn't do anything during
                    # the test, so we can ignore it
                    if (not button_b.value
                        and current_time - last_b_press >= DEBOUNCE_TIME):
                        b_pressed = True
                        last_b_press = current_time
                    if (not button_c.value
                        and current_time - last_c_press >= DEBOUNCE_TIME):
                        c_pressed = True
                        last_c_press = current_time

                    # ONLY log measurements at the measurement interval or if
                    # triggered as a single measurement by the C button
                    if (c_pressed or
                        current_time - last_measurement >= MEASUREMENT_INTERVAL):
                        # take the measurement
                        temperature = measure_temp() # FIX with analog reading + conversion

                        # write the time and temp to a text file
                        time_str = "{t:.4f}".format(t = time_elapsed)
                        temp_str = "{temp:.6f}".format(temp = temperature)
                        file.write(time_str + "\t" + temp_str + "\n")

                        # print time and temperature to the display
                        temp_label.text = "Temp:{temp:.1f}".format(temp = temperature)
                        time_label.text = "Time:{t:.2f}".format(t = time_elapsed)
                        display.show(test_group)

                        # if the measurement was triggered by the C button as an
                        # individual measurement, do not reset the time counter.
                        # We want all measurements to occur as regularly as
                        # possible on the specified time interval
                        if not c_pressed:
                            last_measurement = current_time

                    # check for button press -> if so, end test
                    if (b_pressed):
                        file.flush() # make sure everything is written to file
                        b_pressed = False
                        break

                    # reset input variables
                    b_pressed = False
                    c_pressed = False

        except OSError: # file recording error
            throw_fatal_file_error(test_num)

        # reset system for next test
        led.value = False # turn LED off
        # update the screen to give details of last completed test
        line1.text = end_test_text + "#" + str(test_num)
        line2.text = "Total time: {t}".format(t = int(time_elapsed))
        update_test_num(test_num + 1) # update test number
        display.show(non_test_group)

    # reset input variables
    a_pressed = False
    b_pressed = False
    c_pressed = False
