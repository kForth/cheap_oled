# SSD1306 / SH1106 OLED Driver

Interfacing OLED matrix displays with the SSD1306 (or SH1106) driver in Python using
I2C on the Raspberry Pi. The particular kit I bought can be acquired for 
a few pounds from eBay: http://www.ebay.co.uk/itm/191279261331. Further 
technical details for the SSD1306 OLED display can be found in the 
[datasheet](https://raw.githubusercontent.com/kForth/cheap_oled/master/doc/tech-spec/SSD1306.pdf) [PDF]. 
See also the [datasheet](https://raw.githubusercontent.com/kForth/cheap_oled/sh1106-compat/doc/tech-spec/SH1106.pdf) [PDF] for the SH1106 chipset.

The SSD1306 display is 128x64 pixels, and the board is _tiny_, and will fit neatly
inside the RPi case (the SH1106 is slightly different, in that it supports 132x64
pixels). My intention is to solder wires directly to the underside
of the RPi GPIO pins so that the pins are still available for other purposes.

![Mounted Display](https://raw.githubusercontent.com/kForth/cheap_oled/master/doc/mounted_display.jpg)

## GPIO pin-outs

The SSD1306 device is an I2C device, so connecting to the RPi is very straightforward:

### P1 Header

For prototyping , the P1 header pins should be connected as follows:

| Board Pin | Name  | Remarks     | RPi Pin | RPi Function | Colour |
|----------:|:------|:------------|--------:|--------------|--------|
| 1         | GND   | Ground      | P01-6   | GND          | Black  |
| 2         | VCC   | +3.3V Power | P01-1   | 3V3          | White  |
| 3         | SCL   | Clock       | P01-5   | GPIO 3 (SCL) | Purple |
| 4         | SDA   | Data        | P01-3   | GPIO 2 (SDA) | Grey   |

![GPIO Pins](https://raw.githubusercontent.com/kForth/cheap_oled/master/doc/GPIOs.png)

[Attribution: http://elinux.org/Rpi_Low-level_peripherals]

### P5 Header

On rev.2 RPi's, right next to the male pins of the P1 header, there is a bare 
P5 header which features I2C channel 0, although this doesn't appear to be
initially enabled and may be configured for use with the Camera module. 

| Board Pin | Name  | Remarks     | RPi Pin | RPi Function  | Colour |
|----------:|:------|:------------|--------:|---------------|--------|
| 1         | GND   | Ground      | P5-07   | GND           | Black  |
| 2         | VCC   | +3.3V Power | P5-02   | 3V3           | White  |
| 3         | SCL   | Clock       | P5-04   | GPIO 29 (SCL) | Purple |
| 4         | SDA   | Data        | P5-03   | GPIO 28 (SDA) | Grey   |

![P5 Header](https://raw.githubusercontent.com/kForth/cheap_oled/master/doc/RPi_P5_header.png)

[Attribution: http://elinux.org/Rpi_Low-level_peripherals]

## Pre-requisites

This was tested with Raspian on a rev.2 model B, with a vanilla kernel version 3.12.28+. 
Ensure that the I2C kernel driver is enabled:
```bash
    $ dmesg | grep i2c
    [   19.310456] bcm2708_i2c_init_pinmode(1,2)
    [   19.323643] bcm2708_i2c_init_pinmode(1,3)
    [   19.333772] bcm2708_i2c bcm2708_i2c.1: BSC1 Controller at 0x20804000 (irq 79) (baudrate 100000)
    [   19.501285] i2c /dev entries driver
```
or
```bash
    $ lsmod | grep i2c
    i2c_dev                 5769  0 
    i2c_bcm2708             4943  0 
    regmap_i2c              1661  3 snd_soc_pcm512x,snd_soc_wm8804,snd_soc_core
```
If you dont see the I2C drivers, alter */etc/modules* and add the following 
two lines:
```
    i2c-bcm2708
    i2c-dev
```
And alter */etc/modprobe.d/raspi-blacklist.conf* and comment out the line:
```
   blacklist i2c-bcm2708
```
Increase the I2C baudrate from the default of 100KHz to 400KHz by altering
*/boot/config.txt* to include:
```
    dtparam=i2c_arm=on,i2c_baudrate=400000
```
Then reboot.

Then add your user to the i2c group:
```bash
    $ sudo adduser pi i2c
```
Install some packages:
```bash
    $ sudo apt-get install i2c-tools python-smbus python-pip
    $ sudo pip install pillow
```
Next check that the device is communicating properly (if using a rev.1 board, 
use 0 for the bus not 1):
```bash
    $ i2cdetect -y 1
         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- --
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    30: -- -- -- -- -- -- -- -- -- -- -- UU 3c -- -- --
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    70: -- -- -- -- -- -- -- --
```
According to the manual, "UU" means that probing was skipped, 
because the address was in use by a driver. It suggest that
there is a chip at that address. Indeed the documentation for
the device indicates it uses two addresses.

# Installing the Python Package

From the bash prompt, enter:

```bash
# $ sudo python setup.py install
python -m pip install .
```

This will install the python files in `/usr/local/lib/python2.7` making them ready for use in other programs.

# Example usage:
```python
import pigpio
from PIL import ImageFont, ImageDraw
from cheap_oled import OLED_SSD1306, OLED_SH1106, OLED_Canvas

pi = pigpio.pi()

if not pi.connected:
    exit()

font = ImageFont.load_default()
device = OLED_SSD1306(pi, port=1, address=0x3C)

with OLED_Canvas(device) as draw:
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.text(30, 40, "Hello World", font=font, fill=255)

device.close()

pi.stop()
```

 As soon as the with-block scope level is complete, the graphics primitives will be flushed to the device.

 Creating a new canvas is effectively 'carte blanche': If you want to retain an existing canvas, then make a reference like:
```python
c = OLED_Canvas(device)
for X in ...:
    with c as draw:
        draw.rectangle(...)
```
 As before, as soon as the with block completes, the canvas buffer is flushed to the device

Run the demos in the example directory:

    $ python examples/demo.py
    $ python examples/sys_info.py
    $ python examples/pi_logo.py
    $ python examples/maze.py

# References

* https://learn.adafruit.com/monochrome-oled-breakouts
* https://github.com/adafruit/Adafruit_Python_SSD1306
* http://www.dafont.com/bitmap.php
* http://raspberrypi.znix.com/hipidocs/topic_i2cbus_2.htm
* http://martin-jones.com/2013/08/20/how-to-get-the-second-raspberry-pi-i2c-bus-to-work/

# License

The MIT License (MIT)

Copyright (c) 2015 Richard Hull

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
