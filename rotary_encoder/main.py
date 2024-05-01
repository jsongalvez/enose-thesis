from rotary import Rotary
#import utime as time
import time

dt_pin_1 = 20
dt_pin_2 = 8
clk_pin_1 = 2
clk_pin_2 = 7
sw_pin = 21

with Rotary(20,8,2,7,21) as rot:
    def rotary_changed(change):
        print('rotary changed', change)

    rot.add_handler()

    while True:
        time.sleep(0.1)


#  val = 0

#  def rotary_changed(change):
#      global val
#      if change == Rotary.ROT_CW:
#          val = val + 1
#          print(val)
#      elif change == Rotary.ROT_CCW:
#          val = val - 1
#          print(val)
#      elif change == Rotary.SW_PRESS:
#          print('PRESS')
#      elif change == Rotary.SW_RELEASE:
#          print('RELEASE')
#          
#  rotary.add_handler(rotary_changed)

