# Temperature logger

## Components
- *Adafruit Feather M4 Express ([Adafruit #3857](https://www.adafruit.com/product/3857), $22.95)
- *Adafruit Featherwing 128x64 OLED ([Adafruit #4650](https://www.adafruit.com/product/4650), $14.95)
- *Adafruit Adalogger Featherwing ([Adafruit #2922](https://www.adafruit.com/product/2922), $8.95)
- *Adafruit Analog Amplifier for K-Type Thermocouple AD8495 Breakout ([Adafruit #1778](https://www.adafruit.com/product/1778), $11.95)
- K-type Temperature Probe (We used [Temprel #T21MU3KCl](https://www.digikey.com/en/products/detail/temprel/T21MU3KCI/13277973) but any other K-type probe would work)
- MicroSD card (We used 16 GB but smaller capacities would also be fine since it will just hold text files with data)
- Stacking headers ([Adafruit #2830](https://www.adafruit.com/product/2830))
- Female headers ([Adafruit #2940](https://www.adafruit.com/product/2940))
- Male headers ([Adafruit #3002](https://www.adafruit.com/product/3002))
- Wire
- 5V USB Power source
- Micro B USB cable

Total cost for major electronic components (*): $58.80

*Prices based on ordering directly from Adafruit in March 2022*

**Equipment needed for assembly and setup:**
- Wire strippers
- Soldering iron and solder
- Laptop
- Micro SD card reader

## Hardware assembly
1. Solder the stacking headers onto the Feather M4 Express such that the long pins go down through the top of the board and the female ends of the pins are on top of the board.

2. Solder the female headers onto the Featherwing 128x64 OLED.

3. Solder a screw terminal onto the end of the AD895 Analog Amplifier.

4. Solder wires from the Feather M4 Express to the AD8495 Analog Amplifier:
     - 3.3V -> Vcc
     - GND -> GND
     - A5 -> Vout

5. Plug the Featherwing 128x64 OLED into the female headers on top of the Feather M4 Express.

6. Either solder the Adalogger Featherwing directly to the male ends of the headers on the bottom of the Feather M4 Express or solder female headers onto the Adalogger Featherwing (facing up) and plug those into the bottom of the stacking headers of the Feather M4 Express.

7. Wrap wire around the positive and negative leads of the T21MU3KCl K-type temperature probe and solder them together. Connect the other ends of these wires to the screw terminal on the AD895 Analog Amplifier.

Congrats! Your hardware is fully assembled.

## Software Prep
1. Download the official SD card formatter:
2. Insert the microSD card into your computer.
3. Open the SD card formatter and select “Overwrite” to format the SD card and prepare it for use in the temperature logger. Click “Ok.” This process will take a few minutes, depending on how big the SD card you use is.
4. Remove the SD card from your computer and put it into Adalogger.
5. Download the `device_files.zip` from the Github. Unzip the file.
6. Connect the Feather M4 Express to your computer via a micro B USB cable. It should show up as a `CIRCUIT_PYTHON` device. Copy the contents of the `device_files.zip` onto it.
7. Disconnect the Feather M4 Express assembly from your computer and connect it to your 5V power source of choice (outlet, USB battery pack, etc.) via the micro B USB cable.

Your temperature logger is now up and running!

**Note:** if you need to make any modifications to the program (for example, the measurement interval or the pin that the temperature sensor is connected to), we prefer the Mu Editor for ease of updating the code on the Feather.

## Program Description
When triggered via a button press, the temperature logger measures and records the temperature of the K-type probe with time stamps to a datafile saved on the attached microSD card. By default, measurements will be taken every 10 seconds, but this can be modified by modifying the `MEASUREMENT_INTERVAL` constant in the `code.py` file. The screen will update every 1 second (but those temperatures will not be recorded), but this can be modified via the `UPDATE_INTERVAL` constant in the `code.py` file.

### User interface:
- A button – starts a new logging session
- B button - ends a logging session
- C button - takes a single temperature measurement.
     - If a logging session has been started, this temperature will also be logged to the data file, but will not interrupt the regular measurement intervals.
     - If a logging session was not already started, this value will not be written to a datafile and will only be displayed on the screen.
- Red on-board LED – turns on to indicate that a logging session is active. It will also blink if there is a file access error, which will require troubleshooting before the logger can be used again.

### Output files:
All data files are saved to the microSD card inserted into the Adalogger under the file name: `test#.txt` where # is the number of the test. These will start at 1 and count up with each consecutive test, unless the logger is reset by running the `“logging_test.py` script on the Feather to reset the logging at test 1. If the system is fully reinitialized, then any data files on the SD card will be overwritten as additional tests are completed with the same numbering. Note that on the microSD card, there is also a file called `num_file.txt` that is used to store the test number. `logging_test.py` resets the file to contain:
```
1
```
which restarts the numbering.

The files contain a single header line:
```
Time(s)	Temp(C) Press
```
followed by three tab-separated columns of data that represent (1) the time in seconds, (2) the temperature in degrees Celsius, and (3) the type of measurement. The type of measurement is given as 0 if it was an automatically logged measurement (based on the time interval), or a whole number counting up from 0 if the measurement was triggered by a button press. This functionality will allow the user to track the times and temperature of key time points (such as when a reaction starts, when reagents are added, when heat is applied, etc.). The files can easily be opened in Excel and the data separated into columns by using tab or whitespace as a deliminator.

## Test Scripts
- `button_test.py` - can be used to confirm that the Featherwing is properly connected to the Feather. Pressing any of the buttons will turn the LED on or off. The program will also count the number of button presses. Each time a button is pressed, the program prints out the button name and the counter to the Serial monitor.
- `screen_test.py` - can be used to confirm that the OLED screen on the Featherwing is working properly. Prints a small recording symbol to the screen.
- `logging_test.py` - can be used to confirm that the Adalogger and microSD card are working properly. Writes a text file called `num_file.txt` containing `1` to the microSD card. This also resets the numbering of the logging sessions.
