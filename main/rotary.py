import OPi.GPIO as GPIO
import atexit

atexit.register(GPIO.cleanup)

class Rotary:

    ROT_CW = 1
    ROT_CCW = 2
    SW_PRESS = 3

    def __init__(self, sw, dt1=None, dt2=None, clk1=None, clk2=None):
        self.dt_pin_rise = dt1
        self.dt_pin_fall = dt2
        self.clk_pin_rise = clk1
        self.clk_pin_fall = clk2
        self.sw_pin = sw

        GPIO.setboard(4) # Orange Pi One
        GPIO.setmode(GPIO.SOC) # GPIO column in gpio readall
        
        try:
            if dt1 is not None:
                GPIO.setup(self.dt_pin_rise, GPIO.IN)
                GPIO.add_event_detect(self.dt_pin_rise, GPIO.RISING, callback=self.rotary_change, bouncetime=100)
            if dt2 is not None:
                GPIO.setup(self.dt_pin_fall, GPIO.IN)
                GPIO.add_event_detect(self.dt_pin_fall, GPIO.FALLING, callback=self.rotary_change, bouncetime=100)
            if clk1 is not None:
                GPIO.setup(self.clk_pin_rise, GPIO.IN)
                GPIO.add_event_detect(self.clk_pin_rise, GPIO.RISING, callback=self.rotary_change, bouncetime=100)
            if clk2 is not None:
                GPIO.setup(self.clk_pin_fall, GPIO.IN)
                GPIO.add_event_detect(self.clk_pin_fall, GPIO.FALLING, callback=self.rotary_change, bouncetime=100)
            
            GPIO.setup(self.sw_pin, GPIO.IN)
            GPIO.add_event_detect(self.sw_pin, GPIO.RISING, callback=self.sw_change, bouncetime=300)
        except Exception:
            pass

        self.prev_status = 0b11
        self.curr_dt = 0
        self.curr_clk = 0

        self.handlers = []

    def rotary_change(self, pin):
        # Which edge fell
        if pin == self.dt_pin_fall:
            self.curr_dt = 0
        elif pin == self.clk_pin_fall:
            self.curr_clk = 0
        elif pin == self.dt_pin_rise:
            self.curr_dt = 1
        elif pin == self.clk_pin_rise:
            self.curr_clk = 1
        
        # Find way to offload below as scheduled task or something

        # 2 bits
        curr_status = self.curr_dt << 1 | self.curr_clk

        # ignore repeats
        if self.prev_status == curr_status:
            return
        
        # 4 bits
        transition = self.prev_status << 2 | curr_status
        
        # clockwise
        if transition == 0b1110:
            self.call_handlers(Rotary.ROT_CW)
        
        # counter-clockwise
        if transition == 0b1101:
            self.call_handlers(Rotary.ROT_CCW)

        self.prev_status = curr_status
        print(curr_status)

    def sw_change(self, pin):
        self.call_handlers(Rotary.SW_PRESS)

    def add_handler(self, handler):
        self.handlers.append(handler)

    def call_handlers(self, type):
        for handler in self.handlers:
            handler(type)
