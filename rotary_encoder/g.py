import OPi.GPIO as GPIO
import atexit

#atexit.register(GPIO.cleanup)

dt_pin = 29

print(GPIO.RISING)

GPIO.setboard(4)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(dt_pin, GPIO.IN)
ctr = 0
def add_callback(pin, edge, callback):
    def callback_wrapper(pin):
        if edge == GPIO.RISING and GPIO.input(dt_pin): callback()
        elif edge == GPIO.FALLING and not GPIO.input(dt_pin): callback()

    global ctr
    if ctr == 0:
        GPIO.add_event_detect(dt_pin, GPIO.BOTH, callback=callback_wrapper)
        ctr += 1

def callback1(channel):
    print("Rising")

def callback2(channel):
    print("Falling")

add_callback(dt_pin, GPIO.RISING, callback1)
add_callback(dt_pin, GPIO.FALLING, callback2)

try:
    while True:
        pass

finally:
    GPIO.cleanup()
