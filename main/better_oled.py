import time
import os
import signal  # SIGTERM handling
import sys
import csv
import datetime
from sensors import Sensors
from enum import Enum
from rotary import Rotary
from fan import Fan
import OPi.GPIO as GPIO
import dht22

print(GPIO.__file__)

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

# Pin setup

rotary = Rotary(20, 8, 2, 7, 21)  # GPIO.SOC
fan = Fan(13)  # GPIO.BCM
sensors = Sensors()

Item = Enum("Item", ["LABEL", "CALLBACK", "SUBMENU", "PARENT_MENU"], module=__name__)
Menu = Enum("Menu", ["ITEMS", "PARENT"], module=__name__)
Name = Enum("Name", ["MAIN_MENU", "TRAIN_MENU"])

# Menu structure with callbacks

menu_structure = {
    Name.MAIN_MENU: {
        Menu.ITEMS: [
            {Item.LABEL: "Predict", Item.CALLBACK: lambda: print("Predict selected")},
            {Item.LABEL: "Fan", Item.CALLBACK: lambda: fan.on()},
            {Item.LABEL: "Train", Item.SUBMENU: Name.TRAIN_MENU},
            {Item.LABEL: "Sensors", Item.CALLBACK: lambda: log_data()},
            # {Item.LABEL: "Reboot", Item.CALLBACK: lambda: os.system("reboot")},
            # {Item.LABEL: "Shutdown", Item.CALLBACK: lambda: os.system("shutdown now")}
        ],
        Menu.PARENT: None,
    },
    Name.TRAIN_MENU: {
        Menu.ITEMS: [
            {Item.LABEL: "<< Back", Item.PARENT_MENU: Name.MAIN_MENU},
            {Item.LABEL: "Bagoong", Item.CALLBACK: lambda: print("Training Bagoong")},
            {Item.LABEL: "Patis", Item.CALLBACK: lambda: print("Training Patis")},
            {Item.LABEL: "Toyo", Item.CALLBACK: lambda: print("Training Toyo")},
            {Item.LABEL: "Suka", Item.CALLBACK: lambda: print("Training Suka")},
            {Item.LABEL: "Achara", Item.CALLBACK: lambda: print("Training Achara")},
        ],
        Menu.PARENT: Name.MAIN_MENU,
    },
}

# Display settings

VISIBLE_ITEMS = 4  # Number of menu items visible at once
font_size = 20
current_menu = Name.MAIN_MENU
# current_menu = Name.TRAIN_MENU
current_index = 0  # Index of items
scroll_ctr = 0  # Offsets visible items


def rotary_changed(event):
    global current_index
    menu_items = get_current_menu()[Menu.ITEMS]

    if event == Rotary.ROT_CW and current_index < len(menu_items) - 1:
        current_index += 1
        update_scroll()
    elif event == Rotary.ROT_CCW and current_index > 0:
        current_index -= 1
        update_scroll()
    elif event == Rotary.SW_PRESS:
        handle_menu_action()
    # print(current_index)
    update_display()


def update_scroll():
    global scroll_ctr

    if current_index > scroll_ctr + VISIBLE_ITEMS - 1:
        scroll_ctr = current_index - VISIBLE_ITEMS + 1
    elif current_index < scroll_ctr:
        scroll_ctr = current_index


def handle_menu_action():
    menu_item = get_current_menu()[Menu.ITEMS]
    selected_item = menu_item[current_index]

    if Item.CALLBACK in selected_item:
        selected_item[Item.CALLBACK]()
    elif Item.SUBMENU in selected_item:
        enter_submenu(selected_item[Item.SUBMENU])
    elif Item.PARENT_MENU in selected_item:
        enter_submenu(selected_item[Item.PARENT_MENU])


def enter_submenu(menu_name):
    global current_menu, current_index, scroll_ctr
    current_menu = menu_name
    current_index = 0
    scroll_ctr = 0
    update_display()


def get_current_menu():
    return menu_structure[current_menu]


def get_visible_items():
    menu_items = get_current_menu()[Menu.ITEMS]
    return menu_items[scroll_ctr : scroll_ctr + VISIBLE_ITEMS]


def draw_menu(draw, font):
    visible_items = get_visible_items()
    cumulative_height = 0
    for i, item in enumerate(visible_items):
        current_i = i + scroll_ctr
        bbox = draw.textbbox((0, 0), item[Item.LABEL], font=font, anchor="lt")
        x0, y0, x1, y1 = bbox
        text_height = y1 - y0

        # hightlight

        if current_i == current_index:
            draw.rectangle(
                (
                    x0,
                    y0 + cumulative_height,
                    device.width,
                    y0 + cumulative_height + text_height,
                ),
                fill="white",
                outline="white",
            )
            font_color = "black"
        else:
            font_color = "white"
        # text

        # print(f"i: {i}")
        # print(f"x0: {x0}, y0: {y0}, i: {i}, text_height: {text_height}")
        # print(f"y0 + i * text_height: {y0 + cumulative_height}")
        draw.text(
            (x0, y0 + cumulative_height),
            item[Item.LABEL],
            fill=font_color,
            font=font,
            anchor="lt",
        )

        cumulative_height += text_height
    # scroll indicators

    menu_items = get_current_menu()[Menu.ITEMS]
    if scroll_ctr > 0:
        draw.text((device.width - 10, 0), "▲", fill="white", font=font, anchor="rt")
    if scroll_ctr + VISIBLE_ITEMS < len(menu_items):
        draw.text((device.width - 10, 0), "▼", fill="white", font=font, anchor="rb")


def update_display():
    draw.rectangle((0, 0, device.width, device.height), fill="black", outline="black")
    draw_menu(draw, font)
    device.display(image)


def log_data():
    print("logging data...", end=" ")

    # Get current timestamp
    timestamp = datetime.datetime.now().isoformat(timespec="minutes")
    data = sensors.get_values()

    row = [timestamp] + data

    # Append the data to the CSV file
    with open("sensor_data.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row)

    print("Success!")


def create_csv(filename):
    if os.path.isfile(filename):
        print(f"Appending to '{filename}'")
        return

    with open(filename, "w", newline="") as csvfile:
        print(f"Creating CSV file \"{filename}\"...", end=" ")
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Timestamp",
                "MQ2",
                "MQ3",
                "MQ4",
                "MQ5",
                "MQ6",
                "MQ8",
                "MQ135",
                "PWR",
                "temp",
                "humidity",
                "target",
            ]
        )
        print("Success!")


def main():
    update_display()
    rotary.add_handler(rotary_changed)

    global running
    while running:
        rotary_changed(Rotary.ROT_CW)
        time.sleep(0.5)
        rotary_changed(Rotary.ROT_CW)
        time.sleep(0.5)
        rotary_changed(Rotary.ROT_CW)
        time.sleep(0.5)
        rotary_changed(Rotary.SW_PRESS)
        time.sleep(0.5)
        rotary_changed(Rotary.ROT_CCW)
        time.sleep(0.5)
        rotary_changed(Rotary.ROT_CCW)
        time.sleep(0.5)
        rotary_changed(Rotary.ROT_CCW)
        time.sleep(0.5)
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
        device = st7735(serial, rotate=0, h_offset=1, v_offset=26, inverse=True)

        font_path = Path(__file__).resolve().parent.joinpath("fonts", "code2000.ttf")
        font = ImageFont.truetype(font_path, font_size)

        image = Image.new("RGB", device.size, "black")
        draw = ImageDraw.Draw(image)

        create_csv("sensor_data.csv")

        main()
    except FileExistsError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        print("Goodbye")
