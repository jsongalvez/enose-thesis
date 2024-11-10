import random
import csv

# Define the targets
targets = ['Bagoong', 'Achara', 'Patis', 'Suka', 'Toyo']

# Generate the data
data = []
for i in range(500):
    target = random.choice(targets)
    MQ2 = random.randint(300, 750)
    MQ3 = random.randint(150, 370)
    MQ4 = random.randint(380, 800)
    MQ5 = random.randint(20, 200)
    MQ6 = random.randint(240, 760)
    MQ8 = random.randint(80, 300)
    MQ135 = random.randint(450, 960)
    PWR = random.randint(4800, 5100)
    temp = round(random.uniform(40.0, 62.0), 1)
    humidity = round(random.uniform(14.0, 20.0), 1)
    row = [MQ2, MQ3, MQ4, MQ5, MQ6, MQ8, MQ135, PWR, temp, humidity, target]
    data.append(row)

# Write the data to a CSV file
with open('sensor_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ8', 'MQ135', 'PWR', 'temp', 'humidity', 'target'])
    writer.writerows(data)

print('CSV file created: sensor_data.csv')