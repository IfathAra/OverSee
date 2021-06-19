import serial
import time
import string
import pynmea2

while True:
    port="/dev/ttyAMA0"
    ser=serial.Serial(port, baudrate=9600, timeout=0.5)
    dataout = pynmea2.NMEAStreamReader()
    newdata=ser.readline()
    print(newdata)
    if newdata[0:6] == "$GPRMC":
    #if newdata[0:6] == "$GPGGA":
        newmsg=pynmea2.parse(newdata)
        print(newmsg)
        lat=newmsg.latitude
        lng=newmsg.longitude
        gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
        print(gps)
