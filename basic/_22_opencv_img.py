import cv2

img = cv2.imread("lena.jpg")

cv2.imshow("Output", img)
cv2.waitKey(0)

# 이미지
# pip install python-opencv