import cv2

동영상 = cv2.VideoCapture('video.mp4')
# 동영상 = cv2.VideoCapture(0)            # -1 ~ 2, 거의 0 또는 1

while True:
    성공, 프레임 = 동영상.read()
    if 성공:
        cv2.imshow("my video", 프레임)
    if cv2.waitKey(20) & 0xFF == 27:            # 27은 ESC키(종료)
        break
