import numpy as np
import base64
import pytesseract
import cv2 as cv
from PIL import Image
import time
import paho.mqtt.client as mqtt
from threading import Thread, Lock,Semaphore
import io
import re
from vpdconfig import *
from recipe import * 
import json
import requests
import datetime
import os
import subprocess
#################### SERVER ##################
serverconfig = VPDServer()
#################### Config ##################
config = VPDConfig()
################## LastRecipe ################
lastRecipe = VPDLastMachineRecipe()
#################### Recipe ##################
recipeParam = VPDparam()
#################### StateMachine ############
mutex = Lock() # loak main process
pauseProcess = False
ReqTakePicture = False 
ReqReboot = False
reqstoploopprocess = False
################### MQTT #####################
mqtt_client = mqtt.Client()
lastpublishStatus = ''
################# Process ####################
sem = Semaphore(1)
ProcThread = []

recipeOK = False
################ TNF #########################
base64tnfImg = '/9j/4AAQSkZJRgABAQEBLAEsAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAAXADEBAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/AOy/4VnoX/QXP/fS/wCNH/Cs9C/6C5/76X/Gj/hWehf9Bc/99L/jR/wrPQv+guf++l/xo/4VnoX/AEFz/wB9L/jR/wAKz0L/AKC5/wC+l/xo/wCFZ6F/0Fz/AN9L/jXD/wDCMeJv+fC7/P8A+vR/wjHib/nxu/z/APr0n/CMeJv+fC7/AD/+vS/8Ix4m/wCfC7/P/wCvR/wjHib/AJ8bv8//AK9H/CMeJv8Anwu/z/8Ar0n/AAjHib/nwu/z/wDr10H/AAtfVv8An1go/wCFr6t/z6wUf8LX1b/n1go/4Wvq3/PrBR/wtfVv+fWCj/ha+rf8+sFH/C19W/59YK//2Q=='
TNFimg = []
Cameraindex = 0
countTrytoConnect = 3
maxTrytoConnect = 5
#############################################

class Proc():
    def __init__(self,recipeParam = None,frame=None,sem=None,serverconfig=None,config=None,TNFimg=None):
        #Thread.__init__(self)
        self.recipeParam = recipeParam
        self.frame = frame
        self.sem = sem
        self.serverconfig = serverconfig
        self.config = config
        self.TNFimg = TNFimg
        
    def EdgesDetect(self,image):
        return cv.Canny(image, 100, 200)

    def GrayImg(self,image):
        return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    def CropROI(self,imageCrop,ROI):
        #edited return imageCrop[ROI.Col1:ROI.Col2, ROI.Row1:ROI.Row2]
         return imageCrop[ROI.Row1:ROI.Row2, ROI.Col1:ROI.Col2]

    def ReadOCR(self,image):
        #custom_config = r'-l eng --psm 6'
        #custom_config = r'--oem 3 --psm 6'
        #custom_co((nfig = r'--psm 7'
        cv.waitKey(2)
        custom_config = r'--oem 3 --psm 7'
        text = pytesseract.image_to_string(image, config=custom_config,lang='eng')
        return re.sub(r'\n{2, 10}', '\n', text[:-2].strip().replace('\u2018','').replace('\u2014','').replace('\u00a2','').replace('\u00b0',':')).rstrip("\n\x0c")#.replace('Beata ice) ig','ERROR')

    def QRcodeReader(self,frame2,drawROI = False):
        detector = cv.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(frame2)
        if (bbox is not None):
            if(drawROI):
                for i in range(len(bbox)):
                    cv.line(frame2, tuple(bbox[i][0]), tuple(bbox[(i + 1) % len(bbox)][0]), color=(255,0, 255), thickness=2)
        
                cv.putText(frame2, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
        else:
            data = "Not Found"
        return data
    
    def ReadTNFerror(self,img):
        (r1, c1, r2, c2) = [24, 701, 67, 864]
        crop = img[r1:r2, c1:c2]
        custom_config = r'--oem 3 --psm 7'
        ocr0 = pytesseract.pytesseract.image_to_string(crop, lang='eng', config=custom_config)
        indexstr = ocr0.find('ERROR')
        return (indexstr != -1)

    def calculateIntersection(self,a0, a1, b0, b1):
        if a0 >= b0 and a1 <= b1:  # Contained
            intersection = a1 - a0
        elif a0 < b0 and a1 > b1:  # Contains
            intersection = b1 - b0
        elif a0 < b0 and a1 > b0:  # Intersects right
            intersection = a1 - b0
        elif a1 > b1 and a0 < b1:  # Intersects left
            intersection = b1 - a0
        else:
            intersection = 0
        return intersection

    def findOverlap(self,x0, y0, x1, y1):
        # roi_error
        X0, Y0, X1, Y1, = [697, 25, 867, 66]
        AREA = float((X1 - X0) * (Y1 - Y0))
        width = self.calculateIntersection(x0, x1, X0, X1)
        height = self.calculateIntersection(y0, y1, Y0, Y1)
        area = width * height
        percent = area / AREA
        
        if (percent >= 0.65):
            print('IsOverlap')
            return True
        else:
            return False

    def sort_contours(self,cnts, method="left-to-right"):
	    reverse = False
	    i = 0
	    if method == "right-to-left" or method == "bottom-to-top":
		    reverse = True
	    if method == "top-to-bottom" or method == "bottom-to-top":
		    i = 1

	    boundingBoxes = [cv.boundingRect(c) for c in cnts]
	    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		    key=lambda b:b[1][i], reverse=reverse))
	    # return the list of sorted contours and bounding boxes
	    return (cnts, boundingBoxes)

    def TNF_readerFunction(self,img):
        #cv.imshow('threshold',img)
        imgRun = []
        #find Standard diviation
        contrast = []
        gray_hsv = cv.cvtColor(cv.cvtColor(img,cv.COLOR_BGR2HSV),cv.COLOR_BGR2GRAY)
        contrast.append(gray_hsv.std())
        gray_rgb = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        contrast.append(gray_rgb.std())
        if(contrast[0]>contrast[1]):
            imgRun = gray_hsv
        else:
            imgRun = gray_rgb
        
        isMat = False
        res = cv.matchTemplate(imgRun,self.TNFimg, cv.TM_CCOEFF_NORMED)
        treshole = 0.5
        loc = np.where(res >= treshole)
        for pt in zip(*loc[::-1]):
            if len(pt) == 2:
                isMat = True
                break
        ret, thresh1 = cv.threshold(imgRun, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY)
        
        erosion = []
        if(isMat):
            #remove horizontal line
            rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 9))
            erosion = cv.erode(thresh1,rect_kernel, iterations = 1)
            #print('header')
        else:
            #print('not header')
            erosion = thresh1
        #Extend region Text
        dillation_kernel = cv.getStructuringElement(cv.MORPH_RECT, (15, 15))
        dilation = cv.dilate(erosion, dillation_kernel, iterations = 2)
        
        #.imshow('img dilate',dilation)   
        #dilation = erosion
        #connection
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (9, 1))
        connected = cv.morphologyEx(dilation, cv.MORPH_CLOSE, kernel)
        
        #cv.imshow('img connect',connected)

        contours, hierarchy = cv.findContours(connected, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
        cnts_sort,_ = self.sort_contours(contours)
        ocrRead = ''
        count = 0
        for cnt in cnts_sort:
            x, y, w, h = cv.boundingRect(cnt)
            #rect = cv.rectangle(cv.cvtColor(imgRun,cv.COLOR_GRAY2BGR), (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv.imshow('rect',rect)
            cropped = imgRun[y:y + h, x:x + w]
            #cv.imshow('img read 2',cropped)
            mean = int(cropped.mean())
            _,inv = cv.threshold(cropped, mean, 255, cv.THRESH_OTSU)
            # #cv.imshow('img run',cropped)
           
            text = self.ReadOCR(inv)
            if(count>0):
                ocrRead += ' '
            ocrRead += text
        
            count+=1
        return ocrRead

    def run(self):
        recipeParam = self.recipeParam
        frame = self.frame
        sem = self.sem
        serverconfig = self.serverconfig
        config = self.config
        #global sem,serverconfig,config
        #sem.acquire()
        t1 = time.time()
        dataLineOCR = []
        dataQRcode = []
        strOCR = ''
        strQR = ''
        log = Logfile()
        if(recipeParam.UseOCRreader):
            for OCRROI in recipeParam.OCR_ROI:
                ocrroi = recipeParam.OCR_ROI[OCRROI]
                if(ocrroi.UseROI):
                    if(recipeParam.MachineModel == "TNF"):
                        imgcrop = self.CropROI(frame,ocrroi.ROI)
                        dataLineOCR.append(self.TNF_readerFunction(imgcrop))
                    else:
                        imgreadOCR = []
                        if(ImageMode(ocrroi.ImgMode) == ImageMode.Raw):
                            imgreadOCR = frame
                        elif(ImageMode(ocrroi.ImgMode) == ImageMode.Gray):
                            imgreadOCR = self.GrayImg(frame)
                        else:
                            imgreadOCR = self.EdgesDetect(frame)

                        imgcrop = self.CropROI(imgreadOCR,ocrroi.ROI)
                        ocrdata = self.ReadOCR(imgcrop)
                        if(ocrdata != None or ocrdata != ' 'or ocrdata != ''):
                            dataLineOCR.append(ocrdata)
                        else:
                            ocrdata = 'Cannot Read'
                            dataLineOCR.append(ocrdata)

        if(recipeParam.UseQRreader):
            for QRROI in recipeParam.QR_ROI:
                qrroi = recipeParam.QR_ROI[QRROI]
                if(qrroi.UseROI):
                    imgreadQR = []
                    if(ImageMode(qrroi.ImgMode) == ImageMode.Gray):
                        imgreadQR = self.GrayImg(frame)
                    else:
                        imgreadQR = frame
                    dataQR = self.QRcodeReader(self.CropROI(imgreadQR,qrroi.ROI))
                    if(dataQR is not None or dataQR != ' 'or dataQR != ''):
                        #if((qrroi.Comment != '') or (qrroi.Comment is not None)):
                        #    dataQR = qrroi.Comment +':'+ dataQR
                        dataQRcode.append(dataQR)
                        #strQR = dataQR+','
                    #add paintROI
        if(len(dataLineOCR) >0):
            strOCR = json.dumps(dataLineOCR)
        if(len(dataQRcode)>0):
            strQR = json.dumps(dataQRcode)

        if(strOCR!= ''):
            print("OCR data",strOCR)
            log.writelog('OCR : '+strOCR)
        if(strQR!= ''):
            print("QR data",strQR)
            log.writelog('QR : '+strQR)
        body = {
                    "MachineNo": config.MACHINE_NO,
                    "MachineModel": config.MACHINE_MODEL,
                    "Operation": config.OPERATION,
                    "DeviceID": config.DEVICE_ID,
                    "AlarmDetail": json.dumps({ 'OCR': strOCR, 'QR':strQR },indent=4)
               }
        RecordAlarm(serverconfig.Server,serverconfig.MQTTBroker,config.TOPIC_UPDATEDATA,body).start()
        t2 = time.time()
        #"{10:2f}".format(t2-t1)
        #print('ProcessTime : {8:.2f} ms\r\n'.format(t2-t1))
        print('Process Time := {0:.2f} S \r\n'.format(t2-t1))
        #sem.release()                                                                 
##############################################
onlinemode = False
cameracontrol = []
gloImgMat = []
lastTriggerState = False
triggerStateChange = False
##############################################

def adjust_brightness(img, value):
    num_channels = 1 if len(img.shape) < 3 else 1 if img.shape[-1] == 1 else 3
    img = cv.cvtColor(img, cv.COLOR_GRAY2BGR) if num_channels == 1 else img
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv)

    if value >= 0:
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
    else:
        value = int(-value)
        lim = 0 + value
        v[v < lim] = 0
        v[v >= lim] -= value

    final_hsv = cv.merge((h, s, v))

    img = cv.cvtColor(final_hsv, cv.COLOR_HSV2BGR)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY) if num_channels == 1 else img
    return img

def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))

def toRGB(image,gray=False):
    img = cv.cvtColor(np.array(image), cv.COLOR_BGR2RGB)
    if(gray):
        return cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    else:
        return img
    
def Zoom(cvObject, zoomSize):
    cvObject = imutils.resize(cvObject, width=(zoomSize * cvObject.shape[1]))
    center = (cvObject.shape[0]/2,cvObject.shape[1]/2)
    cropScale = (center[0]/zoomSize, center[1]/zoomSize)
    cvObject = cvObject[cropScale[0]:(center[0] + cropScale[0]), cropScale[1]:(center[1] + cropScale[1])]
    return cvObject

def intersection(a,b):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    w = min(a[0]+a[2], b[0]+b[2]) - x
    h = min(a[1]+a[3], b[1]+b[3]) - y
    if w<0 or h<0: 
        return (0,0,0,0) 
    return (x, y, w, h)

def intersectionPercent(a,b):
    res = intersection(a,b)
    if(res[0] == 0 or res[1] == 0 or res[2] == 0 or res[3] == 0):
        return 0
    return((res[2]*res[3])/(a[2]*a[3]))

def base64str2cvimg(base64_string,gray=False):
    return toRGB(stringToImage(base64_string),gray)

def connectMqtt():
    global serverconfig,mqtt_client
    port = 1883
    Server_ip = serverconfig.MQTTBroker
    mqtt_client.on_connect = onConnectedMqtt
    mqtt_client.on_message = onMessageMqtt
    mqtt_client.connect(Server_ip, port)
    mqtt_client.loop_start()
    #mqtt_client.loop_forever()

def disconnectMQTT():
    global mqtt_client
    publicStatus('Disconnect MQTT')
    try:
        mqtt_client.disconnect()
        mqtt_client.loop_stop()
    except:
        pass

def onConnectedMqtt(self, client, userdata, rc):
    global config,mutex
    mutex.acquire()
    global MqttConnected
    MqttConnected = True
    mutex.release()
    subscribe = [(config.TOPIC_UPDATERECIPE,2),(config.TOPIC_REBOOT,2),(config.TOPIC_SUB_TAKEPICTURE,2),(config.TOPIC_MidnightAlarmClock,2)]
    self.subscribe(subscribe)

def onMessageMqtt(client, userdata,msg):
    global pauseProcess,config,mutex,ReqTakePicture,ReqReboot
    mutex.acquire()
    pauseProcess = True
    mutex.release()
    try:
        msgstr = msg.payload.decode("utf-8")
        print(msg.topic)
        if(msg.topic == config.TOPIC_UPDATERECIPE):
            time.sleep(3)
            loadRecipe(msgstr)
            try:
                cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, recipeParam.FrameWidth)
                cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, recipeParam.FrameHeight)
            except:
                cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
                cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
            time.sleep(0.01)
        elif(msg.topic == config.TOPIC_SUB_TAKEPICTURE):
            time.sleep(3)
            mutex.acquire()
            ReqTakePicture = True
            mutex.release()
        elif(msg.topic == config.TOPIC_MidnightAlarmClock):
            mutex.acquire()
            log = Logfile()
            log.writelog('   ')
            mutex.release()
        elif(msg.topic == config.TOPIC_REBOOT):
            time.sleep(3)
            mutex.acquire()
            ReqReboot = True
            mutex.release()
            #
    except:
        pass


    mutex.acquire()
    pauseProcess = False
    mutex.release()

def publicImage(cvimg):
    global config,serverconfig,mqtt_client
    try:
        print('Publish img')
        publicStatus('Start Publish Img')
        retval, buffer = cv.imencode('.jpg', cvimg)
        imgstr = str(base64.b64encode(buffer),'utf-8')
        mqtt_client.publish(config.TOPIC_PUB_TAKEPICTURE,json.dumps({'image': imgstr }),qos=2)
        publicStatus('Published')
    except: 
        publicStatus('Publish Image error')
        pass

def publicStatus(strstatus):
    global config,serverconfig,lastpublishStatus,mqtt_client
    if(lastpublishStatus == strstatus):
        return
    else:
        lastpublishStatus = strstatus
    try:
        mqtt_client.publish(config.TOPIC_UPDATESTATUS ,json.dumps({ 'status': strstatus }),qos=0)
    except: 
        pass

def publicReboot():
    global config,serverconfig,mqtt_client
    try:
        mqtt_client.publish(config.TOPIC_REBOOT,'Reboot',qos=0)
    except: 
        pass

 
def loadRecipe(str_recipe):
    global recipeParam,serverconfig,gloImgMat,lastRecipe,config,recipeOK,mutex
    if(str_recipe == ''):
        mutex.acquire()
        recipeOK = False
        mutex.release()
        return False
    publicStatus('Check recipe in server.')
    if(recipeParam.checkRecipeInserver(serverconfig.Server,str_recipe) == False):
        publicStatus('Not Found recipe in server.')
        mutex.acquire()
        recipeOK = False
        mutex.release()
        return False
    publicStatus('Loading recipe '+str_recipe)
    try:
        recipeParam.load(serverconfig.Server,str_recipe)
        print('Recipe loaded := ',str_recipe)
        publicStatus('Loaded recipe '+str_recipe)
        lastRecipe.save(serverconfig.Server,config.DEVICE_ID,str_recipe)
        gloImgMat = base64str2cvimg(recipeParam.Matching_ROI.base64img,True)
        mutex.acquire()
        recipeOK = True
        mutex.release()
        return True
    except:
        print('load Recipe Error') 
        mutex.acquire()
        recipeOK = False
        mutex.release()
        publicStatus('Load recipe '+str_recipe+' Error !!!')
        lastrec = lastRecipe.load(serverconfig.Server,config.DEVICE_ID)
        return loadRecipe(lastrec)

def OpenCamera():
    global Cameraindex,countTrytoConnect,maxTrytoConnect
    path = r'C:\Users\41394642\Desktop\fastapiConnectVPDdatabase(Mysql)\alarmQR2.mp4'
    return cv.VideoCapture(Cameraindex)  # ('/home/vpd/Desktop/VPD/alarm1.mp4')

def CloseCamera(camera):
    camera.release()
    publicStatus('Close Camera.')

def DrawRectangle(frame3, R1, C1, R2, C2):
    start_point = (C1, R1)
    end_point = (C2, R2)
    color = (0, 255, 0)
    thickness = 3
    return cv.rectangle(cv.cvtColor(frame3, cv.COLOR_GRAY2BGR), start_point, end_point, color, thickness)

def GPIOInput():
    if(hardwareCon):
        GPIO.setmode(GPIO.BOARD) 
        GPIO.setup(7, GPIO.IN)
        GPIO.setup(13,GPIO.IN)
        GPIO.setup(15,GPIO.IN)
        GPIO.setup(29,GPIO.IN)
        while start_loop_gpio:
            IO1 = GPIO.input(7)
            IO2 = GPIO.input(13)
            IO3 = GPIO.input(15)
            IO4 = GPIO.input(29)

def FindMatching(imagefind,imageMat):
    try:
         #w, h = imageMat.shape[::-1]
        res = cv.matchTemplate(cv.cvtColor(imagefind,cv.COLOR_BGR2GRAY), imageMat, cv.TM_CCOEFF_NORMED)
        treshole = 0.9
        #cv.imshow('imgMat',imageMat)
        #cv.imshow('imgFind',imagefind)
        loc = np.where(res >= treshole)
        #print(loc)
        for pt in zip(*loc[::-1]):
            #print(pt)
            if len(pt) == 2:
                #print('Is matching')
                #cv.imshow('imgMat',cv.rectangle(imagefind, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 3))
                #cv.waitKey(0)
                return True #cv.rectangle(imagefind, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 3)
        return False
    except:
        return False

def gettriggerSignal(img = None):
    global lastTriggerState,triggerStateChange,gloImgMat,recipeParam
    if(recipeParam.TriggerSource == Trigger.IO):
        #readIOstatus
        if(lastTriggerState != True):
            triggerStateChange = True
            lastTriggerState = True
        return True
    else:
        if(img is None):
            return False
        foundmat = False
        if(recipeParam.Matching_ROI.UseROI):
            foundmat = FindMatching(Proc().CropROI(img,recipeParam.Matching_ROI.ROI),gloImgMat)
            if(lastTriggerState != foundmat):
                triggerStateChange = True
                lastTriggerState = foundmat
                #print('Screen has changed.')
            else:
                triggerStateChange = False
                #print('Same last screen.')
        return foundmat

def DisconnectAll():
    global cameracontrol
    try:
        CloseCamera(cameracontrol)
    except:
        pass
    disconnectMQTT()

def ResetAllUSB():
    #Pi4
    #os.popen("sudo -S %s"%('uhubctl -l 2 -a 2'), 'w').write('vpd\n')
    
    #JetSon
    os.popen("sudo -S %s"%('uhubctl -l 2-1 -a 2'), 'w').write('vpd\n')
    print('              \r\n')
    time.sleep(25)

def CheckImageShift(cam,img,ROI):
    try:
        global cameracontrol,recipeParam
        try:
            cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, recipeParam.FrameWidth)
            cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, recipeParam.FrameHeight)
        except:
            pass
        gray_frame = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        Row1 = ROI.Row1
        Col1 = ROI.Col1
        Row2 = ROI.Row2
        Col2 = ROI.Col2
        Width = Col2-Col1
        Height = Row2-Row1
        AreaMain = Width*Height
        crop = Proc().CropROI(gray_frame,ROI)#gray_frame[Row1:Row2,Col1:Col2]
        _, thresh = cv.threshold(crop, 6, 255, cv.THRESH_BINARY)
        x1,y1,w1,h1 = cv.boundingRect(thresh)
        AreaThis = w1*h1
        AreaPercent = (AreaThis/AreaMain) * 100.00
        if (AreaPercent <95 and AreaPercent >70):
            current_time = datetime.datetime.now()
            fname = '/home/vpdpi/Desktop/ImageAlarm/'+str(current_time.year)+'_'+str(current_time.month)+'_'+str(current_time.day)+'_'+str(current_time.hour)+'_'+str(current_time.minute)+'_'+str(current_time.second)+'.jpg'
            cv.imwrite(fname, img)
            publicStatus('Image Shift.')
            CloseCamera(cameracontrol)
            ResetAllUSB()
            try:
                cameracontrol = OpenCamera()
                try:
                    cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, recipeParam.FrameWidth)
                    cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, recipeParam.FrameHeight)
                except:
                    pass
            except:
                pass
        elif(AreaPercent<70):
            publicStatus('No Input Signal.')
            current_time = datetime.datetime.now()
            fname = '/home/vpdpi/Desktop/ImageAlarm/'+str(current_time.year)+'_'+str(current_time.month)+'_'+str(current_time.day)+'_'+str(current_time.hour)+'_'+str(current_time.minute)+'_'+str(current_time.second)+'.jpg'
            cv.imwrite(fname, img)
        else:
            pass
    except:
        pass

    
def startProcess():
    global cameracontrol,triggerStateChange,pauseProcess,recipeParam,ProcThread,sem,ReqTakePicture,ReqReboot,serverconfig,config,Cameraindex,countTrytoConnect,maxTrytoConnect,TNFimg 
    reqStopProcess = False
    if(recipeParam is None):
        DisconnectAll()
        print('Not Found Recipe')
        return
    try:
        cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, recipeParam.FrameWidth)
        cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, recipeParam.FrameHeight)
    except:
        cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    countReconnect = 0
    loc_pauseProcess = False
    loc_takepicture = False
    
    counterImgShift = 0
    maxImgCheckShift = 100
    t1Status = time.time()
    t2Status = time.time()
    count_recon = 0
    while(reqStopProcess == False):
        mutex.acquire()
        t2Status = time.time()
        if((t2Status -t1Status) >= 60.0):
            t1Status = time.time()
            #print('Online.')
            publicStatus('Online.')
        if(pauseProcess):
            loc_pauseProcess = True
        else:
            loc_pauseProcess = False
        
        if(ReqTakePicture):
            loc_takepicture = True
            ReqTakePicture = False
        if(ReqReboot):
            reqStopProcess = True
        mutex.release()
        if(reqStopProcess):
            print('Force Stop')
            DisconnectAll()
            break
        ret, frame = [],[]
        if(loc_pauseProcess == False):
            ret, frame = cameracontrol.read()
            if(counterImgShift >= maxImgCheckShift):
                CheckImageShift(cameracontrol,frame,recipeParam.DispPosition)
                counterImgShift = 0
                ret, frame = cameracontrol.read()
            else:
                counterImgShift+=1
            #frame = adjust_brightness(frame, serverconfig.Brightness)
        if(loc_pauseProcess):
            print('Pause Process')
            publicStatus('Pause Process.')
            time.sleep(2)
        elif(ret):
            
            publicStatus('Running.')
            if(loc_takepicture):
                publicStatus('Take Picture.')
                publicImage(frame)
                loc_takepicture = False
            countReconnect = 0
            #, (int(1920/2), int(1080/2) cv.resize(
            #cvtgray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
            #cv.imshow('crop',frame) #cv.resize(frame, (int(1920/2), int(1080/2)))
            #cv.resizeWindow('crop',1000, 724)
            #cv.waitKey(1)
            #print('I m here')
            if(gettriggerSignal(frame)):
                #print('is matching')
                if(triggerStateChange):
                    publicStatus('Alarm !!!')
                    print('State Change')
                    time.sleep(recipeParam.Delay)
                    ret, frame = cameracontrol.read()
                    #current_time = datetime.datetime.now()
                    #fname = '/home/vpdpi/Desktop/ImageAlarm/'+str(current_time.year)+'_'+str(current_time.month)+'_'+str(current_time.day)+'_'+str(current_time.hour)+'_'+str(current_time.minute)+'_'+str(current_time.second)+'.jpg'
                    #cv.imwrite(fname, frame)
                    #sem.acquire()
                    #ProcThread = Thread(target=Proc().run,args=(recipeParam,frame,))
                    #ProcThread.start()
                    processing = Proc(recipeParam,frame,sem,serverconfig,config,TNFimg)
                    processing.run()
        else:
            countReconnect +=1
            if(count_recon>countTrytoConnect):
                count_recon = 0
                Cameraindex = Cameraindex+1
            if(Cameraindex>maxTrytoConnect):
                Cameraindex = 0
                ResetAllUSB()
            if(countReconnect >120):
                publicReboot()
                Cameraindex = 0
            try:
                cv.destroyAllWindows()
            except:
                pass 
            print('Camera Error try to reconnect ', countReconnect)
            publicStatus('Reconnect Camera :.;lp0- '+str(countReconnect))
            try:
                CloseCamera(cameracontrol)
            except:
                print('Close camera error')
            try:
                cameracontrol = OpenCamera()
                ret, frame = cameracontrol.read()
                time.sleep(0.1)
                ret, frame = cameracontrol.read()
                time.sleep(0.1)
                try:
                    cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, recipeParam.FrameWidth)
                    cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, recipeParam.FrameHeight)
                except:
                    cameracontrol.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
                    cameracontrol.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
            except:
                print('Open camera error')
            time.sleep(2) 
            count_recon = count_recon+1
    reqstoploopprocess = False
    DisconnectAll()

def startupConnection():
    print("Program Startup")
    global cameracontrol,serverconfig,config,lastRecipe,mutex,recipeOK,pauseProcess,Cameraindex,countTrytoConnect,maxTrytoConnect
    config.load(serverconfig.Server)
    mqttconnected = False
    while(mqttconnected == False):
        connectMqtt()
        time.sleep(2)
        mutex.acquire()
        global MqttConnected
        mqttconnected = MqttConnected
        print("MQTT Connected. ",MqttConnected)
        mutex.release()
        if(mqttconnected == True):
            print("MQTT Connect complete.")
            break
        else:
            print("Cannot Connect MQTT.")
            time.sleep(0.5)
        print("MQTT try to re connected.") 
    cameraconnected = False

    publicStatus('Camera Connecting.')
    count_recon = 0
    while(cameraconnected == False):
        ret = False
        frame = []
        if(count_recon>countTrytoConnect):
            count_recon = 0
            Cameraindex = Cameraindex+1
        if(Cameraindex>maxTrytoConnect):
            ResetAllUSB()
            Cameraindex = 0
        try:
            cameracontrol = OpenCamera()
            time.sleep(0.5)
            ret, frame = cameracontrol.read()
        except:
            pass

        if(ret):
            publicStatus('Camera Connected.')
            print("Camera Connected.")
            cameraconnected = True
            break
        else:
            print("Cannot Connect Camera.")
            try:
                CloseCamera(cameracontrol)
            except:
                pass
            time.sleep(0.5)
        count_recon = count_recon+1
    
    lastRecipe.load(serverconfig.Server,config.DEVICE_ID) 
    loadRecipe(lastRecipe.LastRecipe)
    while(True):
        mutex.acquire()
        recok = recipeOK
        pause = pauseProcess
        mutex.release()
        if(pause == False):
            if(recok):
                break
            else:
                print('Recipe error waitting for re-load Recipe 5 Sec.')
                publicStatus('Recipe error waitting for re-load Recipe 5 Sec.')
                time.sleep(5)
    startProcess()
    
TNFimg = np.array(stringToImage(base64tnfImg))
ResetAllUSB()
startupConnection()
