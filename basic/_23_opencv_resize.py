import cv2

img = cv2.imread("lena.jpg")
resize = cv2.resize(img, (300, 300))
crop = img[0:300, 0:300]

cv2.imshow("normal Image", img)             # 원본
cv2.imshow("resize Image", resize)          # 리사이즈
cv2.imshow("crop Image", crop)              # 잘라내기
cv2.waitKey(0)
