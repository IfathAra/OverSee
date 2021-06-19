import FaBo9Axis_MPU9250
import time
mpu9250 = FaBo9Axis_MPU9250.MPU9250()
accel = mpu9250.readAccel()
basex=accel['x']
basey=accel['y']
basez=accel['z']
motion=0
while True: 
    accel = mpu9250.readAccel()
    diffx=abs(accel['x']-basex)
    diffy=abs(accel['y']-basey)
    diffz=abs(accel['z']-basez)
    print("accel X: " + str(accel['x'])+" accel y: " + str(accel['y'])+" accel z: " + str(accel['z']))
    if(diffx>0.03 or diffy>0.03 or diffz>0.03 ):
        motion=1
    else:
        motion=0 
    if(motion):
        print("Nortese")
    else:
        print("nortese naaaaa")
    #print("accel X: " + str(accel['x']))
    #print("accel y: " + str(accel['y']))
    #print("accel z: " + str(accel['z']))

    time.sleep(0.1)


