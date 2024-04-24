#!/usr/bin/env python

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def main():
    image = Image.new("RGB", device.size, "yellow")
    draw = ImageDraw.Draw(image)
    font_path = Path(__file__).resolve().parent.joinpath('fonts','code2000.ttf')
    font = ImageFont.truetype(font_path, 16)
    draw.text((40,40), "Hello World", fill=(255,255,255), font=font)
    device.display(image)
    while True:
        pass
    

if __name__ == "__main__":
    try:
        serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
        device = st7735(serial, rotate=0)
        main()
    except KeyboardInterrupt:
        pass
