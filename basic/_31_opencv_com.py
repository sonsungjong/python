import cv2          # opencv 포함

# pixabay           무료이미지
# pexels            무료동영상

img = cv2.imread('bb.jpg')       # 해당 경로의 파일 읽어오기   
cv2.imshow('title', img)        # title이라는 이름으로 img를 표시
cv2.waitKey(0)              # 지정된 시간(ms)만큼 사용자 키 입력 대기
cv2.destroyAllWindows()

img_color = cv2.imread('bb.jpg', cv2.IMREAD_COLOR)     # 기본
img_gray = cv2.imread('bb.jpg', cv2.IMREAD_GRAYSCALE)      # 흑백
img_unchanged = cv2.imread('bb.jpg', cv2.IMREAD_UNCHANGED)     # 투명 영역까지 포함
cv2.imshow('img_color', img_color)
cv2.imshow('img_gray', img_gray)
cv2.imshow('img_unchanged', img_unchanged)

cv2.waitKey(0)
cv2.destroyAllWindows()

# ===============================

cap = cv2.VideoCapture('foreman.mp4')

while cap.isOpened():           # 동영상이 올바로 열렸는지?
    ret, frame = cap.read()     # ret : 성공 여부, frame : 받아온 이미지 (프레임)
    if not ret:
        print("프레임 끝")
        break
    cv2.imshow('video', frame)

    if cv2.waitKey(25) == 27:
        print("사용자 입력으로 종료")
        break

cap.release()           # 자원 해제
cv2.destroyAllWindows()     # 모든 창 닫기


# 이미지 저장
img = cv2.imread('bb.jpg', cv2.IMREAD_GRAYSCALE)
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

result = cv2.imwrite('img_save.jpg', img)
print(result)

# 동영상 저장
cap = cv2.VideoCapture('foreman.mp4')
# 코덱 정의
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
width = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# 저장 파일명, 코덱, FPS, 크기(width, height)
out = cv2.VideoWriter("output.avi", fourcc, fps, (width,height))

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    frame_resized = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    out.write(frame_resized)            # 영상데이터 저장(소리X)
    cv2.imshow('video', frame_resized)
    if cv2.waitKey(25) == ord('q'):
        break

out.release()       # 자원해제
cap.release()
cv2.destroyAllWindows()

img = cv2.imread('img.jpg')
dst = cv2.resize(img, (400, 500))   # width, height 크기조정
dst2 = cv2.resize(img, None, fx=0.5, fy=0.5)   # 비율로 조정

cv2.imshow('img', img)
cv2.imshow('resize', dst)
cv2.imshow('resize2', dst2)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 좌우대칭
img = cv2.imread('bb.jpg')
flip_horizontal = cv2.flip(img, 1)
cv2.imshow('img', img)
cv2.imshow('flip_horizontal', flip_horizontal)
cv2.waitKey(0)
cv2.destroyAllWindows()