import OPi.GPIO as GPIO
import atexit
import time

atexit.register(GPIO.cleanup)

class Rotary:
    ROT_CW = 1
    ROT_CCW = 2
    SW_PRESS = 4
    SW_RELEASE = 8
    
    def __init__(self, dt, clk, sw):
        print("Starting initialization...")
        self.dt_pin = dt
        self.clk_pin = clk
        self.sw_pin = sw
        
        # Initialize GPIO
        print("Setting up GPIO board...")
        GPIO.setboard(4)
        GPIO.setmode(GPIO.SOC)
        
        # Setup pins and print their initial states
        print(f"Configuring pins - DT: {dt}, CLK: {clk}, SW: {sw}")
        GPIO.setup(self.dt_pin, GPIO.IN)
        GPIO.setup(self.clk_pin, GPIO.IN)
        GPIO.setup(self.sw_pin, GPIO.IN)
        
        # Print initial states
        print(f"Initial pin states:")
        print(f"DT ({self.dt_pin}): {GPIO.input(self.dt_pin)}")
        print(f"CLK ({self.clk_pin}): {GPIO.input(self.clk_pin)}")
        print(f"SW ({self.sw_pin}): {GPIO.input(self.sw_pin)}")
        
        # Initialize last status
        self.last_status = (GPIO.input(self.dt_pin) << 1) | GPIO.input(self.clk_pin)
        print(f"Initial encoder status: {bin(self.last_status)}")
        
        # Try removing and re-adding event detection
        for pin in [self.dt_pin, self.clk_pin, self.sw_pin]:
            try:
                GPIO.remove_event_detect(pin)
                print(f"Removed existing event detection on pin {pin}")
            except:
                print(f"No existing event detection on pin {pin}")
        
        print("Adding event detection...")
        # Add event detection with debug messages
        try:
            GPIO.add_event_detect(self.dt_pin, GPIO.BOTH, callback=self.rotary_change)
            print(f"Added event detection to DT pin {self.dt_pin}")
        except Exception as e:
            print(f"Error adding DT event detection: {e}")
            
        try:
            GPIO.add_event_detect(self.clk_pin, GPIO.BOTH, callback=self.rotary_change)
            print(f"Added event detection to CLK pin {self.clk_pin}")
        except Exception as e:
            print(f"Error adding CLK event detection: {e}")
            
        try:
            GPIO.add_event_detect(self.sw_pin, GPIO.BOTH, callback=self.switch_detect)
            print(f"Added event detection to SW pin {self.sw_pin}")
        except Exception as e:
            print(f"Error adding SW event detection: {e}")
        
        self.handlers = []
        self.last_button_status = GPIO.input(self.sw_pin)
        self.debug_counter = 0
        print("Initialization complete\n")

    def rotary_change(self, pin):
        self.debug_counter += 1
        dt_val = GPIO.input(self.dt_pin)
        clk_val = GPIO.input(self.clk_pin)
        pin_name = "DT" if pin == self.dt_pin else "CLK"
        
        print(f"Event #{self.debug_counter} on {pin_name} pin:")
        print(f"  DT={dt_val} CLK={clk_val}")
        
        new_status = (dt_val << 1) | clk_val
        if new_status == self.last_status:
            print("  No state change detected")
            return
            
        transition = (self.last_status << 2) | new_status
        print(f"  Transition: {bin(transition)}")
        
        if transition == 0b1110:
            print("  Clockwise rotation detected")
            self.call_handlers(Rotary.ROT_CW)
        elif transition == 0b1101:
            print("  Counter-clockwise rotation detected")
            self.call_handlers(Rotary.ROT_CCW)
        else:
            print(f"  Unknown transition pattern: {bin(transition)}")
            
        self.last_status = new_status
        
    def switch_detect(self, pin):
        current_state = GPIO.input(self.sw_pin)
        print(f"Button event detected - state: {current_state}")
        
        if self.last_button_status == current_state:
            print("  Ignoring duplicate button state")
            return
            
        self.last_button_status = current_state
        if current_state:
            print("  Button released")
            self.call_handlers(Rotary.SW_RELEASE)
        else:
            print("  Button pressed")
            self.call_handlers(Rotary.SW_PRESS)
            
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    def call_handlers(self, type):
        for handler in self.handlers:
            handler(type)

    def __del__(self):
        print("Cleaning up GPIO...")
        GPIO.cleanup()
        print("Cleanup complete")