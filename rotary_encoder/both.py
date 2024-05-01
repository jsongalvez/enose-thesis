import OPi.GPIO as GPIO
import atexit
import time

atexit.register(GPIO.cleanup)

#board pins
dt_pin_rise = 22
dt_pin_fall = 29
clk_pin_rise = 37
clk_pin_fall = 31
sw_pin = 26

#default values
val_dt = 1
val_clk = 1
val_sw = 0
val_dt_prev = val_dt
val_clk_prev = val_clk
val_sw_prev = val_sw

#channels
CH_DT_RISE = 20
CH_DT_FALL = 8
CH_CLK_RISE = 2
CH_CLK_FALL = 7

#flags
curr_dt = 0b1
prev_dt = 0b1
curr_clk = 0b1
prev_clk = 0b1
curr_status = 0b11
prev_status = 0b11
transition = 0b1111

#temp
ctr = 0

def setup():
    # setup
    GPIO.setboard(4)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(dt_pin_rise, GPIO.IN)
    GPIO.setup(dt_pin_fall, GPIO.IN)
    GPIO.setup(clk_pin_rise, GPIO.IN)
    GPIO.setup(clk_pin_fall, GPIO.IN)
    GPIO.setup(sw_pin, GPIO.IN)
    GPIO.add_event_detect(dt_pin_rise, GPIO.RISING, callback=rotary_change, bouncetime=4)
    GPIO.add_event_detect(dt_pin_fall, GPIO.FALLING, callback=rotary_change, bouncetime=4)
    GPIO.add_event_detect(clk_pin_rise, GPIO.RISING, callback=rotary_change, bouncetime=4)
    GPIO.add_event_detect(clk_pin_fall, GPIO.FALLING, callback=rotary_change, bouncetime=4)
    GPIO.add_event_detect(sw_pin, GPIO.RISING, callback=sw_change)


def main():
    setup()

    while True:
        time.sleep(0.1)

def rotary_change(channel):
    global curr_dt, prev_dt
    global curr_clk, prev_clk
    global curr_status, prev_status
    global transition
    global ctr

    # Which edge fell
    if channel == CH_DT_FALL:
        curr_dt = 0
    elif channel == CH_CLK_FALL:
        curr_clk = 0
    elif channel == CH_DT_RISE:
        curr_dt = 1
    elif channel == CH_CLK_RISE:
        curr_clk = 1

    # 2 bits
    curr_status = curr_dt << 1 | curr_clk

    # ignore repeats
    if prev_status == curr_status:
        return
    
    # 4 bits
    transition = prev_status << 2 | curr_status
    
    if transition == 0b1110:
        ctr += 1
        print(ctr)
    if transition == 0b1101:
        ctr -= 1
        print(ctr)

    prev_dt = curr_dt
    prev_clk = curr_clk
    prev_status = curr_status

def sw_change(channel):
    print("sw_change")

main()
