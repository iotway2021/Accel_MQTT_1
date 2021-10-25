import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import threading
import time
import paho.mqtt.client as mqtt
import json
import sys
from mpu6050 import mpu6050

publishDic ={}

X_vect1 =[]
Y_vect1 =[]
Z_vect1 =[]

X_vel1 =[]
Y_vel1 =[]
Z_vel1 =[]

XACCel =[]
YACCel =[]
ZACCel =[]

Xvel_fft =[]
Yvel_fft =[]
Zvel_fft =[]

def DoFFT():
    while len(X_vect1) < 1000:
        time.sleep(0.005)
    #fs = 20; #hz sampling frequency or the line freq
    LL = len(X_vect1)
    print("Samples:" + str(LL))
    N=LL
    #f = fs/2*np.linspace(0, 10, np.int(N/2+1))
    f = np.linspace(0.0, int (N/2), int (N/2))
    f = list(f)

    X = fft(X_vect1, N)/LL        # Accel. along X axis
    XACCel =2 * np.abs(X[0:np.int(N/2)])
    XACCel= list(XACCel)


    XVel = fft(X_vel1, N) / LL  # Vel. along X axis
    Xvel_fft = 2 * np.abs(XVel[0:np.int(N / 2)])
    Xvel_fft = list(Xvel_fft)

    Y = fft(Y_vect1, N)/LL          #% Accel. along Y axis
    YACCel =2 * np.abs(Y[0:np.int(N/2)])
    YACCel= list(YACCel)

    YVel = fft(Y_vel1, N) / LL  # Vel. along Y axis
    Yvel_fft = 2 * np.abs(YVel[0:np.int(N / 2)])
    Yvel_fft = list(Yvel_fft)

    Z = fft(Z_vect1, N)/LL         #% Accel. along Z axis
    ZACCel =2 * np.abs(Z[0:np.int(N/2)])
    ZACCel= list(ZACCel)

    ZVel = fft(Z_vel1, N) / LL  # Accel. along Y axis
    Zvel_fft = 2 * np.abs(ZVel[0:np.int(N / 2)])
    Zvel_fft = list(Zvel_fft)

def MQTTClientConnection():
    global mclient
    global IsMQTTConnectionisinProgress
    IsMQTTConnectionisinProgress =True
    while IsMQTTConnectionisinProgress:
        try:
            try:
                if mclient is not None:
                    mclient.disconnect()
            except:
                e = sys.exc_info()[0]
                print(e)

            mclient = mqtt.Client()
            mclient.username_pw_set("Demo","Demo123")
            print("Connecting MQTT!!!")

            IsMQTTConnected = mclient.connect("18.188.164.204",1884,10)
            mclient.on_connect = on_connect
            mclient.on_disconnect = on_disconnect
            mclient.loop_forever()
            print("Disconected from old thread")
            break
        except:
            e = sys.exc_info()[0]
            print(e)

        time.sleep(10)

def on_disconnect(client, userdata, rc):

    if not IsMQTTConnectionisinProgress:
        print("[INFO] DisConnected to broker")
        x3 = threading.Thread(target=MQTTClientConnection)
        x3.start()

def on_connect(client, userdata, flags, rc):
    global connected  # Use global variable
    global IsMQTTConnectionisinProgress
    if rc == 0:

        print("[INFO] Connected to broker")
        IsMQTTConnectionisinProgress = False
        connected = True  # Signal connection
    else:
        print("[INFO] Error,MQTT connection failed")


def MQTTPublishData():

    while True:
        try:
            time.sleep(60)
            DoFFT()
            if mclient.is_connected():
                publishDic["XAccel"] =X_vect1
                publishDic["YAccel"] = Y_vect1
                publishDic["ZAccel"] = Z_vect1
                publishDic["XAccel_FFT"] = XACCel
                publishDic["YAccel_FFT"] = YACCel
                publishDic["ZAccel_FFT"] = ZACCel
                publishDic["XVel"] = X_vel1
                publishDic["YVel"] = Y_vel1
                publishDic["ZVel"] = Z_vel1
                publishDic["XVel_FFT"] = Xvel_fft
                publishDic["YVel_FFT"] = Yvel_fft
                publishDic["ZVel_FFT"] = Zvel_fft

                jsonStr = json.dumps(publishDic)
                print(jsonStr)
                mclient.publish("FFTData", jsonStr)
                X_vect1.clear()
                Y_vect1.clear()
                Z_vect1.clear()
                XACCel.clear()
                YACCel.clear()
                ZACCel.clear()
                X_vel1.clear()
                Y_vel1.clear()
                Z_vel1.clear()
                Xvel_fft.clear()
                Yvel_fft.clear()
                Zvel_fft.clear()

        except:
            e = sys.exc_info()[0]
            print(e)



if __name__ == "__main__":
    x = threading.Thread(target=MQTTClientConnection)
    x.start()
    time.sleep(5)
    b = threading.Thread(target=MQTTPublishData, name='b')
    b.start()

    sensor = mpu6050(0x68)

    while True:
        try:
            if len(X_vect1) < 1000:
                accel_data = sensor.get_accel_data()
                gyro_data = sensor.get_gyro_data()
                temp = sensor.get_temp()
                X_vect1.append(accel_data['x'])
                Y_vect1.append(accel_data['y'])
                Z_vect1.append(accel_data['z'])
                X_vel1.append(gyro_data['x'])
                Y_vel1.append(gyro_data['y'])
                Z_vel1.append(gyro_data['z'])

        except:
            e = sys.exc_info()[0]
            print(e)

        time.sleep(0.001)