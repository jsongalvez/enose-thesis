import OPi.GPIO as GPIO

#  #board pin (physical)
#  dt_pin_rise = 22
#  dt_pin_fall = 29
#  clk_pin_rise = 37
#  clk_pin_fall = 31
#  sw_pin = 26
#  
#  #default values
#  val_dt = 1
#  val_clk = 1
#  val_sw = 0
#  val_dt_prev = val_dt
#  val_clk_prev = val_clk
#  val_sw_prev = val_sw
#  
#  #channels (GPIO)
#  CH_DT_RISE = 20
#  CH_DT_FALL = 8
#  CH_CLK_RISE = 2
#  CH_CLK_FALL = 7
#  CH_SW = 21

class Rotary:

    def __init__(self, dt1, dt2, clk1, clk2, sw):
        self.dt_pin_rise = dt1
        self.dt_pin_fall = dt2
        self.clk_pin_rise = clk1
        self.clk_pin_fall = clk2
        self.sw_pin = sw

        GPIO.setboard(4) # Orange Pi One
        GPIO.setmode(GPIO.SOC) # GPIO column in gpio readall
        
        GPIO.setup(dt_pin_rise, GPIO.IN)
        GPIO.setup(dt_pin_fall, GPIO.IN)
        GPIO.setup(clk_pin_rise, GPIO.IN)
        GPIO.setup(clk_pin_fall, GPIO.IN)
        GPIO.setup(sw_pin, GPIO.IN)
        
        GPIO.add_event_detect(self.dt_pin_rise, GPIO.RISING, callback=self.rotary_change, bouncetime=4)
        GPIO.add_event_detect(self.dt_pin_fall, GPIO.FALLING, callback=self.rotary_change, bouncetime=4)
        GPIO.add_event_detect(self.clk_pin_rise, GPIO.RISING, callback=self.rotary_change, bouncetime=4)
        GPIO.add_event_detect(self.clk_pin_fall, GPIO.FALLING, callback=self.rotary_change, bouncetime=4)
        GPIO.add_event_detect(self.sw_pin, GPIO.RISING, callback=sw_change)

        self.prev_status = 0b11

    def __exit__(self, exc_type, exc_val, exc_tb):
        GPIO.cleanup()

    def rotary_change(self, pin):
        # Which edge fell
        if pin == self.dt_pin_fall:
            curr_dt = 0
        elif pin == self.clk_pin_fall:
            curr_clk = 0
        elif pin == self.dt_pin_rise:
            curr_dt = 1
        elif pin == self.clk_pin_rise:
            curr_clk = 1
        
        # Find way to offload below as scheduled task or something

        # 2 bits
        curr_status = curr_dt << 1 | curr_clk

        # ignore repeats
        if self.prev_status == curr_status:
            return
        
        # 4 bits
        transition = self.prev_status << 2 | curr_status
        
        # clockwise
        if transition == 0b1110:
            # add callback
        
        # counter-clockwise
        if transition == 0b1101:
            # add callback

        self.prev_status = curr_status

    def sw_change(channel):
        print("sw_change")
