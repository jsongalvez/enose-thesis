from gurlgle import Rotary
import time
import OPi.GPIO as GPIO

def rotary_changed(event):
    event_type = {
        Rotary.ROT_CW: "Clockwise",
        Rotary.ROT_CCW: "Counter-clockwise",
        Rotary.SW_PRESS: "Button press",
        Rotary.SW_RELEASE: "Button release"
    }
    print(f">>> Handler called: {event_type.get(event, 'Unknown event')}")

print("\nStarting rotary encoder test...\n")

try:
    rotary = Rotary(8, 7, 21)
    rotary.add_handler(rotary_changed)
    
    print("\nMonitoring rotary encoder. Press Ctrl+C to exit.\n")
    
    counter = 0
    while True:
        # Print a periodic heartbeat to show the program is running
        if counter % 50 == 0:  # Every 5 seconds
            print(".", end="", flush=True)
        time.sleep(0.1)
        counter += 1
        
except KeyboardInterrupt:
    print("\n\nExiting due to keyboard interrupt...")
except Exception as e:
    print(f"\n\nError occurred: {e}")
finally:
    print("Cleaning up...")
    GPIO.cleanup()
    print("Done.")