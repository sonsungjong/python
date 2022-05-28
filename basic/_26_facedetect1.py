import cv2
import mediapipe as mp          # pip install mediapipe
import time

cap = cv2.VideoCapture("foreman.mp4")
pTime = 0

mpFaceDetection = mp.solutions.face_detection
mpDraw = mp.solutions.drawing_utils
faceDetection = mpFaceDetection.FaceDetection()


while True:
    success, img = cap.read()
    if success:
        # 미디어파이프
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = faceDetection.process(imgRGB)
        print(results)

        if results.detections:
            for id, detection in enumerate(results.detections):
                mpDraw.draw_detection(img,detection)
                #print(id, detection)
                #print(detection.score)
                #print(detection.location_data.relative_bounding_box)

        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS:{int(fps)}', (5,30),cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        cv2.imshow("Image", img)
    if cv2.waitKey(20) & 0xFF == 27:
            break