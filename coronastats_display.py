import time
import requests
from lxml import html
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

totalCasesPrevious = 0
totalDeathsPrevious = 0
UScasesPrevious = 0
USopenTests = 0
	
# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE,
                     width=240, height=240, x_offset=0, y_offset=80)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.height   # we swap height/width to rotate it to landscape!
width = disp.width
image = Image.new('RGB', (width, height))
rotation = 270

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    response = requests.get("https://www.worldometers.info/coronavirus/")
    response2 = requests.get("https://www.cdc.gov/coronavirus/2019-ncov/cases-in-us.html")
    
    byte_data = response.content
    byte_data2 = response2.content
    
    source_code = html.fromstring(byte_data) 
    source_code2 = html.fromstring(byte_data2) 
    
    totalCases = source_code.xpath('//*[@id="maincounter-wrap"]/div/span')
    totalDeaths = source_code.xpath('//*[@id="maincounter-wrap"][2]/div/span')
    UScases = source_code2.xpath('/html/body/div[6]/main/div[3]/div/div[3]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td')
    USopenTests = source_code2.xpath('/html/body/div[6]/main/div[3]/div/div[3]/div[1]/div/div/div/div[2]/table/tbody/tr[3]/td')

    TCdiff = str(totalCases - totalCasesPrevious)
    TDdiff = str(totalDeaths - totalDeathsPrevious)
    USCdiff = str(UScases - UScasesPrevious)
    USOdiff = str(USopenTests - USopenTestsPrevious)
	
    update_time = time.localtime()
    t = time.asctime(update_time)
	
    y = top+5
    draw.text((x, y), "CORONAVIRUS", font=font, fill="#FFFFFF")
    y += font.getsize("CORONAVIRUS")[1]
    draw.text((x, y), "TRACKER", font=font, fill="#FFFFFF")
    y += font.getsize("TRACKER")[1] + 10
    draw.text((x, y), "Total: "+totalCases[0].text_content()+" ("+TCdiff+")", font=font, fill="#FFFF00")
    y += font.getsize(totalCases[0].text_content())[1]
    draw.text((x, y), "Dead: "+totalDeaths[0].text_content()+" ("+TDdiff+")", font=font, fill="#FF0000")
    y += font.getsize(totalDeaths[0].text_content())[1]
    draw.text((x, y), "US Cases: "+UScases[0].text_content()+" ("+USCdiff+")", font=font, fill="#FFa500")
    y += font.getsize(UScases[0].text_content())[1]
    draw.text((x, y), "US Open Tests: "+USopenTests[0].text_content()+" ("+USOdiff+")", font=font, fill="#00FF00")
    y += font.getsize(USopenTests[0].text_content())[1] + 10
    draw.text((x, y), "LAST UPDATED:", font=font, fill="#FFFFFF")
    y += font.getsize("LAST UPDATED:")[1]
    draw.text((x, y), t[:-4], font=font, fill="#FFFFFF")
    # Display image.
    disp.image(image, rotation)
	
    totalCasesPrevious = totalCases
    totalDeathsPrevious = totalDeaths
    UScasesPrevious = UScases
    USopenTestsPrevious = USopenTests
    
    time.sleep(300)
