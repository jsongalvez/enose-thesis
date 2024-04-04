import os
import time

# Set pin numbers
dt = 19
clk = 20

# Set pin mode to INPUT
os.system(f"gpio mode {dt} up")
os.system(f"gpio mode {clk} up")

# Define the ISR (Interrupt Service Routine) function
def rotaryChange(pin):
	dt_value = int(os.popen(f"gpio read {dt}").read())
	clk_value = int(os.popen(f"gpio read {clk}").read())
	print(f"dtPin: {dt_value}, clkPin: {clk_value}")

# Attach interrupts to both pins
os.system(f"gpio wfi {dt} both")
os.system(f"gpio wfi {clk} both")

# Main loop
try:
	while True:
		pass
except KeyboardInterrupt:
	# Clean up on program exit
	print("\nExiting program")
