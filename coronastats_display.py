# -*- coding: utf-8 -*-

import time
import requests
from lxml import html
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789


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
rotation = 180

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
    byte_data = response.content 
    source_code = html.fromstring(byte_data) 
    tree = source_code.xpath('//*[@id="maincounter-wrap"]/div/span')
    tree2 = source_code.xpath('//*[@id="maincounter-wrap"][2]/div/span')
    response2 = requests.get("https://www.cdc.gov/coronavirus/2019-ncov/cases-in-us.html")
    byte_data2 = response2.content 
    source_code2 = html.fromstring(byte_data2) 
    tree3 = source_code2.xpath('/html/body/div[6]/main/div[3]/div/div[3]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td')
    tree4 = source_code2.xpath('/html/body/div[6]/main/div[3]/div/div[3]/div[1]/div/div/div/div[2]/table/tbody/tr[3]/td')
    update_time = time.localtime()
    t = time.asctime(update_time)
    # Write four lines of text.
    y = top+5
    draw.text((x, y), "CORONAVIRUS", font=font, fill="#FFFFFF")
    y += font.getsize("CORONAVIRUS")[1]
    draw.text((x, y), "TRACKER", font=font, fill="#FFFFFF")
    y += font.getsize("TRACKER")[1] + 10
    draw.text((x, y), "Total: "+tree[0].text_content(), font=font, fill="#FFFF00")
    y += font.getsize(tree[0].text_content())[1]
    draw.text((x, y), "Dead: "+tree2[0].text_content(), font=font, fill="#FF0000")
    y += font.getsize(tree2[0].text_content())[1]
    draw.text((x, y), "US Cases: "+tree3[0].text_content(), font=font, fill="#FFa500")
    y += font.getsize(tree3[0].text_content())[1]
    draw.text((x, y), "US Open Tests: "+tree4[0].text_content(), font=font, fill="#00FF00")
    y += font.getsize(tree4[0].text_content())[1] + 10
    draw.text((x, y), "LAST UPDATED:", font=font, fill="#FFFFFF")
    y += font.getsize("LAST UPDATED:")[1]
    draw.text((x, y), t[:-4], font=font, fill="#FFFFFF")
    # Display image.
    disp.image(image, rotation)
    time.sleep(5)
