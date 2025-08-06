from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

img = Image.open('./quotation_noline/19층 모형실 가구장^0001.png')
img_cv = np.array(img)
gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)         # Image 로 읽으면 RGB 순 (cv2로 읽으면 BGR순)

height, width = gray.shape[:2]
new_width = 800
new_height = int(height * (new_width / width))
gray_img_resized = cv2.resize(gray, (new_width, new_height))

cv2.imshow('window_name', gray_img_resized)
cv2.waitKey(0)
cv2.destroyAllWindows()
# plt.imshow(gray, cmap='gray')
# plt.axis('off')
# plt.show()