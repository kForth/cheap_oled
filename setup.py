#!/usr/bin/env python

from distutils.core import setup
setup(
    name = "cheap_oled",
    version = "1.0.0",
    author = "K.Goforth",
    author_email = "kgoforth1503@gmail.com",
    description = ("A small library to drive cheap OLED devices (SSD1306 or SH1106 chipsets)"),
    license = "MIT",
    keywords = "raspberry pi rpi oled ssd1306 sh1106",
    url = "https://github.com/kforth/cheap_oled",
    py_modules=['cheap_oled'],
)
