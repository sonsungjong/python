# ffplay -f video4linux2 -input_format mjpeg -video_size 1920x1080 /dev/video0

# MJPG 로 설정해줘야 30fps 가능

import cv2

cap = cv2.VideoCapture(0)

# MJPG 강제 설정
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', "J", "P", "G"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

window_name = "DGX Webcam (MJPG)"

print(F"FPS 설정: {cap.get(cv2.CAP_PROP_FPS)}")

while True:
    ret, frame = cap.read()
    if not ret:
        print("no carera... not ret")
        break

    cv2.imshow(window_name, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('end')
        break

    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        print('end by X button')
        break


cap.release()
cv2.destroyAllWindows()
