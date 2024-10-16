import OPi.GPIO as GPIO
import time
import atexit

atexit.register(GPIO.cleanup)

class Fan:
    def __init__(self, fan):
        self.fan_pin = fan
        
        GPIO.setboard(4) # Orange Pi One
        GPIO.setmode(GPIO.BCM) # GPIO column in gpio readall

        GPIO.setup(self.fan_pin, GPIO.OUT)

        
    def on(self):
        GPIO.output(self.fan_pin, GPIO.HIGH)
        print("Fan on for 5 seconds...")
        time.sleep(5)
        print("Fan off")
        self.off()
        
        
    def off(self):
        GPIO.output(self.fan_pin, GPIO.LOW)

