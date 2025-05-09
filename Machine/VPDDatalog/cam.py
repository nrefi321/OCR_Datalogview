import cv2 

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
while(True):
    ret, frame = cap.read()
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #cv2.imshow('frame_gray',gray)
    cv2.imshow('frame_bgr',frame)
    #print(frame.shape)
    #cv2.imwrite('/home/vpd/Desktop/1.jpg', frame)
    #break
    # Check press key == q -> break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()