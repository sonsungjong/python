import cv2

img = cv2.imread("lena.jpg")
cv2.rectangle(img, (0, 5), (250, 40), (200,128,0), 2)
cv2.putText(img, "Son Sung Jong", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

cv2.imshow("Image", img)
cv2.waitKey(0)
