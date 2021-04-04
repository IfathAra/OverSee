import numpy as np
from flask import Flask, request, jsonify, render_template,Response
import pickle
import cv2
app = Flask(__name__)
camera = cv2.VideoCapture(0)


def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/') # Homepage
def home():
    return render_template('index.html')

@app.route('/predict')
def predict():
    return render_template('page2.html')

@app.route('/back')
def back():
    return render_template('index.html')

@app.route('/next')
def next():
    return render_template('emotion.html')
@app.route('/previous')
def previous():
    return render_template('page2.html')

@app.route('/webcam')
def webcam():
    return render_template('gui.html')
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(port='4000',debug=True)