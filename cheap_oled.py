#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 Richard Hull
# Copyright (c) 2022 Kestin Goforth
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class OLED_Commands:
    """
    Commands that can be sent to adjust the OLED settings
    """

    CHARGEPUMP = 0x8D
    COLUMNADDR = 0x21
    COMSCANDEC = 0xC8
    COMSCANINC = 0xC0
    DISPLAYALLON = 0xA5
    DISPLAYALLON_RESUME = 0xA4
    DISPLAYOFF = 0xAE
    DISPLAYON = 0xAF
    EXTERNALVCC = 0x1
    INVERTDISPLAY = 0xA7
    MEMORYMODE = 0x20
    NORMALDISPLAY = 0xA6
    PAGEADDR = 0x22
    SEGREMAP = 0xA0
    SETCOMPINS = 0xDA
    SETCONTRAST = 0x81
    SETDISPLAYCLOCKDIV = 0xD5
    SETDISPLAYOFFSET = 0xD3
    SETHIGHCOLUMN = 0x10
    SETLOWCOLUMN = 0x00
    SETMULTIPLEX = 0xA8
    SETPRECHARGE = 0xD9
    SETSEGMENTREMAP = 0xA1
    SETSTARTLINE = 0x40
    SETVCOMDETECT = 0xDB
    SWITCHCAPVCC = 0x2


class OLED_Device:
    """
    Base class for OLED driver classes
    """

    CMD_MODE = 0x00
    DATA_MODE= 0x40

    INIT_CMDS = ()

    def __init__(self, pi, size=(128, 64), port=1, address=0x3C, init_cmds=()):
        self._pi = pi
        self.width = size[0]
        self.height = size[1]
        self._pages = self.height // 8

        self._h = self._pi.i2c_open(port, address)

        self.write_commands(*self.INIT_CMDS)

        if init_cmds:
            self.write_commands(*init_cmds)

    def write_commands(self, *cmds):
        """
        Sends a command or sequence of commands through to the
        device - maximum allowed is 32 bytes in one go.
        """
        n_cmds = len(cmds)
        for i in range(0, n_cmds, 32):
            chunk = [self.CMD_MODE] + list(cmds[i:min(n_cmds, i + 32)])
            self._pi.i2c_write_device(self._h, chunk)

    def write_data(self, data):
        """
        Sends a data byte or sequence of data bytes through to the
        device - maximum allowed in one transaction is 32 bytes, so if
        data is larger than this it is sent in chunks.
        """
        n_data = len(data)
        for i in range(0, n_data, 32):
            chunk = [self.DATA_MODE] + list(data[i:min(n_data, i + 32)])
            self._pi.i2c_write_device(self._h, chunk)
    
    def close(self):
        self._pi.i2c_close(self._h)

class OLED_SH1106(OLED_Device):
    """
    A device encapsulates the I2C connection (address/port) to the SH1106
    OLED display hardware. After the device initializes further control
    commands can be sent to affect the brightness.
    Direct use of the write_commands() and write_data() methods are discouraged.
    """

    INIT_CMDS = (
        OLED_Commands.DISPLAYOFF,
        OLED_Commands.MEMORYMODE,
        OLED_Commands.SETHIGHCOLUMN,      0xB0, 0xC8,
        OLED_Commands.SETLOWCOLUMN,       0x10, 0x40,
        OLED_Commands.SETCONTRAST,        0x7F,
        OLED_Commands.SETSEGMENTREMAP,
        OLED_Commands.NORMALDISPLAY,
        OLED_Commands.SETMULTIPLEX,       0x3F,
        OLED_Commands.DISPLAYALLON_RESUME,
        OLED_Commands.SETDISPLAYOFFSET,   0x00,
        OLED_Commands.SETDISPLAYCLOCKDIV, 0xF0,
        OLED_Commands.SETPRECHARGE,       0x22,
        OLED_Commands.SETCOMPINS,         0x12,
        OLED_Commands.SETVCOMDETECT,      0x20,
        OLED_Commands.CHARGEPUMP,         0x14,
        OLED_Commands.DISPLAYON
    )

    def render_image(self, image):
        """
        Takes a 1-bit image and dumps it to the SH1106 OLED display.
        """
        assert(image.mode == '1')
        assert(image.size[0] == self.width)
        assert(image.size[1] == self.height)

        page = 0xB0
        pix = list(image.getdata())
        step = self.width * 8
        for y in range(0, self._pages * step, step):

            # move to given page, then reset the column address
            self.write_commands(page, 0x02, 0x10)
            page += 1

            buf = []
            for x in range(self.width):
                byte = 0
                for n in range(0, step, self.width):
                    byte |= (pix[x + y + n] & 0x01) << 8
                    byte >>= 1

                buf.append(byte)

            self.write_data(buf)


class OLED_SSD1306(OLED_Device):
    """
    A device encapsulates the I2C connection (address/port) to the SSD1306
    OLED display hardware. The init method pumps commands to the display
    to properly initialize it. Further control commands can then be
    called to affect the brightness. Direct use of the command() and
    data() methods are discouraged.
    """

    INIT_COMMANDS = (
        OLED_Commands.DISPLAYOFF,
        OLED_Commands.SETDISPLAYCLOCKDIV, 0x80,
        OLED_Commands.SETMULTIPLEX,       0x3F,
        OLED_Commands.SETDISPLAYOFFSET,   0x00,
        OLED_Commands.SETSTARTLINE,
        OLED_Commands.CHARGEPUMP,         0x14,
        OLED_Commands.MEMORYMODE,         0x00,
        OLED_Commands.SEGREMAP,
        OLED_Commands.COMSCANDEC,
        OLED_Commands.SETCOMPINS,         0x12,
        OLED_Commands.SETCONTRAST,        0xCF,
        OLED_Commands.SETPRECHARGE,       0xF1,
        OLED_Commands.SETVCOMDETECT,      0x40,
        OLED_Commands.DISPLAYALLON_RESUME,
        OLED_Commands.NORMALDISPLAY,
        OLED_Commands.DISPLAYON
    )

    def render_image(self, image):
        """
        Takes a 1-bit image and dumps it to the SSD1306 OLED display.
        """
        assert(image.mode == '1')
        assert(image.size[0] == self.width)
        assert(image.size[1] == self.height)

        self.write_commands(
            OLED_Commands.COLUMNADDR, 0x00, self.width-1,  # Column start/end address
            OLED_Commands.PAGEADDR,   0x00, self._pages-1   # Page start/end address
        )

        pix = list(image.getdata())
        step = self.width * 8
        buf = []
        for y in range(0, self._pages * step, step):
            i = y + self.width-1
            while i >= y:
                byte = 0
                for n in range(0, step, self.width):
                    byte |= (pix[i + n] & 0x01) << 8
                    byte >>= 1

                buf.append(byte)
                i -= 1

        self.write_data(buf)


class OLED_Canvas:
    """
    A canvas returns a properly-sized `ImageDraw` object onto which the caller
    can draw upon. As soon as the with-block completes, the resultant image is
    flushed onto the device.
    """
    def __init__(self, device):
        self._device = device
        self._draw = None
        self._image = Image.new('1', (device.width, device.height))

    def __enter__(self):
        self._draw = ImageDraw.Draw(self._image)
        return self._draw

    def __exit__(self, type, value, traceback):
        if type is None:
            # Draw image on device
            self._device.render_image(self._image)

        del self._draw  # Tidy up the resources
        return False    # Never suppress exceptions
