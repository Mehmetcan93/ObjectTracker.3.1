import cv2
import time
import numpy as np

cv2.namedWindow("video")

cap = cv2.VideoCapture("Zebrafish2.avi")

time.sleep(3)
cap.set(3, 640)
cap.set(4, 480)

while cv2.waitKey(1)!= 30:
    flag, frame = cap.read()
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv2.imshow("video", frame)
print(width)
print(height)
cap.release()
cv2.destroyAllWindows()