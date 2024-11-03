# from rotary import Rotary
from gurlgle import Rotary
import time

# rotary =  Rotary(20,8,2,7,21)
rotary =  Rotary(8,7,21)
val = 0

def rotary_changed(event):
    global val
    if event == Rotary.ROT_CW:
        val += 1
        print(val)
    elif event == Rotary.ROT_CCW:
        val -= 1
        print(val)
    elif event == Rotary.SW_PRESS:
        print('PRESS')

rotary.add_handler(rotary_changed)

while True:
    time.sleep(0.1)

