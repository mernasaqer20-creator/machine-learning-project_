import cv2
import mediapipe as mp
from cvzone.SerialModule import SerialObject
import serial

arduino = SerialObject('COM7')
bluetooth=serial.Serial("COM9", 115200)
bluetooth.flushInput()
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands #getting the values of these different points or landmarks
hands = mpHands.Hands() #this object uses only RGB imgs 
mpDraw = mp.solutions.drawing_utils # this will automatically draw the 21 points instesd if us 
tipIds = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # converting img from BGR to RGB
    results = hands.process(imgRGB) # Getting the result after converting to RGB
    #print(results.multi_hand_landmarks)
    lmList = []
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                #print(id,lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                #print (id,cx,cy)
                lmList.append([id, cx, cy])
               # if id == 4:
               #     cv2.circle(img, (cx,cy), 20, (0,255,255), -1)
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS) #this draw a lines between the points 
    
    if len(lmList) != 0:
        fingers = []

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            print("thump up")
            arduino.sendData([1])
        else:
            print("thump down")
            arduino.sendData([2])
        
        if lmList[tipIds[1]][2] < lmList[tipIds[1] - 2][2]:
            print("index Up")
            arduino.sendData([3])
        else:
            print("index down")
            arduino.sendData([4])

        if lmList[tipIds[2]][2] < lmList[tipIds[2] - 2][2]:
            print("middle Up")
            arduino.sendData([5])
        else:
            print("middle down")
            arduino.sendData([6])
        
        if lmList[tipIds[3]][2] < lmList[tipIds[3] - 2][2]:
            print("ring Up")
            arduino.sendData([7])
        else:
            print("ring down")
            arduino.sendData([8])

        if lmList[tipIds[4]][2] < lmList[tipIds[4] - 2][2]:
            print("pinky Up")
            arduino.sendData([9])
        else:
            print("pinky down")
            arduino.sendData([10])


    cv2.imshow("robot hand", img)
    if cv2.waitKey(1) == ord('q'):
        break
    