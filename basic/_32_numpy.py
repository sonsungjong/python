# 넘파이 : 수학, 과학 계산용 패키지
import numpy as np


# array (배열) : 여러 값들의 그룹
# 넘파이 1차원 배열
np.array([1,2,3,4])
array_1D = np.array([1,2,3,4])
print(array_1D)

# 넘파이 2차원 배열 
np.array([[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,16]])
array_2D = np.array([[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,16]])
print(array_2D)


# shape : 차원의 수를 확인
print(array_1D.shape)
print(array_2D.shape)

print(array_1D[0])
print(array_1D[1])

# axis : 축 (shape의 각 축에 대해 0, 1, 2, ...)
