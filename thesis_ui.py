#!/usr/bin/python
import cv2
import numpy as np
from Tkinter import *
import tkMessageBox
import os
import picamera
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(06,GPIO.OUT)


print("100 dot pixel per centimeter")
print("Image taken will be 2592x1944")
print("maximum 10px radius for circle detection")
print("ensure that the background is clear white when taking a picture")
print("NOTICE: connect display using HDMI to test the camera")

top = Tk()
top.resizable(width=False, height=False)
top.title("Thesis")
top.geometry('480x320')

maxDiameter = StringVar()
area = StringVar()
result = StringVar()

maxDiameter.set("Max Diameter: ")
area.set("Area: ")
result.set("SVM Result: ")

MAIN_DIRECTORY='./'

def testCamera():
        camera = picamera.PiCamera()
        tkMessageBox.showinfo("Notice", "CTRL+D to stop preview")
        camera.start_preview()
        camera.close()


def cannyEdge():
        img = cv2.imread('sample.jpg')
        blur = cv2.medianBlur(img,17)
        
        cv2.imwrite('blur.jpg',blur)
        gray=cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

        edged = cv2.Canny(gray, 20, 50)
        cv2.imwrite('cannyEdged.jpg',edged)

def imageProcess():

        try:
                img = cv2.imread('cropped.jpg',0)
                img = cv2.medianBlur(img,3)
                cv2.imwrite('medianimg.jpg',img)
                os.system('sudo cp medianimg.jpg /var/www/html/medianimg.jpg') 
                cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
                cv2.imwrite('grayimg.jpg',cimg)
                os.system('sudo cp grayimg.jpg /var/www/html/grayimg.jpg') 
                eimg = cv2.Canny(cimg, 20, 50)
                cv2.imwrite('edgedimg.jpg',eimg)
                os.system('sudo cp edgedimg.jpg /var/www/html/edgedimg.jpg')
                
                output = img.copy()

                circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1.25,45,
                                         param1=40,param2=26,minRadius=0,maxRadius=90)
                
                x1=0
                if circles is not None:
                         #convert the (x, y) coordinates and radius of the circles to integers
                        circles = np.round(circles[0, :]).astype("int")
                 
                         #loop over the (x, y) coordinates and radius of the circles
                        for (x, y, r) in circles:
                                x1=x1+1                
                                diameter = (r*2)/float(7.5)
                                print(r)
                                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                                cv2.putText(output,str(diameter)[:4],(x-10,y+5), 1, 1,(255,255,255),2)
                                

                
                print "severity: " , x1 ," detected"
                diam = (max(circles[:,2])*2)/float(7.5)
                print "float: " , diam
                dArea = float(diam*diam*3.1416/6)
                sArea = str(round(dArea,2))
                maximum = str(round(diam,2))
                area.set("Area: " + sArea +"mm^2")
                maxDiameter.set("Max Diameter: " + maximum + "mm")
                cv2.imwrite('output.jpg',output)
                os.system('sudo cp output.jpg /var/www/html/output.jpg')
                print circles[:,2]
                svm(severity=x1,diameter=diam)

        except:
                result.set("SVM Result: ERROR: No Circle Detected")
                
def svm(severity,diameter):

        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib import style
        style.use("ggplot")
        from sklearn import svm


        X = np.array([
                    [19,3],
                    [19,9],
                    [19,11],
                    [19,17],
                    [1,11],    
                    [5,3],
                    [10,10],
                    [15,14],
                    [19,16],
                    [24,4],
                    [30,9],
                    [35,12],
                    [40,16],
                    [45,3],
                    [55,10],
                    [60,14],
                    [1,4],
                    [1,6],
                    [1,9],
                    [1,15],
                    [1,16],
                    [1,20],
                    [50,14],
                    [50,20],
                    [1,1],
                    [0,0],
                    [3,3],
                    [5,5],
                    [11,11],
                    [16,16],
                    [3,5]])

        y = [0,1,2,3,2,3,1,2,3,1,2,2,
             3,2,3,3,0,1,1,2,3,3,3,3,0,0,0,1,2,3,1]

        clf = svm.SVC(kernel='rbf', C=1)
        clf.fit(X,y)

        print "[0] = Negative"
        print "[1] = moderately sensitive"
        print "[2] = midly sensitive"
        print "[3] = very sensitive"
        print "Predicting the value of Wheal Size = 15mm and Amount = 5"
        pred = clf.predict([[severity,diameter]])
        print(pred)

        result.set("SVM Result: " + str(pred))
        
        plt.scatter(X[:, 0], X[:, 1], c = y)
        plt.legend()
        plt.savefig('plot.png')
        os.system('sudo cp plot.png /var/www/html/plot.png')
        #plt.show()

        ############PREDICT VALUE################

def takePicture():
        GPIO.output(26,GPIO.HIGH)
        GPIO.output(16,GPIO.HIGH)
        GPIO.output(19,GPIO.HIGH)
        GPIO.output(13,GPIO.HIGH)
        GPIO.output(06,GPIO.HIGH)

        camera = picamera.PiCamera()
        camera.resolution = (2592, 1944)
        #os.system('sudo cp image.jpg /var/www/html/orig.jpg')
        time.sleep(5)
        camera.capture('image.jpg')
        print "Image Captured."
        img = cv2.imread("image.jpg")
        
        #to crop the picture (original 1350:1780 , 150:2400]
        crop_img = img[ 1050:1800,450:1850]
        cv2.imwrite('cropped.jpg',crop_img)
        os.system('sudo cp image.jpg /var/www/html/orig.jpg')
        os.system('sudo cp cropped.jpg /var/www/html/crop.jpg')
        camera.close()
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(19,GPIO.LOW)
        GPIO.output(13,GPIO.LOW)
        GPIO.output(06,GPIO.LOW)

def manualSVM():
        try:
                diameter = entDiam.get()
                amount = entAmount.get()
                diam = float(diameter)
                amount= int(amount)
                dArea = float(diam*diam*3.1416/6)
                sArea = str(round(dArea,2))
                maximum = str(round(diam,2))
                area.set("Area: " + sArea +"mm^2")
                maxDiameter.set("Max Diameter: " + maximum + "mm")
                svm(severity=amount,diameter=diam)
        except:
                result.set("SVM Result: Input Error")
        
#buttons and labels
btnPicture = Button(top, text="Take Picture", command=takePicture, font=("piboto", 12))
btnStart = Button(top,text="Start Analysis",command=imageProcess, font=("piboto", 12))
lblDia = Label( top, textvariable=maxDiameter,font=("piboto", 12))
lblArea = Label(top, textvariable=area,font=("piboto", 12))
lblRes = Label(top, textvariable=result,font=("piboto", 12))
lblneg = Label(top, text="[0] = Negative",font=("piboto", 8))
lblmod = Label(top, text="[1] = moderately sensitive",font=("piboto", 8))
lblmil = Label(top, text="[2] = midly sensitive",font=("piboto", 8))
lblver = Label(top, text="[3] = very sensitive",font=("piboto", 8))
btnPicture.place(x=50,y=25)
btnStart.place(x=50,y=75)
lblDia.place(x=50,y=125)
lblArea.place(x=50,y=150)
lblRes.place(x=50,y=175)
lblneg.place(x=50,y=200)
lblmod.place(x=50,y=225)
lblmil.place(x=200,y=200)
lblver.place(x=200,y=225)
top.mainloop()

