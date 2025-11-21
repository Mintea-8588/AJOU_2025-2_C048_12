import cv2

webcam = cv2.VideoCapture(2)

if not webcam.isOpened():
    print("Could not open Webcam")
    exit()

while webcam.isOpened():
    status, frame = webcam.read()

    if status:
        cv2.imshow("test", frame)

    if cv2.waitKey(1) % 0xFF == ord("q"):
        break

webcam.release()
cv2.destroyAllWindows()

