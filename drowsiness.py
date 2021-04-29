from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import os
import pyrebase
from playsound import playsound

config = {
    "apiKey": "AIzaSyCOw2PuWM4tDQrY7ua7eUumvQZqZgT9uOs",
    "authDomain": "oversee-6fa5e.firebaseapp.com",
    "projectId": "oversee-6fa5e",
    "databaseURL": "https://oversee-6fa5e-default-rtdb.firebaseio.com/",
    "storageBucket": "oversee-6fa5e.appspot.com",
    "messagingSenderId": "141840160013",
    "appId": "1:141840160013:web:8ac2c33955727150040c44",
    "measurementId": "G-E9JD6D1MMC",
    "serviceAccount": "overseeServiceAccountKey.json"
}

firebase_db = pyrebase.initialize_app(config)
db = firebase_db.database()

statedr="normal"
stateprevdr="normal"

stateyw="normal"
stateprevyw="normal"

statetk="normal"
stateprevtk="normal"

def alarm(msg):
    global alarm_status
    global alarm_status2
    global saying

    while alarm_status:
        s = 'espeak "'+msg+'"'
        os.system(s)

    if alarm_status2:
        saying = True
        s = 'espeak "' + msg + '"'
        os.system(s)
        saying = False

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


ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0,
                help="index of webcam on system")
args = vars(ap.parse_args())

EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 50
TALK_FRAMES=200
YAWN_THRESH = 30
TALK_THRESH = 11
alarm_status = False
alarm_status2 = False
saying = False
COUNTER_EYE = 0
COUNTER_TALK = 0
COUNTER_FRAME = 0
no_face = 0
FRAME_LIMIT=400
print("-> Loading the predictor and detector...")
detector = dlib.get_frontal_face_detector()
#detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")    #Faster but less accurate
#hand_detector = cv2.CascadeClassifier("palm.xml") 
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')


print("-> Starting Video Stream")
vs = VideoStream(src=args["webcam"]).start()
#vs = VideoStream(src='fariha_ghum.mp4').start()
#vs= VideoStream(usePiCamera=True).start()       //For Raspberry Pi
time.sleep(1.0)

while True:

    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)
    
    COUNTER_FRAME += 1
    #for haarcascade
   
    #rects = detector.detectMultiScale(gray, scaleFactor=1.1, #for haarcascade
	#	minNeighbors=5, minSize=(30, 30),
	#	flags=cv2.CASCADE_SCALE_IMAGE)

    for rect in rects:
    #for (x, y, w, h) in rects:
     #   rect = dlib.rectangle(int(x), int(y), int(x + w),int(y + h))
       
        no_face=0
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        eye = final_ear(shape)
        ear = eye[0]
        leftEye = eye [1]
        rightEye = eye[2]

        distance = lip_distance(shape)

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
                playsound('drowsy.wav')
                
                if(statedr != stateprevdr):
                    if(statedr == "Drowsiness Detected"):
                        db.child("TestVal").update({"drowsy":"You are Drowsy, Please take some rest"})
                        stateprevdr=statedr
        else:
            COUNTER_EYE=0
            statedr = "normal"
            if(statedr!=stateprevdr):
                db.child("TestVal").update({"drowsy":"You are not Drowsy, Have a safe drive"})
                stateprevdr=statedr

        if (distance > YAWN_THRESH):
                cv2.putText(frame, "Yawn Alert", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                stateyw = "Yawning Detected"
                playsound('yawn.wav')
                
                if(stateyw != stateprevyw):
                    if(stateyw == "Yawning Detected"):
                        db.child("TestVal").update({"Yawn":"You are Yawning. Please take some rest"})
                        stateprevyw = stateyw
        else:
            stateyw = "normal"
            if(stateyw!=stateprevyw):
                db.child("TestVal").update({"Yawn":"You are not Yawning, Have a safe drive"})
                stateprevyw=stateyw

        
        if (distance < YAWN_THRESH and distance > TALK_THRESH):
            COUNTER_TALK += 1
            if(COUNTER_TALK>=TALK_FRAMES and COUNTER_FRAME>=FRAME_LIMIT):
                playsound('talking.wav')
                statetk = "Talking Detected"        
                db.child("TestVal").update({"talk":"Ypu are Talking, Please be Attentive"})
                stateprevtk=statetk
                COUNTER_TALK=0
                COUNTER_FRAME=0


            cv2.putText(frame, "Talking Alert", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        else:
            statetk = "normal"
            if(statetk!=stateprevtk):
                db.child("TestVal").update({"talk":"You are not Talking, Have a safe drive"})
                stateprevtk=statetk

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "YAWN: {:.2f}".format(distance), (300, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    no_face+=1
    if no_face>100:
        cv2.putText(frame,"No Face {:.2f} sec".format(no_face), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()
