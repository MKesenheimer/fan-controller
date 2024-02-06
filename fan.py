#!/usr/bin/env python3
# Copyright Matthias Kesenheimer <m.kesenheimer@gmx.net>
import os
import time
import signal
import sys
import RPi.GPIO as GPIO

pin = 18 # The pin ID, edit here to change it
setTMP = 40 # The setpoint of the temperature in Celsius
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.setwarnings(False)
p = GPIO.PWM(pin, 1000)
p.start(0)
file = open("/share/fan.out","w+") 
file.seek(0)
file.truncate()

KP = 20
KI = 1
KD = 10

pp = 0.0
ii = 0.0
dd = 0.0

loop = 5
nlines = 0
maxlines = 30 

def writeHeader():
    file.write("# PID is "+str(os.getpid())+"\n")
    file.write("# Kill with: kill -SIGINT "+str(os.getpid())+"\n")
    file.write("# loop intervall is "+str(loop)+"s"+"\n")
    file.write("# temp, P, I, D, dc\n")
    nlines = 3
    return()

def writeData(arr):
    s = str(arr[0])+" "
    s+= str(round(arr[1],1))+" "
    s+= str(round(arr[2],1))+" "
    s+= str(round(arr[3],1))+" "
    s+= str(round(arr[4],1))+"\n"
    file.write(s)
    global nlines
    nlines += 1
    if nlines>=maxlines:
        shortenFile()
    return()

def shortenFile():
    file.seek(0)
    d = file.readlines()
    d.pop(4) # data starts at line 4
    global nlines
    nlines -= 1
    file.seek(0)
    file.truncate()
    for i in d:
        file.write(i)
    file.truncate()
    return()

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    return temp

def setPWM(dc): 
    p.ChangeDutyCycle(dc)
    return()

def controlFAN():
    outTMP = float(getCPUtemperature())
    global pp, ii, dd
    temp = pp
    pp = outTMP-setTMP
    ii += outTMP-setTMP
    if ii > 100:
        ii = 100
    if ii < 0:
        ii = 0
    dd = temp - pp
    dc = KP*pp + KI*ii + KD*dd
    arr = [outTMP, KP*pp, KI*ii, KD*dd, dc]
    writeData(arr)
    if dc < 0:
        dc = 0
    if dc > 100:
        dc = 100
    setPWM(dc)
    return()

try:
    writeHeader()
    while True:
        controlFAN()
        time.sleep(loop)
except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt or use kill -SIGINT PID
    file.close()
    p.stop()
    GPIO.cleanup() # resets all GPIO ports used by this program
