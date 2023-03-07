from cv2 import cv2



#Create tracker object



cap = cv2.VideoCapture("Zebrafish1.avi")

object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)

while True:
    ret, frame = cap.read()
    height, width, _= frame.shape
    print(height,width) #frame size

    #Extract Region of Interest
    roi = frame[300:700,200:400]






    mask = object_detector.apply(frame)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)#this is for destroy shadow it may be not necessary

    contours, _ =cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        #burdad küçük alanlaru çıkartacağız
        area = cv2.contourArea(cnt)
        if area>100:
            #cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),3)





    #cv2.imshow("ROI", roi)
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    key = cv2.waitKey(30)
    if key == 27:
        break
cap.release()
if __name__ == '__main__':
    cv2.destroyAllWindows()
