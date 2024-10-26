import time
import os
import signal # SIGTERM handling
import sys
from rotary import Rotary
from fan import Fan
import OPi.GPIO as GPIO

# For OLED
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Handle SIGTERM
# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
running = True
def sigterm_handler(_signo, _stack_frame):
    global running
    running = False

signal.signal(signal.SIGTERM, sigterm_handler)

# Edit values
menu_items = ["Predict", "Fan", "Train", "Reboot", "Shutdown"]
current_index = 0
font_size = 20

# Rotary setup
rotary = Rotary(20,8,2,7,21) # GPIO.SOC
fan = Fan(13) # GPIO.BCM

def rotary_changed(event):
    global current_index
    if event == Rotary.ROT_CW and current_index < len(menu_items) - 1:
        current_index += 1
    if event == Rotary.ROT_CCW and current_index > 0:
        current_index -= 1 
    if event == Rotary.SW_PRESS:
        item = menu_items[current_index]
        if item == "Fan":
            fan.on()
        if item == "Reboot":
            os.system("reboot")
        if item == "Shutdown":
            os.system("shutdown now")

    draw.rectangle((0,0,device.width, device.height), fill="black", outline="black")
    draw_menu(draw, font)
    device.display(image)


def draw_menu(draw, font):
    for i, item in enumerate(menu_items):
        bbox = draw.textbbox((0, 0), f"{item}", font=font, anchor="lt")
        x0, y0, x1, y1 = bbox
        text_height = y1 - y0
        if i == current_index:
            draw.rectangle((x0, y0 + i * text_height , device.width, y1 + i * text_height), fill="white", outline="white")
            draw.text((x0, y0 + i * text_height), f"{item}", fill="black", font=font, anchor="lt")
            print(bbox)
        else:
            draw.text((x0, y0 + i * text_height), f"{item}", fill="white", font=font, anchor="lt")
            print(bbox)

def main():

    draw_menu(draw, font)

    device.display(image)

    rotary.add_handler(rotary_changed)



    global running
    while running:
        time.sleep(0.1)
    

if __name__ == "__main__":
    try:
        serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
        device = st7735(serial, rotate=0, h_offset=1, v_offset=26, inverse=True)

        font_path = Path(__file__).resolve().parent.joinpath('fonts','code2000.ttf')
        font = ImageFont.truetype(font_path, font_size)

        image = Image.new("RGB", device.size, "black")
        draw = ImageDraw.Draw(image)

        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("CLEANING UP... GOODBYE.")
        GPIO.cleanup()
