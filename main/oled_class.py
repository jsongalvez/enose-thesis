import time
from pathlib import Path
import OPi.GPIO as GPIO
from rotary import Rotary
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont

class MenuDisplay:
    def __init__(self, menu_items, font_size = 24):
        self.menu_items = menu_items
        self.current_index = 0
        self.font_size = font_size

    def setup_display(self):
        serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
        device = st7735(serial, rotate=0, h_offset=1, v_offset=27, inverse=True)
        font_path = Path(__file__).resolve().parent.joinpath('fonts', 'code2000.ttf')
        self.font = ImageFont.truetype(str(font_path), self.font_size)
        self.image = Image.new("RGB", self.device.size, "black")
        self.draw = ImageDraw.Draw(self.image)
    
    def setup_rotary(self):
        self.rotary = Rotary(20, 8, 2, 7, 21)
        self.rotary.add_handler(self.rotary_changed)
        
    def rotary_changed(self, event):
        if event == Rotary.ROT_CW and self.current_index < len(self.menu_items) - 1:
            self.current_index += 1
        elif event == Rotary.ROT_CCW and self.current_index > 0:
            self.current_index -= 1
        else:
            return
        self.update_display()
        
    def update_display(self):
        self.draw.rectangle((0, 0, self.device.width, self.device.height), fill="black")
        self.draw_menu()
        self.device.display(self.image)
        
    def draw_menu(self):
        for i, item in enumerate(self.menu_items):
            bbox = self.draw.textbbox((0, 0), item, font=self.font)
            x0, y0, x1, y1 = bbox
            text_height = y1 - y0
            y_pos = y0 + i * text_height - 7
            if i == self.current_index:
                self.draw.rectangle((x0, y_pos, self.device.width, y_pos + text_height), fill="white")
                self.draw.text((x0, y_pos), item, fill="black", font=self.font)
            else:
                self.draw.text((x0, y_pos), item, fill="white", font=self.font)
                
    def run(self):
        self.update_display()
        while True:
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            
def main():
    menu_items = ["Train", "Predict", "Fan"]
    display = MenuDisplay(menu_items)
    try:
        display.run()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()