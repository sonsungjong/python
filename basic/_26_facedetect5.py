import cv2
# pip install opencv-python
# pip install python-opencv
import mediapipe as mp
# pip install mediapipe

class FaceDetector():
    def __init__(self, minDetectionCon= 0.5):
        self.minDetectionCon = minDetectionCon
        self.mpFaceDetection = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetection = self.mpFaceDetection.FaceDetection(self.minDetectionCon)

    def findFaces(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.faceDetection.process(imgRGB)
        #print(self.results)
        bboxs = []
        if self.results.detections:
            for id, detection in enumerate(self.results.detections):
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                    int(bboxC.width * iw), int(bboxC.height * ih)

                bboxs.append([id, bbox, detection.score])

                if draw:
                    img = self.fancyDraw(img, bbox)
                    #cv2.rectangle(img, bbox, (255,0,255),2)
                    cv2.putText(img, f'{int(detection.score[0]*100)}%',
                (bbox[0], bbox[1]-20),cv2.FONT_HERSHEY_PLAIN, 2, (255, 0,255), 2)
        return img, bboxs
    
    def fancyDraw(self, img, bbox, l=30, t=5, rt=1):
        x, y, w, h = bbox
        x1, y1 = x+w, y+h
        cv2.rectangle(img, bbox, (255, 0, 255), rt)
        # Top Left (x,y)
        cv2.line(img, (x,y), (x+l,y), (255,0,255), t)
        cv2.line(img, (x,y), (x,y+l), (255,0,255), t)
        # Top Right (x1,y)
        cv2.line(img, (x1,y), (x1-l,y), (255,0,255), t)
        cv2.line(img, (x1,y), (x1,y+l), (255,0,255), t)
        # Bottom Left (x,y1)
        cv2.line(img, (x,y1), (x+l,y1), (255,0,255), t)
        cv2.line(img, (x,y1), (x,y1-l), (255,0,255), t)
        # Bottom Right (x1,y1)
        cv2.line(img, (x1,y1), (x1-l,y1), (255,0,255), t)
        cv2.line(img, (x1,y1), (x1,y1-l), (255,0,255), t)
        return img

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)          # 가로
    cap.set(4, 480)          # 세로
    detector = FaceDetector()

    # 코덱 설정
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    width = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 저장 파일명, 코덱, FPS, 크기(width, height)
    out = cv2.VideoWriter("mycam.mp4", fourcc, fps, (width,height))
    
    while True:
        success, img = cap.read()
        if success:
            img, bboxs = detector.findFaces(img)
            
            out.write(img)
            cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()