import ADS1115
import time
import OPi.GPIO as GPIO
import dht22
import datetime

# initialize GPIO
GPIO.setboard(4) # Orange Pi One
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(True)

# read data using pin 7
instance = dht22.DHT22(pin=7)

try:
	while True:
		result = instance.read()
		if result.is_valid():
			print("Last valid input: " + str(datetime.datetime.now()))

			print("Temperature: %-3.1f C" % result.temperature)
			print("Humidity: %-3.1f %%" % result.humidity)

		time.sleep(5)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()

ads1 = ADS1115.ADS1115(address=0x48)
ads2 = ADS1115.ADS1115(address=0x49)
while True:
    time.sleep(0.1)
    MQ2 = ads1.readADCSingleEnded(channel=0, sps=475)
    #time.sleep(0.1)
    MQ3 = ads1.readADCSingleEnded(channel=1, sps=475)
    #time.sleep(0.1)
    MQ4 = ads1.readADCSingleEnded(channel=2, sps=475)
    #time.sleep(0.1)
    MQ5 = ads1.readADCSingleEnded(channel=3, sps=475)
    #time.sleep(0.1)
    MQ6 = ads2.readADCSingleEnded(channel=0, sps=475)
    #time.sleep(0.1)
    MQ8 = ads2.readADCSingleEnded(channel=1, sps=475)
    #time.sleep(0.1)
    MQ135 = ads2.readADCSingleEnded(channel=2, sps=475)
    #time.sleep(0.1)
    PWR = ads2.readADCSingleEnded(channel=3, sps=475)
    print(f"MQ2={MQ2:.0f} mV\t", end='', flush=True)
    print(f"MQ3={MQ3:.0f} mV\t", end='', flush=True)
    print(f"MQ4={MQ4:.0f} mV\t", end='', flush=True)
    print(f"MQ5={MQ5:.0f} mV\t", end='', flush=True)
    print(f"MQ6={MQ6:.0f} mV\t", end='', flush=True)
    print(f"MQ8={MQ8:.0f} mV\t", end='', flush=True)
    print(f"MQ135={MQ135:.0f} mV\t", end='', flush=True)
    print(f"PWR={PWR:.0f} mV", flush=True)