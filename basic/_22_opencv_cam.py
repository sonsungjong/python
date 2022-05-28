import cv2

vc = cv2.VideoCapture(0)            # 0, 1, -1, 2 캠ID
vc.set(3, 640)          # 가로
vc.set(4, 480)          # 세로
# vc.set(10, 100)           # 밝기

while True:
    success, img = vc.read()
    if success:
        cv2.imshow("Cam", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

