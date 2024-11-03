import time
import os
from rotary import Rotary
from fan import Fan
import OPi.GPIO as GPIO

# For OLED
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Pin setup
rotary = Rotary(20,8,2,7,21) # GPIO.SOC
fan = Fan(13) # GPIO.BCM

# Menu structure with callbacks
menu_structure = {
    "main": {
        "items": [
            {"label": "Predict", "callback": lambda: print("Predict selected")},
            {"label": "Fan", "callback": lambda: fan.on()},
            {"label": "Train", "submenu": "train_menu"},
            # {"label": "Reboot", "callback": lambda: os.system("reboot")},
            # {"label": "Shutdown", "callback": lambda: os.system("shutdown now")}
        ],
        "parent": None
    },
    "train_menu": {
        "items": [
            {"label": "<< Back", "parent_menu": "main"},
            {"label": "Bagoong", "callback": lambda: print("Training Bagoong")},
            {"label": "Patis", "callback": lambda: print("Training Patis")},
            {"label": "Toyo", "callback": lambda: print("Training Toyo")},
            {"label": "Suka", "callback": lambda: print("Training Suka")},
            {"label": "Achara", "callback": lambda: print("Training Achara")}
        ],
        "parent": "main"
    }
}

# Display settings
VISIBLE_ITEMS = 4  # Number of menu items visible at once
font_size = 20
current_menu = "main"
current_index = 0
scroll_offset = 0

def get_current_menu():
    return menu_structure[current_menu]

def get_visible_items():
    menu_items = get_current_menu()["items"]
    return menu_items[scroll_offset:scroll_offset + VISIBLE_ITEMS]

def handle_menu_action():
    menu_items = get_current_menu()["items"]
    selected_item = menu_items[current_index]
    
    if "callback" in selected_item:
        selected_item["callback"]()
    elif "submenu" in selected_item:
        enter_submenu(selected_item["submenu"])
    elif "parent_menu" in selected_item:
        enter_submenu(get_current_menu()["parent"])

def enter_submenu(menu_name):
    global current_menu, current_index, scroll_offset
    current_menu = menu_name
    current_index = 0
    scroll_offset = 0
    update_display()

def update_scroll():
    global scroll_offset
    menu_items = get_current_menu()["items"]
    
    # Adjust scroll if selection is beyond visible area
    if current_index >= scroll_offset + VISIBLE_ITEMS:
        scroll_offset = current_index - VISIBLE_ITEMS + 1
    elif current_index < scroll_offset:
        scroll_offset = current_index

def rotary_changed(event):
    global current_index
    menu_items = get_current_menu()["items"]
    
    if event == Rotary.ROT_CW and current_index < len(menu_items) - 1:
        current_index += 1
        update_scroll()
    elif event == Rotary.ROT_CCW and current_index > 0:
        current_index -= 1
        update_scroll()
    elif event == Rotary.SW_PRESS:
        handle_menu_action()
    
    print(current_index)
    update_display()

def draw_menu(draw, font):
    # Clear the display
    draw.rectangle((0, 0, device.width, device.height), fill="black", outline="black")
    
    # # Draw menu title or breadcrumb
    # if current_menu != "main":
    #     draw.text((0, 0), f"< {current_menu.replace('_', ' ').title()}", 
    #              fill="white", font=font, anchor="lt")
    #     y_offset = font_size + 5  # Add some padding after title
    # else:
    #     y_offset = 0
    
    y_offset = 0
    
    # Draw visible menu items
    visible_items = get_visible_items()
    for i, item in enumerate(visible_items):
        relative_index = i + scroll_offset
        bbox = draw.textbbox((0, 0), item["label"], font=font, anchor="lt")
        x0, y0, x1, y1 = bbox
        text_height = y1 - y0
        
        # Draw selection highlight
        if relative_index == current_index:
            draw.rectangle((x0, y_offset + i * text_height,
                          device.width, y_offset + (i + 1) * text_height),
                         fill="white", outline="white")
            text_color = "black"
        else:
            text_color = "white"
            
        draw.text((x0, y_offset + i * text_height), 
                 item["label"], fill=text_color, font=font, anchor="lt")
    
    # Draw scroll indicators if needed
    menu_items = get_current_menu()["items"]
    if scroll_offset > 0:
        draw.text((device.width - 10, 0), "▲", fill="white", font=font, anchor="rt")
    if scroll_offset + VISIBLE_ITEMS < len(menu_items):
        draw.text((device.width - 10, device.height - font_size),
                 "▼", fill="white", font=font, anchor="rb")

def update_display():
    draw.rectangle((0, 0, device.width, device.height), fill="black", outline="black")
    draw_menu(draw, font)
    device.display(image)

def main():
    update_display()
    rotary.add_handler(rotary_changed)
    
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
        device = st7735(serial, rotate=0, h_offset=1, v_offset=26, inverse=True)
        
        font_path = Path(__file__).resolve().parent.joinpath('fonts', 'code2000.ttf')
        font = ImageFont.truetype(font_path, font_size)
        
        image = Image.new("RGB", device.size, "black")
        draw = ImageDraw.Draw(image)
        
        main()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()