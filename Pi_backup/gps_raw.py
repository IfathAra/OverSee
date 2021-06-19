import serial
from time import sleep
import sys
ser = serial.Serial("/dev/ttyAMA0")
try:
    while True:
        received_data = (str)(ser.readline()) #nmea
        print(received_data,"\n")
except KeyboardInterrupt:
    sys.exit(0)