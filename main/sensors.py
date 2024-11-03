import ADS1115
import time
import OPi.GPIO as GPIO
import dht22
import datetime
import statistics
import atexit

atexit.register(GPIO.cleanup)


class Sensors:

    def __init__(self):
        GPIO.setboard(4)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)

        self.dht = dht22.DHT22(pin=4)

        self.ads1 = ADS1115.ADS1115(address=0x48)
        self.ads2 = ADS1115.ADS1115(address=0x49)

    def read_temp_humidity(self, retries=100):
        for _ in range(retries):
            result = self.dht.read()
            if result.is_valid():
                self.temp = result.temperature
                self.humidity = result.humidity
                return [self.temp, self.humidity]
            time.sleep(0.2)
    
        self.temp = -999
        self.humidity = -999
        return [self.temp, self.humidity]

    def read_ads(self):
        readings = []
        for _ in range(5):
            MQ2 = self.ads1.readADCSingleEnded(channel=0, sps=475)
            MQ3 = self.ads1.readADCSingleEnded(channel=1, sps=475)
            MQ4 = self.ads1.readADCSingleEnded(channel=2, sps=475)
            MQ5 = self.ads1.readADCSingleEnded(channel=3, sps=475)
            MQ6 = self.ads2.readADCSingleEnded(channel=0, sps=475)
            MQ8 = self.ads2.readADCSingleEnded(channel=1, sps=475)
            MQ135 = self.ads2.readADCSingleEnded(channel=2, sps=475)
            PWR = self.ads2.readADCSingleEnded(channel=3, sps=475)

            readings.append([MQ2, MQ3, MQ4, MQ5, MQ6, MQ8, MQ135, PWR])
            time.sleep(0.1)
            # print(readings)

        modes = []
        for i in range(8):  # channels of ads1 + ads2
            sensor_readings = [reading[i] for reading in readings]
            try:
                mode = statistics.median(sensor_readings)
                # print("median\t", end="")
            except statistics.StatisticsError:
                mode = statistics.mean(sensor_readings)
            #     print("error happened")
            # print("sensor_readings", sensor_readings, mode)
            modes.append(mode)

        return modes

    def get_values(self):
        values = []
        values += self.read_ads()
        values += self.read_temp_humidity()
        return values


if __name__ == "__main__":
    # Create an instance of the Sensors class
    sensors = Sensors()

    # Call the read_ads method
    ads_readings = sensors.read_ads()
    print("ADS Readings:", ads_readings)

    temp, humidity = sensors.read_temp_humidity()
    print(f"Temperature: {temp}°C, Humidity: {humidity}%")

    print(sensors.get_values())
