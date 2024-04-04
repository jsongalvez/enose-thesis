import os
import time

# Set pin numbers
dt_pin = 19
clk_pin = 20
sw_pin = 16

# Initializations
dt_prev = clk_prev = sw_prev = -1
dt_value = clk_value = sw_value = 0

# Set as INPUT
os.system(f"gpio mode {dt_pin} in")
os.system(f"gpio mode {clk_pin} in")
os.system(f"gpio mode {sw_pin} in")

def read_pin(pin):
    return int(os.popen(f"gpio read {pin}").read())

def rotary():
    try:
        while True:
            global dt_prev, clk_prev, sw_prev
            global dt_value, clk_value, sw_value

            last_status = (dt_value << 1) | clk_value
            # Read and print pin values
            dt_value = read_pin(dt_pin)
            clk_value = read_pin(clk_pin)
            sw_value = read_pin(sw_pin)
            
            new_status = (dt_value << 1) | clk_value
            if last_status == new_status:
                continue
            print(dt_value, clk_value)

    except KeyboardInterrupt:
        # Clean up on program exit
        print("\nExiting program")
        pass

rotary()
