import OPi.GPIO as GPIO
import time

# intended for use with `watch -n0.1 gpio readall`

# Set the board to Orange Pi One
GPIO.setboard(4)


def blink_pin(pin, mode):
    GPIO.setmode(mode)
    try:
        GPIO.setup(pin, GPIO.OUT)
        print(f"Blinking pin {pin} in {switch(GPIO.getmode())} mode")
        for _ in range(5):  # 5 cycles = 2 seconds total
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.2)
    except:
        print(f"Pin {pin} is not available in {switch(GPIO.getmode())} mode")
    # finally:
    #     GPIO.cleanup(pin)


def switch(mode):
    if mode == GPIO.SOC:
        name = "GPIO.SOC"
    elif mode == GPIO.BOARD:
        name = "GPIO.BOARD"
    elif mode == GPIO.BCM:
        name = "GPIO.BCM"
    else:
        name = "Unknown"
    return name


def blink_all_pins(mode):
    print(f"\nTesting pins in {switch(mode)} mode:")
    GPIO.setmode(mode)
    for pin in range(1, 41):  # Assuming a 40-pin header
        blink_pin(pin, mode)
    time.sleep(1)  # Pause between modes


# # Test in SOC mode
blink_all_pins(GPIO.SOC)

# # Test in BOARD mode
# blink_all_pins(GPIO.BOARD)

# Test in BCM mode (not recommended, but included for completeness)
# blink_all_pins(GPIO.BCM)

GPIO.cleanup()
print("Test completed.")
