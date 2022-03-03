# run this script, then disconnect the feather, remove the SD card, and insert
# the SD card into your computer. There should be a .txt file named "test.txt"
# that says "Hello world!" in it.

# needed for initializing SPI and CS line connections
import board
import busio
import digitalio
# import SD card and filesystem access modules
import adafruit_sdcard
import storage

# create SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# create chip selection (CS) line
cs = digitalio.DigitalInOut(board.D10)
# create microSD card object
sd_card = adafruit_sdcard.SDCard(spi, cs)
# create filesystem object
vfs = storage.VfsFat(sd_card)
# mount the microSD card filesystem into the CircuitPython file system
storage.mount(vfs, "/sd") # /sd/ now used as location for sd card files

with open("/sd/num_file.txt", "w") as file:
    file.write("1")

print("done!")
