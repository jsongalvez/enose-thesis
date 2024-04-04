import os
import time

# Set pin numbers
dt = 19
clk = 20
sw = 16
dt_prev = 0
clk_prev = 0
sw_prev = 1
dt_value = 1
clk_value = 1
sw_value = 0

# Set as INPUT
os.system(f"gpio mode {dt} in")
os.system(f"gpio mode {clk} in")
os.system(f"gpio mode {sw} in")

# Main loop
try:
	while True:
		# Read and print pin values
		dt_value = int(os.popen(f"gpio read {dt}").read())
		if dt_prev != dt_value:
			dt_prev = dt_value
			print(dt_value, clk_value, sw_value)
		clk_value = int(os.popen(f"gpio read {clk}").read())
		if clk_value != clk_prev:
			clk_prev = clk_value
			print(dt_value, clk_value, sw_value)
		sw_value = int(os.popen(f"gpio read {sw}").read())
		if sw_value != sw_prev:
			sw_prev = sw_value
			print(dt_value, clk_value, sw_value)
		# Delay before reading again

except KeyboardInterrupt:
	# Clean up on program exit
	print("\nExiting program")
	pass
