import cv2

img = cv2.imread("lena.jpg")
canny = cv2.Canny(img, 100, 100)

cv2.imshow("normal Image", img)
cv2.imshow("blur Image", canny)
cv2.waitKey(0)
