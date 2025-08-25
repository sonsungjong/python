# text recognition in images

# https://pypi.org/project/pytesseract/

# sudo apt install tesseract-ocr    # ubuntu
# sudo apt install tesseract-ocr-kor

# https://github.com/UB-Mannheim/tesseract/releases    # windows + PATH
# 시스템 환경변수에 C:\Program Files\Tesseract-OCR 추가

# pip install pytesseract


# 언어 추가 설치

# !apt-get install tesseract-ocr-kor
# !apt-get install tesseract-ocr-eng
# !apt-get install tesseract-ocr-por

# Tesseract OCR에서 한국어(kor) 인식 기능을 사용하려면, 이 언어 데이터 파일(kor.traineddata)이 반드시 필요합니다.
# https://github.com/tesseract-ocr/tessdata/tree/main

# 리눅스에서 파일을 인터넷에서 다운로드할 때 사용하는 명령어 wget 
# !wget -O ./tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata?raw=true
# !wget -O ./tessdata/kor.traineddata https://github.com/tesseract-ocr/tessdata/blob/main/kor.traineddata?raw=true
# !wget -O ./tessdata/kor_vert.traineddata https://github.com/tesseract-ocr/tessdata/blob/main/kor_vert.traineddata?raw=true
# !wget -O ./tessdata/por.traineddata https://github.com/tesseract-ocr/tessdata/blob/main/por.traineddata?raw=true


import os
import pytesseract      # pip install pytesseract
import numpy as np
import cv2          # pip install opencv-python
import matplotlib.pyplot as plt
from PIL import ImageFont, ImageDraw, Image, ImageOps
import re
from math import atan2, degrees

WORDS_PATH = "./words.txt"
PATTERNS_PATH = "./patterns.txt"
TESSDATA_DIR = 'tessdata'

img = Image.open('./quotation_line/1월 건물관리비, 건물임차료^0005.png')
img_cv = np.array(img)
increase = cv2.resize(img_cv, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_CUBIC)
gray = cv2.cvtColor(increase, cv2.COLOR_RGB2GRAY)
bg = cv2.medianBlur(gray, 35)
norm = cv2.divide(gray, bg, scale=255)
norm = cv2.convertScaleAbs(norm, alpha=1.4, beta=0)
bin_img = cv2.adaptiveThreshold(norm, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 12)
bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, np.ones((1,1), np.uint8), iterations=1)


# -------- config --------
cfg_h = rf'''--oem 1 --psm 6 -l eng+kor
--user-words "{WORDS_PATH}" 
--user-patterns "{PATTERNS_PATH}" 
--tessdata-dir tessdata 
'''

cfg_v = rf'''--oem 1 --psm 5 -l eng+kor_vert
--user-words "{WORDS_PATH}" 
--user-patterns "{PATTERNS_PATH}" 
--tessdata-dir tessdata 
-c user_defined_dpi=350 
-c preserve_interword_spaces=1 
-c load_system_dawg=F 
-c load_freq_dawg=F
'''
cfg_num = r'''--oem 1 --psm 7 -l eng 
-c tessedit_char_whitelist=0123456789,.-
--tessdata-dir tessdata
'''

# -------- 본문 OCR (수평/세로 둘 다 시도) --------
txt_h = pytesseract.image_to_string(bin_img, config=cfg_h)
# txt_v = pytesseract.image_to_string(bin_img, config=cfg_v)
# txt_num = pytesseract.image_to_string(bin_img, config=cfg_num)

print(txt_h)
# print(txt_v)
# print(txt_num)

# -------- 키워드 주변 숫자 추출 --------
# data = pytesseract.image_to_data(bin_img, config=CFG_H6, output_type=Output.DICT)
# fields = {"공급가액": None, "세액": None, "합계": None}
# label_map = {
#     "공급가액": {"공급가액", "공급가"},
#     "세액": {"세액", "부가세"},
#     "합계": {"합계", "합계금액", "총액"}
# }
# H, W = bin_img.shape[:2]
# NUM_RE = re.compile(r'[₩]?\s*\d{1,3}(?:,\d{3})+(?:\.\d+)?')

# for i, word in enumerate(data["text"]):
#     if not word or data["conf"][i] == '-1':
#         continue
#     x,y,w,h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
#     for key, aliases in label_map.items():
#         if word.strip() in aliases and fields[key] is None:
#             # 오른쪽/아래 영역 잘라서 숫자 전용 OCR
#             rx1, ry1 = min(x+w+5, W-1), max(y-5, 0)
#             rx2, ry2 = min(x+w+200, W-1), min(y+h+30, H-1)
#             roi_r = bin_img[ry1:ry2, rx1:rx2]

#             bx1, by1 = max(x-10,0), min(y+h+3, H-1)
#             bx2, by2 = min(x+w+200, W-1), min(y+h+60, H-1)
#             roi_b = bin_img[by1:by2, bx1:bx2]

#             for roi in [roi_r, roi_b]:
#                 if roi.size == 0:
#                     continue
#                 cand = []
#                 t1 = pytesseract.image_to_string(roi, config=CFG_H6)
#                 t2 = pytesseract.image_to_string(roi, config=CFG_V5)
#                 t3 = pytesseract.image_to_string(roi, config=CFG_NUM)
#                 for t in [t1,t2,t3]:
#                     m = NUM_RE.search(t)
#                     if m:
#                         cand.append(m.group(0))
#                 if cand:
#                     fields[key] = max(cand, key=len).replace(" ","")

# print("=== FIELDS ===")
# print(fields)