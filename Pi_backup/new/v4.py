from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import serial              
from time import sleep
import sys
import pyrebase
import time
import dlib
import cv2
import os
import pyrebase
import pygame
import FaBo9Axis_MPU9250
import time
import socket
pygame.mixer.init()
#from playsound import playsound

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

statedr="normal"
stateprevdr="normal"

stateyw="normal"
stateprevyw="normal"

statetk="normal"
stateprevtk="normal"

statest="normal"
stateprevst="normal"

statefc = "normal"
stateprevfc = "normal"

stateang = "normal"
stateprevang = "normal"

def test_connection():
    try:
        socket.create_connection(('Google.com',80))
        return True
    except OSError:
        return False
    
def eyebrow_distance(shape):
    left_eyebrow = shape[21]
    right_eyebrow = shape[22]
    distance = left_eyebrow[1] - right_eyebrow[1]
    return distance

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear

def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)

def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))

    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))

    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)

    distance = abs(top_mean[1] - low_mean[1])
    return distance

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position

ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0,
                help="index of webcam on system")
args = vars(ap.parse_args())

lat = "23.8276"
longi = "90.3857"
#lat = convert_to_degrees(lat)
#longi = convert_to_degrees(longi)

EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 20
COUNTER_EYE = 0
COUNTER_NORMAL = 0

EYE_AR_THRESH_STRESS = 0.20
FRAME_COUNT_STRESS = 0
COUNTER_EYE_STRESS = 0

EYEBROW_THRESH = 2
COUNTER_ANGER = 0
COUNTER_ANGER_FRAME = 0
COUNTER_ANGER_NORMAL = 0

YAWN_THRESH = 25
YAWN_CONSEC_FRAMES = 5
COUNTER_YAWN = 0
COUNTER_NORMAL_YAWN = 0

TALK_FRAMES=30
TALK_THRESH = 16
COUNTER_TALK = 0
COUNTER_FRAME = 0
FRAME_LIMIT=58
COUNTER_NORMAL_TALK = 0

COUNTER_FACE_NORMAL = 0
no_face = 0

print("-> Loading the predictor and detector...")
detector = dlib.get_frontal_face_detector()
#detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")    #Faster but less accurate
#hand_detector = cv2.CascadeClassifier("palm.xml") 
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

print("-> Starting Video Stream")
vs = VideoStream(src=args["webcam"]).start()
#vs = VideoStream(src='fariha_ghum.mp4').start()
#vs= VideoStream(usePiCamera=True).start()       //For Raspberry Pi
firebase_db = pyrebase.initialize_app(config)
db = firebase_db.database()

ser = serial.Serial ("/dev/ttyAMA0")
gpgga_info = "$GPGGA,"
GPGGA_buffer = 0
NMEA_buff = 0



time.sleep(1.0)

mpu9250 = FaBo9Axis_MPU9250.MPU9250()
accel = mpu9250.readAccel()
basex=accel['x']
basey=accel['y']
basez=accel['z']
motion=0
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    
    received_data = (str)(ser.readline()) #read NMEA string received
    GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                
    if (GPGGA_data_available>0):
        GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after ???$GPGGA,??? string
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
            if(test_connection()):
                db.child("TestVal").update({"map":map_link})
            #db.child("TestVal").update({"lat":lat})
            #db.child("TestVal").update({"long":longi})
            

    
    
    accel = mpu9250.readAccel()
    diffx=abs(accel['x']-basex)
    diffy=abs(accel['y']-basey)
    diffz=abs(accel['z']-basez)
    print("accel X: " + str(accel['x'])+" accel y: " + str(accel['y'])+" accel z: " + str(accel['z']))
    if(diffx>0.03 or diffy>0.03 or diffz>0.03 ):
        motion=1
    else:
        motion=0
        
    if(motion==0):
        print("Moving")
        
        
        if(COUNTER_FRAME <= FRAME_LIMIT):
            COUNTER_FRAME = COUNTER_FRAME + 1
        else:
            COUNTER_FRAME = 0

        if(FRAME_COUNT_STRESS <= 100):
            FRAME_COUNT_STRESS = FRAME_COUNT_STRESS + 1
        else:
            FRAME_COUNT_STRESS = 0

        if(COUNTER_ANGER>0):
            COUNTER_ANGER_FRAME = COUNTER_ANGER_FRAME+1
        else:
            COUNTER_ANGER_FRAME = 0

        #for haarcascade
       
        #rects = detector.detectMultiScale(gray, scaleFactor=1.1, #for haarcascade
        #   minNeighbors=5, minSize=(30, 30),
        #   flags=cv2.CASCADE_SCALE_IMAGE)

        for rect in rects:
        #for (x, y, w, h) in rects:
         #   rect = dlib.rectangle(int(x), int(y), int(x + w),int(y + h))
           
            no_face=0
            COUNTER_FACE_NORMAL += 1
            if(COUNTER_FACE_NORMAL >=20):
                statefc = "normal"
                COUNTER_FACE_NORMAL = 0
                if(statefc!=stateprevfc):
                    if(test_connection()):
                        db.child("TestVal").update({"talk":"Inattention"})
                    stateprevfc=statefc    


            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            eye = final_ear(shape)
            ear = eye[0]
            leftEye = eye [1]
            rightEye = eye[2]

            distance = lip_distance(shape)

            distance1 = eyebrow_distance(shape)

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 155, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            lip = shape[48:60]
            cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

            if ear < EYE_AR_THRESH:
                COUNTER_EYE += 1

                if COUNTER_EYE >= EYE_AR_CONSEC_FRAMES:

                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    statedr = "Drowsiness Detected"
                    #playsound('drowsy.wav')
                    #lattitude = '23.3456'
                    #longitude = '90.2345'
                    park_link = 'https://'+'www.google.com/maps/search/Parking/@'+ lat+ ',' + longi + ',15z/data=!3m1!4b1!4m7!2m6!3m5!1sParking!2s' + lat + ',' + longi+ '!4m2!1d' + longi + '!2d' + lat +''
                    if(test_connection()):
                        db.child("TestVal").update({"link":park_link})
                    pygame.mixer.music.load("drowsy.wav")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() == True:
                        continue

                    if(statedr != stateprevdr):
                        if(statedr == "Drowsiness Detected"):
                            if(test_connection()):
                                db.child("TestVal").update({"Sleep":"Take rest"})
                            stateprevdr=statedr
            else:
                COUNTER_EYE=0
                COUNTER_NORMAL += 1
                if(COUNTER_NORMAL >= 20):
                    statedr = "normal"
                    COUNTER_NORMAL = 0
                    if(statedr != stateprevdr):
                        if(test_connection()):
                            db.child("TestVal").update({"Sleep":"Sleep"})
                        stateprevdr=statedr

            if ear < EYE_AR_THRESH:
                COUNTER_EYE_STRESS += 1
                print(COUNTER_EYE_STRESS)
                print(FRAME_COUNT_STRESS)
                cv2.putText(frame, "blink!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if (COUNTER_EYE_STRESS >= 50 and FRAME_COUNT_STRESS <= 100):
                    cv2.putText(frame, "STRESS ALERT!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    statest = "stress"
                    #playsound('anger.wav')
                    FRAME_COUNT_STRESS = 0
                    COUNTER_EYE_STRESS = 0
                    if(statest != stateprevst):
                        if(test_connection()):
                            db.child("TestVal").update({"Anger":"stressed"})
                        stateprevst = statest
                    pygame.mixer.music.load('stress.wav')
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() == True:
                        continue   
            if(COUNTER_EYE_STRESS < 50 and FRAME_COUNT_STRESS == 100):
                COUNTER_EYE_STRESS = 0
                statest = "normal"
                if(statest!=stateprevst):
                    if(test_connection()):
                        db.child("TestVal").update({"Anger":"Anger"})
                    stateprevst = statest

            if (distance1 > EYEBROW_THRESH):
                COUNTER_ANGER = COUNTER_ANGER + 1
                #print(""+ COUNTER_ANGER + " " + COUNTER_ANGER_FRAME)
                cv2.putText(frame, "Disgust Mode Alert", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                if(COUNTER_ANGER >= 50 and COUNTER_ANGER_FRAME <= 80):
                    COUNTER_ANGER_FRAME = 0
                    COUNTER_ANGER = 0
                    stateang='angry'
                    if(stateprevang!=stateang):
                        if(test_connection()):
                            db.child("TestVal").update({"Anger":"disgusted"})
                        stateprevang=stateang
                    
                    pygame.mixer.music.load('anger.wav')
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() == True:
                        continue
            else:
                COUNTER_ANGER_NORMAL = COUNTER_ANGER_NORMAL+1
                if(COUNTER_ANGER_NORMAL >= 50):
                    COUNTER_ANGER_NORMAL = 0
                    stateang = "normal"
                    if(stateang != stateprevang):
                        if(test_connection()):
                            db.child("TestVal").update({"Anger":"Anger"})
                        stateprevang = stateang
               

            if (distance > YAWN_THRESH):
                COUNTER_YAWN = COUNTER_YAWN + 1
                if(COUNTER_YAWN >= YAWN_CONSEC_FRAMES):
                    res_link = 'https://'+'www.google.com/maps/search/Resturants/@'+ lat+ ',' + longi + ',15z/data=!3m1!4b1!4m7!2m6!3m5!1sRestaurants!2s' + lat + ',' + longi+ '!4m2!1d' + longi + '!2d' + lat +''
                    #db.child("TestVal").update({"res":res_link})
                    #print("SEEEEEEEEEEEEEEEEEEEEE")
                    print(test_connection())
                    if(test_connection()):
                        db.child("TestVal").update({"link":res_link})
                        
                    cv2.putText(frame, "Yawn Alert", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    stateyw = "Yawning Detected"
                    #playsound('yawn.wav')
                    pygame.mixer.music.load('yawn.wav')
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() == True:
                        continue

                    if(stateyw != stateprevyw):
                        if(stateyw == "Yawning Detected"):
                            if(test_connection()):
                                db.child("TestVal").update({"Sleep":"Be careful"})
                                #db.child("TestVal").update({"res":res_link})
                            stateprevyw = stateyw
            else:
                COUNTER_YAWN = 0
                COUNTER_NORMAL_YAWN += 1
                if(COUNTER_NORMAL_YAWN >= 10):
                    stateyw = "normal"
                    COUNTER_NORMAL_YAWN = 0
                    if(stateyw!=stateprevyw):
                        if(test_connection()):
                            db.child("TestVal").update({"Sleep":"Sleep"})
                        stateprevyw=stateyw
                        

            
            if (distance < YAWN_THRESH and distance > TALK_THRESH):
                COUNTER_TALK += 1
                if(COUNTER_TALK >= TALK_FRAMES and COUNTER_FRAME >= FRAME_LIMIT):
                    #playsound('talking.wav')
                    pygame.mixer.music.load('talking.wav')
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() == True:
                        continue

                    statetk = "Talking Detected"        
                    if(test_connection()):
                        db.child("TestVal").update({"talk":"Be attentive"})
                    stateprevtk=statetk
                    COUNTER_TALK=0
                    COUNTER_FRAME=0


                cv2.putText(frame, "Talking Alert", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
            else:
                COUNTER_NORMAL_TALK += 1
                if(COUNTER_NORMAL_TALK >= 10):
                    statetk = "normal"
                    COUNTER_NORMAL_TALK = 0
                    if(statetk!=stateprevtk):
                        if(test_connection()):
                            db.child("TestVal").update({"talk":"Inattention"})
                        stateprevtk=statetk

            cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "YAWN: {:.2f}".format(distance), (300, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        no_face+=1
        if no_face>60:
            statefc = "not attentive"
            cv2.putText(frame,"No Face {:.2f} sec".format(no_face), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            pygame.mixer.music.load("attention.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
            if(test_connection()):
                db.child("TestVal").update({"talk":"pay attention"}) 
            stateprevfc = statefc
            #no_face = 0 
                
    else:
        print("Not moving so no alert!")
        
    
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
            break

cv2.destroyAllWindows()
vs.stop()