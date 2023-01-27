import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np
# pip install pyinstaller
# pyinstaller -w -F --icon="myico.ico" "opencv3.py"

def hangulText(image, text, pos, size, color):
    img_pil = Image.fromarray(image)        # 이미지를 np리스트형태로 만든다
    img_draw = ImageDraw.Draw(img_pil)          # 그림을 그릴 공간 지정
    font = ImageFont.truetype('GULIM.TTC', size)        # 폰트와 사이즈 설정
    img_draw.text(pos, text, font=font, fill=color)     # 글자 그리기
    return np.array(img_pil)

width = 200
height = 300
origin_pos = np.array([ [137,157], [297, 128], [204, 347], [378, 308] ], dtype=np.float32)
change_pos = np.array([ [0,0], [width,0], [0, height], [width, height] ], dtype=np.float32)
matrix = cv2.getPerspectiveTransform(origin_pos, change_pos)

img = cv2.imread('card.jpg')            # 이미지 읽기
img_change = cv2.warpPerspective(img, matrix, (width, height))

img_change = hangulText(img_change, "손성종", (10, 10), 30, (255,0,255))

cv2.imshow("origin image", img)             # 원본 이미지 보여주기
cv2.imshow("change image", img_change)      # 자른 이미지 보여주기
cv2.waitKey(0)                          # 무한대기

# 137, 157     왼쪽위
# 297, 128    오른쪽위
# 204, 347    왼쪽아래
# 378, 308    오른쪽아래