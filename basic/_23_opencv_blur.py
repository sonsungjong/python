import cv2

img = cv2.imread("lena.jpg")
blur = cv2.GaussianBlur(img, (7,7), 0)

cv2.imshow("normal Image", img)
cv2.imshow("blur Image", blur)
cv2.waitKey(0)
