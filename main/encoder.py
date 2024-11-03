import pyky040

# PIN_A =   24 # PC7
# PIN_B =   23 # PC4
# PIN_BTN =  4 # PA6

PIN_A =   6 # PA8
PIN_B =   5 # PA7
PIN_BTN =  7 # PA21

def inc_mock(pos):
    # print('Rotary incremented: {:d}'.format(pos))
    pass

def dec_mock(pos):
    # print('Rotary decremented: {:d}'.format(pos))
    pass

def chg_mock(pos):
    print('Rotary changed: {:d}'.format(pos))
    # pass

def sw_mock():
    print("Rotary pressed")

encoder = pyky040.Encoder(CLK = PIN_B, DT = PIN_A, SW = PIN_BTN)
encoder.setup(inc_callback=inc_mock, dec_callback=dec_mock, chg_callback=chg_mock, sw_callback=sw_mock, sw_debounce_time=100)
encoder.watch()

# try:
#     while True:
#         pass 
# finally:
#         GPIO.cleanup()