import serial

arduino_port = "/dev/cu.usbserial-AQ01L2Z7" #serial port of Arduino
baud = 115200 #arduino uno runs at 9600 baud
fileName="values.txt" #name of the CSV file generated

ser = serial.Serial(arduino_port, baud)
print("Connected to Arduino port:" + arduino_port)
file = open(fileName, "a")
print("Created file")

samples = 10 #how many samples to read 
samples *= 5 #each sample is 5 lines
samples += 10 #startup takes 10 lines
print_labels = False
line = 0 #start at 0 because our header is 0 (not real data)



# collect the samples


while(True):
    getData = ser.readline()
    dataString = getData.decode('utf-8')
    #data = dataString[0:]
    data = getData.decode('utf-8')
    print(data)
    with open(fileName, 'w', encoding='UTF8', newline='\n') as f:
        f.write(data)
    file.close()
