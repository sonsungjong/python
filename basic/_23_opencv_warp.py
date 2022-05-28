import cv2
import numpy as np

w = 250
h = 350
img = cv2.imread("lena.jpg")

src = np.array([[215,181],[372,181],[215,400],[372,400]], dtype=np.float32)
dst = np.array([[0,0],[w,0],[0,h],[w,h]], dtype=np.float32)
matrix = cv2.getPerspectiveTransform(src, dst)
imgWarp = cv2.warpPerspective(img, matrix, (w,h))

cv2.imshow("normal Image", img)             # 원본
cv2.imshow("img Warp", imgWarp)          # 리사이즈
cv2.waitKey(0)
cv2.destroyAllWindows()