import FaBo9Axis_MPU9250
import time
mpu9250 = FaBo9Axis_MPU9250.MPU9250()

while True: 
    accel = mpu9250.readAccel()
    print("accel X: " + str(accel['x'])+" accel y: " + str(accel['y'])+" accel z: " + str(accel['z']))
    #print("accel X: " + str(accel['x']))
    #print("accel y: " + str(accel['y']))
    #print("accel z: " + str(accel['z']))

    time.sleep(0.1)

