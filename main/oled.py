import time
from rotary import Rotary
import OPi.GPIO as GPIO

# For OLED
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Edit values
menu_items = ["Train", "Predict", "Fan"]
current_index = 0
font_size = 24
anchor_start = 20 
anchor_buffer = 20

# Oled Setup



# Rotary setup
rotary = Rotary(20,8,2,7,21) 

def rotary_changed(event):
    global current_index
    if event == Rotary.ROT_CW and current_index < len(menu_items) - 1:
        current_index += 1
        draw_menu(draw, font)
        device.clear()
        device.display(image)
    if event == Rotary.ROT_CCW and current_index > 0:
        current_index -= 1
        draw_menu(draw, font)
        device.clear()
        device.display(image)


def draw_menu(draw, font):
    for i, item in enumerate(menu_items):
        bbox = draw.textbbox((0, 0), f"{item}", font=font)
        x0, y0, x1, y1 = bbox
        text_height = y1 - y0
        if i == current_index:
            #draw.rectangle((0, anchor_start + i * anchor_buffer, 160, 45 + i * 10), fill="black", outline="black")
            draw.rectangle((x0, y0 + i * text_height , device.width, y1 + i * text_height), fill="white", outline="white")
            draw.text((x0, y0 + i * text_height -7), f"{item}", fill="black", font=font)
            print(bbox)
        else:
            draw.text((x0, y0 + i * text_height -7), f"{item}", fill="white", font=font)
            print(bbox)

def main():

    draw_menu(draw, font)

    device.display(image)

    rotary.add_handler(rotary_changed)



    while True:
        pass
    

if __name__ == "__main__":
    try:
        serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
        device = st7735(serial, rotate=0, h_offset=1, v_offset=27, inverse=True)

        font_path = Path(__file__).resolve().parent.joinpath('fonts','code2000.ttf')
        font = ImageFont.truetype(font_path, font_size)

        image = Image.new("RGB", device.size, "black")
        draw = ImageDraw.Draw(image)

        main()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
