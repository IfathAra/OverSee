import serial              
from time import sleep
import sys
import pyrebase
config = {
   "apiKey": "AIzaSyC40LmBxIdvaUZRPf8cP9jCIx_QJqu4DFY",
  "authDomain": "oversee-70b41.firebaseapp.com",
  "databaseURL": "https://oversee-70b41-default-rtdb.firebaseio.com",
  "projectId": "oversee-70b41",
  "storageBucket": "oversee-70b41.appspot.com",
  "messagingSenderId": "62841252291",
  "appId": "1:62841252291:web:0f7fe37c37beb4c73bb576",
  "measurementId": "G-D0XNDG0REX"
}

firebase_db = pyrebase.initialize_app(config)
db = firebase_db.database()

ser = serial.Serial ("/dev/ttyAMA0")
gpgga_info = "$GPGGA,"
GPGGA_buffer = 0
NMEA_buff = 0

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position

try:
    while True:
        received_data = (str)(ser.readline()) #read NMEA string received
        GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                
        if (GPGGA_data_available>0):
            GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after “$GPGGA,” string
            NMEA_buff = (GPGGA_buffer.split(','))
            nmea_time = []
            nmea_latitude = []
            nmea_longitude = []
            nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
            nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
            nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
            print("NMEA Time: ", nmea_time,'\n')
            print("NMEA Lat: ", nmea_latitude," ",len(nmea_latitude),'\n')
            print("NMEA Long: ", nmea_longitude," ",len(nmea_longitude),'\n')
            if(len(nmea_latitude) > 0 and len(nmea_longitude) >0):
                lat = (float)(nmea_latitude)
                lat = convert_to_degrees(lat)
                longi = (float)(nmea_longitude)
                longi = convert_to_degrees(longi)
                print ("NMEA Latitude:", lat,"NMEA Longitude:", longi,'\n')
                map_link = 'http://maps.google.com/?q='+lat+','+longi
                db.child("TestVal").update({"map":map_link})
                db.child("TestVal").update({"lat":lat})
                db.child("TestVal").update({"long":longi})
            
            #webbrowser.open(map_link)

except KeyboardInterrupt:
    sys.exit(0)