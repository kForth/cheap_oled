#!/usr/bin/env python

import pigpio
from PIL import ImageDraw, Image
from cheap_oled.device import OLED_SSD1306, OLED_SH1106
from cheap_oled.render import OLED_Canvas

pi = pigpio.pi()

if not pi.connected:
    exit()

device = OLED_SSD1306(pi, port=1, address=0x3C)

with OLED_Canvas(device) as draw:
    logo = Image.open('examples/images/pi_logo.png')
    draw.bitmap((32, 0), logo, fill=1)

device.close()

pi.stop()