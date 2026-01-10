# pip install python-opencv ultralytics
import cv2
from ultralytics import YOLO

# 1. Yolo 모델 불러오기
print("YOLO nano 모델 로드 중...")
model = YOLO('yolo11n.pt')

# 2. 카메라 설정
cap = cv2.VideoCapture(0)
'''
# 하드웨어 성능이 부족해서 최신프레임만 처리해야할 때
gst_input = (
    "v4l2src device=/dev/video0 ! "
    "video/x-raw, width=1920, height=1080, framerate=30/1 ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! "
    "appsink drop=true max-buffers=1 sync=false"
)

# 숫자 0 대신 gst_input 사용
cap = cv2.VideoCapture(gst_input, cv2.CAP_GSTREAMER)
'''

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
window_name = "YOLOv11 Live Detection"

print("카메라 시작")

while True:
    ret, frame = cap.read()
    if not ret:
        print("no camera... not ret")
        break

    # 3. YOLO 물체 찾기 (추론)
    # conf=0.6 : 신뢰도가 60% 이상인 것만 표시
    results = model(frame, conf=0.6, verbose=False)

    # 4. 감지된 물체들을 변수 로 생성
    frame_results = []

    # 감지되었을때만 실행
    if results[0].boxes:
        # 5. 감지된 물체 정보 얻기
        for box in results[0].boxes:
            # 6. 좌표 (x1, y1, x2, y2) 를 Tensor 에서 리스트로 바꿔서 저장
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # 7. 정확도
            conf = box.conf[0].item()

            # 8. 클래스 아이디와 이름
            cls_id = int(box.cls[0].item())
            name = results[0].names[cls_id]

            # 9. 정보를 딕셔너리 형태로 묶어서 리스트에 추가
            dic_detected_info = {
                "name": name,
                "conf": round(conf, 2),             # 보기 좋게 소수점 2자리로 반올림
                "coords": [round(x1,1), round(y1,1), round(x2,1), round(y2,1)]
            }
            frame_results.append(dic_detected_info)

        print(frame_results)


    # 10. 결과 화면에 그리기
    annotated_frame = results[0].plot()

    # 11. 화면 출력
    cv2.imshow(window_name, annotated_frame)

    # 종료 조건
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('end')
        break
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        print('end by X button')
        break

cap.release()
cv2.destroyAllWindows()




'''
# 카메라 -> HD-SDI -> SDI to USB 3.0 Capture Card -> Jetson(Yolo) -> 이더넷(UDP/RTSP프로토콜) -> UI프로그램
# 인코딩하여 RTSP 스트리밍으로 내보내기 (UDP통신)

# Jetson Orin Nano (CPU Encoding)
pipeline = "appsrc ! videoconvert ! x264enc tune=zerolatency ! rtspclientsink ..."

# Jetson Orin NX (GPU Encoding)
pipeline = "appsrc ! videoconvert ! nvv4l2h264enc ! rtspclientsink ..."
'''
