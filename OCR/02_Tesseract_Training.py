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

# 파일쌍
# 이미지.png
# 이미지.gt.txt


