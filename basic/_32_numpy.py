# 넘파이 : 수학, 과학 계산용 패키지
import numpy as np


# array (배열) : 여러 값들의 그룹
# 넘파이 1차원 배열
np.array([1,2,3,4])
_1D_array = np.array([1,2,3,4])
print(_1D_array)

# 넘파이 2차원 배열 
np.array([[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,16]])
_2D_array = np.array([[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,16]])
print(_2D_array)


# shape : 차원의 수를 확인
print(_1D_array.shape)
print(_2D_array.shape)

# axis : 축 (shape의 각 축에 대해 0, 1, 2, ...)
