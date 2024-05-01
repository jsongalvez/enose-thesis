import OPi.GPIO as GPIO
import atexit
import time

atexit.register(GPIO.cleanup)

#board pins
dt_pin_edge = 29
clk_pin_edge = 31
sw_pin_edge = 26
dt_pin = 22
clk_pin = 37

#default values
val_dt = 1
val_clk = 1
val_sw = 0
val_dt_prev = val_dt
val_clk_prev = val_clk
val_sw_prev = val_sw
last_status = 0b11
new_status = 0b11
transition = 0b1111

def main():
    GPIO.setboard(4)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(dt_pin_edge, GPIO.IN)
    GPIO.setup(clk_pin_edge, GPIO.IN)
    GPIO.setup(sw_pin_edge, GPIO.IN)
    GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(dt_pin_edge, GPIO.BOTH, callback=rotary_change)
    GPIO.add_event_detect(clk_pin_edge, GPIO.BOTH, callback=rotary_change)
    GPIO.add_event_detect(sw_pin_edge, GPIO.RISING, callback=sw_change)
    #global val_dt, val_dt_prev, val_clk, val_clk_prev
    global last_status
    last_status = GPIO.input(dt_pin) << 1 | GPIO.input(clk_pin)
    print(f"{last_status:b}")
    while True:
        time.sleep(0.1)
        
        #print(val_dt, val_clk, val_sw)
        #if val_dt != val_dt_prev or \
        #    val_clk != val_clk_prev or \
        #    val_sw != val_sw_prev:
        #    val_dt_prev = val_dt
        #    val_clk_prev = val_clk
        #    print(f"dt = {val_dt} clk = {val_clk}")

def rotary_change(channel):
    #global val_dt, val_clk
    #val_dt = GPIO.input(dt_pin)
    #val_clk = GPIO.input(clk_pin)
    global new_status, last_status, transition
    new_status = GPIO.input(dt_pin) << 1 | GPIO.input(clk_pin)
    transition = last_status << 2 | new_status
    #print(f"{transition:b}")
    if transition == 0b1101:
        #pass
        print("CW")
    elif transition == 0b1110:
        #pass
        print("CCW")
    last_status = new_status

def sw_change(channel):
    print("sw_change")

main()
