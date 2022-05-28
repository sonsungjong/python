import cv2

vc = cv2.VideoCapture("foreman.mp4")

while True:
    success, img = vc.read()
    if success:
        cv2.imshow("Video", img)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# 동영상