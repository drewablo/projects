import time
import requests
import re
from lxml import html
import digitalio
import board
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

totalCasesPrevious = 0
totalDeathsPrevious = 0
UScasesPrevious = 0
USopenTestsPrevious = 0

totalCaseChange = 0
totalDeathChange = 0
UScasesChange = 0 
USopenChange = 0	

previousSymbol = 0

switcher = Button(23)

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

def symbolUpdate(caseChange):
	global previousSymbol
	if caseChange != 0:
		if caseChange > 0:
			previousSymbol = "\u25b2"
		elif caseChange < 0:
			previousSymbol = "\u25BE"
	else:
		previousSymbol = previousSymbol
	return previousSymbol
	
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

    totalCasesReturn = totalCases[0].text_content()
    totalDeathsReturn = totalDeaths[0].text_content()
    UScasesReturn = UScases[0].text_content()
    USopenTestsReturn = USopenTests[0].text_content()
	
	
    totalCaseChange = int(re.findall("\d+",totalCasesReturn)[0]) - totalCasesPrevious
    totalDeathChange = int(re.findall("\d+",totalDeathsReturn)[0]) - totalDeathsPrevious
    UScasesChange = int(re.findall("\d+",UScasesReturn)[0]) - UScasesPrevious
    USopenChange = int(re.findall("\d+",USopenTestsReturn)[0]) - USopenTestsPrevious
	
    update_time = time.localtime()
    t = time.asctime(update_time)
	
	if totalCaseChange != 0 or totalDeathChange != 0 or UScasesChange !=0 or USopenChange !=0:
		y = top+5
		draw.text((x, y), "CORONAVIRUS", font=font, fill="#FFFFFF")
		y += font.getsize("CORONAVIRUS")[1] + 10
		draw.text((x, y), "Total: " + totalCasesReturn + " " + symbolUpdate(totalCaseChange), font=font, fill="#FFFF00")
		y += font.getsize(totalCasesReturn)[1]
		draw.text((x, y), "Dead: " + totalDeathsReturn + " " + symbolUpdate(totalDeathChange), font=font, fill="#FF0000")
		y += font.getsize(totalDeathsReturn)[1]
		draw.text((x, y), "US Cases: " + UScasesReturn + " " + symbolUpdate(UScasesChange), font=font, fill="#FFa500")
		y += font.getsize(UScasesReturn)[1]
		draw.text((x, y), "US Open Tests: " + USopenTestsReturn + symbolUpdate(USopenChange), font=font, fill="#00FF00")
		y += font.getsize(USopenTestsReturn)[1] + 10
		draw.text((x, y), "LAST CHANGE:", font=font, fill="#FFFFFF")
		y += font.getsize("LAST CHANGE:")[1]
		draw.text((x, y), t[:-4], font=font, fill="#FFFFFF")
		# Display image.
		disp.image(image, rotation)
	
    totalCasesPrevious = int(re.findall("\d+",totalCasesReturn)[0])
    totalDeathsPrevious = int(re.findall("\d+",totalDeathsReturn)[0])
    UScasesPrevious = int(re.findall("\d+",UScasesReturn)[0])
    USopenTestsPrevious = int(re.findall("\d+",USopenTestsReturn)[0])
    
    time.sleep(300)
