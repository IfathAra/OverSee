import tensorflow
from deepface import DeepFace
import cv2

img1=cv2.imread('ifath.jpg')
result= DeepFace.analyze(img1,actions=['emotion'])
print(result)