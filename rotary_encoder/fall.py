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

#channels
DT_FALL = 8
CLK_FALL = 7

#flags
curr_dt = 0b1
prev_dt = 0b1
curr_clk = 0b1
prev_clk = 0b1
curr_status = 0b11
prev_status = 0b11
curr_transition = 0b1111
prev_transition = 0b1111
curr_transition_change = 0b10001000
prev_transition_change = 0b10001000
curr_rotation_state = 0b1000100010001000
prev_rotation_state = 0b1000100010001000

#temp
ctr = 0

def setup():
    # setup
    GPIO.setboard(4)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(dt_pin_edge, GPIO.IN)
    GPIO.setup(clk_pin_edge, GPIO.IN)
    GPIO.setup(sw_pin_edge, GPIO.IN)
    GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(dt_pin_edge, GPIO.BOTH, callback=rotary_change, bouncetime=4)
    GPIO.add_event_detect(clk_pin_edge, GPIO.BOTH, callback=rotary_change, bouncetime=4)
    GPIO.add_event_detect(sw_pin_edge, GPIO.RISING, callback=sw_change)


def main():
    setup()

    while True:
        time.sleep(0.1)

def rotary_change(channel):
    global curr_dt, prev_dt
    global curr_clk, prev_clk
    global curr_status, prev_status
    global curr_transition, prev_transition
    global curr_transition_change, prev_transition_change
    global curr_rotation_state, prev_rotation_state
    global ctr

    # Which edge fell
    if channel == DT_FALL:
        curr_dt = 0
    elif channel == CLK_FALL:
        curr_clk = 0

    # 2 bits
    curr_status = curr_dt << 1 | curr_clk

    # ignore repeats
    if prev_status == curr_status:
        return
    
    # 4 bits
    curr_transition = prev_status << 2 | curr_status

    #print(f"{ctr}\t{prev_transition:>04b}\t{curr_transition:>04b}")

    # 8 bits
    curr_transition_change = prev_transition << 4 | curr_transition

    #print(f"{curr_transition_change:>08b}")

    curr_rotation_state = prev_transition_change << 8 | curr_transition_change

    print(f"{ctr}\t{prev_rotation_state:>016b}\t{curr_rotation_state:>016b}")

    if curr_rotation_state == prev_rotation_state and curr_rotation_state == 0b0:
        pass


    prev_dt = curr_dt
    prev_clk = curr_clk
    prev_status = curr_status
    prev_transition = curr_transition
    prev_transition_change = curr_transition_change
    prev_rotation_state = curr_rotation_state

    ctr += 1

    if curr_dt == 0 and curr_clk == 0:
        curr_dt = 1
        curr_clk = 1

def sw_change(channel):
    print("sw_change")

main()
