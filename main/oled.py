import threading
import time
import os
import signal  # SIGTERM handling
import sys
import csv
import datetime
from sensors import Sensors
from enum import Enum

from rotary import Rotary
import pyky040
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


serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
device = st7735(serial, rotate=0, h_offset=1, v_offset=26, inverse=True)

image = Image.new("RGB", device.size, "black")
draw = ImageDraw.Draw(image)

font_size = 35
font_path = Path(__file__).resolve().parent.joinpath("fonts", "code2000.ttf")
font = ImageFont.truetype(font_path, font_size)

pos_prev = 0

# Pin setup

# def rotary_inc(pos):
#     global current_index
#     menu_items = get_current_menu()[Menu.ITEMS]
#     if current_index < len(menu_items) - 1:
#         current_index += 1
#         update_scroll()
#     update_display()


# def rotary_dec(pos):
#     global current_index
#     if current_index > 0:
#         current_index -= 1
#         update_scroll()
#     update_display()

direction = 0
step_count = 0


def rotary_change(pos):
    global current_index, pos_prev, direction, step_count

    # print(f"pos: {pos}")
    menu_items = get_current_menu()[Menu.ITEMS]

    # Determine direction
    if pos > pos_prev:
        new_direction = 1  # clockwise
    elif pos < pos_prev:
        new_direction = -1  # counter-clockwise
    else:
        return  # No change, exit early

    # Check if direction has changed
    if new_direction != direction:
        direction = new_direction
        step_count = 0

    # Increment step count
    step_count += abs(pos - pos_prev)

    # Update current_index if a full step is completed
    if step_count >= 2:
        if direction == 1 and current_index < len(menu_items) - 1:
            current_index += 1
            update_scroll()
        elif direction == -1 and current_index > 0:
            current_index -= 1
            update_scroll()

        # Reset step count
        step_count = 0

    pos_prev = pos
    update_display()


# File settings
save_directory = "/home/orangepi/Desktop/"
csv_filename = "sensor_data.csv"
csv_filepath = os.path.join(save_directory, csv_filename)


Item = Enum("Item", ["LABEL", "CALLBACK", "SUBMENU", "PARENT_MENU"], module=__name__)
Menu = Enum("Menu", ["ITEMS", "PARENT"], module=__name__)
Name = Enum(
    "Name", ["MAIN_MENU", "TRAIN_MENU", "SENSOR_MENU", "SENSOR_MENU_2"], module=__name__
)

# Display settings

VISIBLE_ITEMS = 3  # Number of menu items visible at once
current_menu = Name.MAIN_MENU
# current_menu = Name.TRAIN_MENU
current_index = 0  # Index of items
scroll_ctr = 0  # Offsets visible items
switch = 0

# Menu structure with callbacks
menu_structure = {
    Name.MAIN_MENU: {
        Menu.ITEMS: [
            {Item.LABEL: "Predict", Item.CALLBACK: lambda: print("Predict selected")},
            {Item.LABEL: "Fan ON", Item.CALLBACK: lambda: fan.on()},
            {Item.LABEL: "Fan OFF", Item.CALLBACK: lambda: fan.off()},
            {Item.LABEL: "Train", Item.SUBMENU: Name.TRAIN_MENU},
            # {
            #     Item.LABEL: "Sample",
            #     Item.CALLBACK: lambda: log_data(csv_filepath, "None"),
            # },
            {
                Item.LABEL: "Sensors",
                Item.SUBMENU: Name.SENSOR_MENU,
                Item.CALLBACK: lambda: draw_sensors(),
            },
            {Item.LABEL: "Reboot", Item.CALLBACK: lambda: os.system("reboot")},
            {Item.LABEL: "Shutdown", Item.CALLBACK: lambda: os.system("shutdown now")}
        ],
        Menu.PARENT: None,
    },
    Name.TRAIN_MENU: {
        Menu.ITEMS: [
            {Item.LABEL: "<< Back", Item.PARENT_MENU: Name.MAIN_MENU},
            {
                Item.LABEL: "Bagoong",
                Item.CALLBACK: lambda: log_data(csv_filepath, "Bagoong"),
            },
            {
                Item.LABEL: "Patis",
                Item.CALLBACK: lambda: log_data(csv_filepath, "Patis"),
            },
            {Item.LABEL: "Toyo", Item.CALLBACK: lambda: log_data(csv_filepath, "Toyo")},
            {Item.LABEL: "Suka", Item.CALLBACK: lambda: log_data(csv_filepath, "Suka")},
            {
                Item.LABEL: "Achara",
                Item.CALLBACK: lambda: log_data(csv_filepath, "Achara"),
            },
            {Item.LABEL: "Fan ON", Item.CALLBACK: lambda: fan.on()},
            {Item.LABEL: "Fan OFF", Item.CALLBACK: lambda: fan.off()},
            {
                Item.LABEL: "Sensors",
                Item.SUBMENU: Name.SENSOR_MENU_2,
                Item.CALLBACK: lambda: draw_sensors(),
            },
        ],
        Menu.PARENT: Name.MAIN_MENU,
    },
    Name.SENSOR_MENU: {
        Menu.ITEMS: [
            {Item.LABEL: "<< Back", Item.PARENT_MENU: Name.MAIN_MENU},
        ],
        Menu.PARENT: Name.MAIN_MENU,
    },
    Name.SENSOR_MENU_2: {
        Menu.ITEMS: [
            {Item.LABEL: "<< Back", Item.PARENT_MENU: Name.TRAIN_MENU},
        ],
        Menu.PARENT: Name.MAIN_MENU,
    },
}


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


def enter_submenu(menu_name):
    global current_menu, current_index, scroll_ctr
    current_menu = menu_name
    current_index = 0
    scroll_ctr = 0
    update_display()


def handle_menu_action():
    # print(get_current_menu()) 
    menu_item = get_current_menu()[Menu.ITEMS]
    selected_item = menu_item[current_index]
    # print(f"selected_item: {selected_item}")
    
    if Item.PARENT_MENU in selected_item:
        enter_submenu(selected_item[Item.PARENT_MENU])
    if Item.SUBMENU in selected_item:
        enter_submenu(selected_item[Item.SUBMENU])
    global switch
    if Item.CALLBACK in selected_item:
        if selected_item[Item.LABEL] == "Sensors":
            # print("Threaded sensors selected")
            switch = 0
            threading.Thread(target=draw_sensors).start()
        else:
            # print(f"Callback: {selected_item[Item.CALLBACK]}")
            selected_item[Item.CALLBACK]()
    if selected_item[Item.LABEL] == "<< Back":
        switch = 1


def rotary_sw(event):
    print("sw pressed")
    handle_menu_action()
    update_display()


# rotary = Rotary(20, 8, 2, 7, 21)  # GPIO.SOC
rotary = Rotary(sw=21)  # GPIO.SOC
encoder = pyky040.Encoder(
    CLK=6,
    DT=5,
    # SW = 7
)  # BCM
# encoder = pyky040.Encoder(CLK=8, DT=7, SW=21)  # SOC
encoder.setup(
    # inc_callback=rotary_inc,
    # dec_callback=rotary_dec,
    chg_callback=rotary_change,
    # sw_callback=rotary_sw,
    # sw_debounce_time=200,
)
threading.Thread(target=encoder.watch).start()
fan = Fan(13)  # GPIO.BCM
sensors = Sensors()


# def rotary_changed(event):
#     global current_index
#     menu_items = get_current_menu()[Menu.ITEMS]

#     if event == Rotary.ROT_CW and current_index < len(menu_items) - 1:
#         current_index += 1
#         update_scroll()
#     elif event == Rotary.ROT_CCW and current_index > 0:
#         current_index -= 1
#         update_scroll()
#     elif event == Rotary.SW_PRESS:
#         print("sw pressed")
#         handle_menu_action()
#     # print(current_index)
#     update_display()


def update_scroll():
    global scroll_ctr

    if current_index > scroll_ctr + VISIBLE_ITEMS - 1:
        scroll_ctr = current_index - VISIBLE_ITEMS + 1
    elif current_index < scroll_ctr:
        scroll_ctr = current_index


def log_data(filepath, target="Unspecified", sample_id="unspecified_0", sample_brand="Unspecified"):
    print("logging data...", end=" ")

    # Get current timestamp
    timestamp = datetime.datetime.now().isoformat(timespec="milliseconds")
    data = sensors.get_values()

    # Add sample_id and sample_brand to the row
    row = [timestamp] + data + [target, sample_id, sample_brand]
    print(row)
    
    # Append the data to the CSV file
    with open(filepath, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row)

    print("Success!")


def draw_sensors():
    print("drawing sensors...")
    global switch
    # print(f"switch: {switch}")
    last_update_time = time.time()
    update_interval = 0.2  # 200 milliseconds

    while switch != 1:
        current_time = time.time()

        if current_time - last_update_time >= update_interval:
            print(f"switch: {switch}")
            global font_size
            font_size = 15
            font = ImageFont.truetype(font_path, font_size)
            draw.rectangle(
                (0, 0, device.width, device.height), fill="black", outline="black"
            )
            data = sensors.get_values()

            # Left column sensors
            left_sensors = [
                ("MQ2", data[0]),
                ("MQ3", data[1]),
                ("MQ4", data[2]),
                ("MQ5", data[3]),
                ("MQ6", data[4]),
            ]

            # Right column sensors
            right_sensors = [
                ("MQ8", data[5]),
                ("MQ135", data[6]),
                ("PWR", data[7]),
                ("T", data[8]),
                ("H", data[9]),
            ]

            # Calculate positions
            left_x = 0
            right_x = device.width // 2
            y_spacing = 15  # Adjust this value to change vertical spacing

            # Draw left column
            for i, (sensor, value) in enumerate(left_sensors):
                text = f"{value}"
                draw.text(
                    (left_x, i * y_spacing), text, fill="white", font=font, anchor="lt"
                )

            # Draw right column
            for i, (sensor, value) in enumerate(right_sensors):
                text = f"{value}"
                draw.text(
                    (right_x, i * y_spacing), text, fill="white", font=font, anchor="lt"
                )

            device.display(image)
            font_size = 35
            font = ImageFont.truetype(font_path, font_size)

            last_update_time = current_time

        # Add a small delay to prevent excessive CPU usage
        time.sleep(0.01)


def create_csv(filepath):
    if os.path.isfile(filepath):
        print(f"Appending to '{filepath}'")
        return

    # Make sure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", newline="") as csvfile:
        print(f'Creating CSV file "{filepath}"...', end=" ")
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
                "sample_id",
                "sample_brand"
            ]
        )
        print("Success!")


def main():
    update_display()
    # draw_sensors()
    # rotary.add_handler(rotary_changed)

    
    # fan.on()
    fan.off()

    global running
    while running:
        # log_data(csv_filepath, target="Bagoong", sample_id="bagoong_0020", sample_brand="UFC")
        # log_data(csv_filepath, target="Fan", sample_id="bagoong_0020", sample_brand="UFC")
        # log_data(csv_filepath, target="Bagoong", sample_id="bagoong_0040", sample_brand="Barrio Fiesta")
        # log_data(csv_filepath, target="Fan", sample_id="bagoong_0040", sample_brand="Barrio Fiesta")

        log_data(csv_filepath, target="Air", sample_id="air_0016", sample_brand="Air")

        # log_data(csv_filepath, target="Achara", sample_id="achara_0020", sample_brand="Market")
        # log_data(csv_filepath, target="Fan", sample_id="achara_0020", sample_brand="Market")
        # log_data(csv_filepath, target="Air", sample_id="achara_0001", sample_brand="Market")

        # log_data(csv_filepath, target="Achara", sample_id="achara_0040", sample_brand="Baliwag")
        # log_data(csv_filepath, target="Fan", sample_id="achara_0040", sample_brand="Baliwag")

        # log_data(csv_filepath, target="Patis", sample_id="patis_0022", sample_brand="Lorins")
        # log_data(csv_filepath, target="Fan", sample_id="patis_0022", sample_brand="Lorins")
        # log_data(csv_filepath, target="Patis", sample_id="patis_0042", sample_brand="Silver Swan")
        # log_data(csv_filepath, target="Fan", sample_id="patis_0042", sample_brand="Silver Swan")

        # log_data(csv_filepath, target="Suka", sample_id="suka_0020", sample_brand="Datu Puti")
        # log_data(csv_filepath, target="Fan", sample_id="suka_0020", sample_brand="Datu Puti")
        # log_data(csv_filepath, target="Suka", sample_id="suka_0040", sample_brand="Silver Swan")
        # log_data(csv_filepath, target="Fan", sample_id="suka_0040", sample_brand="Silver Swan")


        # rotary_changed(Rotary.ROT_CW)
        # time.sleep(0.5)
        # rotary_changed(Rotary.SW_PRESS)
        # time.sleep(0.5)
        # rotary_changed(Rotary.ROT_CCW)
        # time.sleep(0.5)
        

        # log_data(csv_filepath, target="Toyo", sample_id="toyo_0020", sample_brand="Datu Puti")
        # log_data(csv_filepath, target="Fan", sample_id="toyo_0020", sample_brand="Datu Puti")
        # log_data(csv_filepath, target="Toyo", sample_id="toyo_0040", sample_brand="Silver Swan")
        # log_data(csv_filepath, target="Fan", sample_id="toyo_0040", sample_brand="Silver Swan")






        time.sleep(1)
        # time.sleep(0.1)


if __name__ == "__main__":
    try:
        rotary.add_handler(rotary_sw)

        # image = Image.new("RGB", device.size, "black")
        # draw = ImageDraw.Draw(image)

        # Set the directory where you want to save the CSV file
        create_csv(csv_filepath)

        main()
    except FileExistsError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        print("Goodbye")
