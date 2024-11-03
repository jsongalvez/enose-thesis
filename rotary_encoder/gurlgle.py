#import machine
#import utime as time
#from machine import Pin
#import micropython
import OPi.GPIO as GPIO
import atexit

atexit.register(GPIO.cleanup)

class Rotary:
    
    ROT_CW = 1
    ROT_CCW = 2
    SW_PRESS = 4
    SW_RELEASE = 8
    
    def __init__(self,dt,clk,sw):
        print("__init__")
        #self.dt_pin = Pin(dt, Pin.IN)
        #self.clk_pin = Pin(clk, Pin.IN)
        #self.sw_pin = Pin(sw, Pin.IN)
        self.dt_pin = dt
        self.clk_pin = clk
        self.sw_pin = sw
        GPIO.setboard(4)
        # GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.SOC)
        GPIO.setup(self.dt_pin, GPIO.IN)
        GPIO.setup(self.clk_pin, GPIO.IN)
        GPIO.setup(self.sw_pin, GPIO.IN)
        self.last_status = (GPIO.input(self.dt_pin) << 1) | GPIO.input(self.clk_pin)
        #self.dt_pin.irq(handler=self.rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING )
        #self.clk_pin.irq(handler=self.rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING )
        #self.sw_pin.irq(handler=self.switch_detect, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING )
        GPIO.add_event_detect(self.dt_pin, GPIO.BOTH, callback=self.rotary_change)
        GPIO.add_event_detect(self.clk_pin, GPIO.BOTH, callback=self.rotary_change)
        GPIO.add_event_detect(self.sw_pin, GPIO.BOTH, callback=self.switch_detect)
        self.handlers = []
        self.last_button_status = GPIO.input(self.sw_pin)

    def __exit__(self):
        print("__exit__")
        GPIO.cleanup()

    def rotary_change(self, pin):
        print(f"dt = {GPIO.input(self.dt_pin)} clk = {GPIO.input(self.clk_pin)} sw = {GPIO.input(self.sw_pin)}")
        new_status = (GPIO.input(self.dt_pin) << 1) | GPIO.input(self.clk_pin)
        if new_status == self.last_status:
            return
        transition = (self.last_status << 2) | new_status
        if transition == 0b1110:
            #micropython.schedule(self.call_handlers, Rotary.ROT_CW)
            self.call_handlers(Rotary.ROT_CW)
        elif transition == 0b1101:
            #micropython.schedule(self.call_handlers, Rotary.ROT_CCW)
            self.call_handlers(Rotary.ROT_CCW)
        self.last_status = new_status
        
    def switch_detect(self,pin):
        if self.last_button_status == GPIO.input(self.sw_pin):
            return
        self.last_button_status = GPIO.input(self.sw_pin)
        if GPIO.input(self.sw_pin):
            #micropython.schedule(self.call_handlers, Rotary.SW_RELEASE)
            self.call_handlers(Rotary.SW_RELEASE)
        else:
            #micropython.schedule(self.call_handlers, Rotary.SW_PRESS)
            self.call_handlers(Rotary.SW_PRESS)
            
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    def call_handlers(self, type):
        for handler in self.handlers:
            handler(type)
            
            
            
            
            
