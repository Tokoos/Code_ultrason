import RPi.GPIO as GPIO
import time

from gtts import gTTS
import cv2
import os
import time

thres = 0.45 
nms = 0.2


def speak(text):
    tts = gTTS(text=text, lang='fr', slow=False)
    tts.save('output.mp3')
    os.system('mpg321 output.mp3')


classNames = []
classFile = "/home/canne/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/canne/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/canne/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

# Charger le modèle de détection d'objet
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def getObjects(img, objects=[]):
    # Détecter les objets dans l'image
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    objectInfo =[]
    
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            
            if className in objects:
                objectInfo.append([box,className])
                
                # Annoncer vocalement le nom de l'objet détecté
                objectName = classNames[classId - 1]
                
                cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    return img,objectInfo


def activeCamera():
    cap = cv2.VideoCapture(0)
    cap.set(640,3)
    cap.set(480,4)
    #cap.set(10,70)
    
    objects_to_announce =  ["chaise", "personne", "mur", "table", "Telephorn"]

    while True:
        success, img = cap.read()
        result,objectInfo = getObjects(img,objects=objects_to_announce)
        print(objectInfo)
        objectInfo = objectInfo[:1]
        
        for obj in objectInfo:
            objectName = obj[1]
            if objectName.endswith("e"):
                speak(f"Papa roger, Une {objectName} est en face de vous")
            else:
                speak(f"papa roger, un {objectName} est passée devant vous !")
                
            time.sleep(0.2)
            speak(f"vous pouvez dévier en faisant 2 pas vers la gauche")
            time.sleep(2)
        break
        
        cv2.imshow("Output",img)
        cv2.waitKey(1)
        
def activeCamera2():
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    #cap.set(10,70)
    
    objects_to_announce =  ["chaise", "personne", "mur", "table"]

    while True:
        success, img = cap.read()
        # Détecter les objets prioritaires dans l'image
        #result, objectInfo = getObjects(img,0.45,0.2, objects=objects_to_announce)
        result,objectInfo = getObjects(img,objects=objects_to_announce)
        print(objectInfo)
        objectInfo = objectInfo[:1]
        
        for obj in objectInfo:
            objectName = obj[1]
            if objectName.endswith("e"):
                speak(f"Papa roger, Une {objectName} est passée devant vous !")
            else:
                speak(f"papa roger, un {objectName} est passée devant vous !")
                
            time.sleep(0.2)
            speak(f"faites attention")
            time.sleep(2)
        break
         
        cv2.imshow("Output",img)
        cv2.waitKey(1)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = 23
ECHO = 24
BUZZER = 25
capteur = 14

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(capteur, GPIO.IN)

GPIO.output(TRIG, False)
GPIO.output(BUZZER, False)

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17165
    distance = round(distance, 1)
    return distance

def sound_buzzer():
    GPIO.output(BUZZER, True)
    time.sleep(0.5)
    GPIO.output(BUZZER, False)
    time.sleep(0.5)

try:
    print('Measuring distance...')
    while True:
        distance = measure_distance()
        print('Distance:', distance, 'cm')
        
        if GPIO.input(capteur):
            sound_buzzer()
            print('mouvement detected!')
            try :
                #Vérification
                cap = cv2.VideoCapture(0)
                cap.set(3,640)
                cap.set(4,480)
                activeCamera2()
            except Exception as e :
                print(e)

        if distance <= 180:
            print('Obstacle detected!')
            sound_buzzer()
            try :
                cap = cv2.VideoCapture(0)
                cap.set(3,640)
                cap.set(4,480)
                activeCamera()
            except Exception as e :
                print(e)

        time.sleep(1)

except KeyboardInterrupt:
    print('Measurement stopped by user')
finally:
    GPIO.cleanup()
