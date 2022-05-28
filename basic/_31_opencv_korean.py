import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image

def myText(src, text, pos, font_size, font_color):
    img_pil = Image.fromarray(src)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype('fonts/gulim.ttc', font_size)
    draw.text(pos, text, font=font, fill=font_color)
    return np.array(img_pil)

#img = np.zeros((480, 640, 3), dtype= np.uint8)
img = cv2.imread('bb.jpg')
FONT_SIZE = 30
COLOR = (255,255,255)

img = myText(img, "한글입력", (20, 50), FONT_SIZE, COLOR)

cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()