import ADS1115
import time
import OPi.GPIO as GPIO
import dht22
import datetime


GPIO.setboard(4)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(True)


instance = dht22.DHT22(pin=7)


ads1 = ADS1115.ADS1115(address=0x48)
ads2 = ADS1115.ADS1115(address=0x49)

def read_temp_humidity():
    result = instance.read()
    if result.is_valid():
        return result.temperature, result.humidity
    return None, None

try:
    temp = 0
    humidity = 0
    while True:
        
        new_temp, new_humidity = read_temp_humidity()
        if new_temp is not None and new_humidity is not None:
            temp = new_temp
            humidity = new_humidity

        
        MQ2 = ads1.readADCSingleEnded(channel=0, sps=475)
        MQ3 = ads1.readADCSingleEnded(channel=1, sps=475)
        MQ4 = ads1.readADCSingleEnded(channel=2, sps=475)
        MQ5 = ads1.readADCSingleEnded(channel=3, sps=475)
        MQ6 = ads2.readADCSingleEnded(channel=0, sps=475)
        MQ8 = ads2.readADCSingleEnded(channel=1, sps=475)
        MQ135 = ads2.readADCSingleEnded(channel=2, sps=475)
        PWR = ads2.readADCSingleEnded(channel=3, sps=475)

        
        print(f"{MQ2:4.0f}, {MQ3:4.0f}, {MQ4:4.0f}, {MQ5:4.0f}, {MQ6:4.0f}, {MQ8:4.0f}, {MQ135:4.0f}, {PWR:4.0f}, {temp:5.1f}, {humidity:5.1f}")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nCleanup")
    GPIO.cleanup()