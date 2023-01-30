#넘파이 정렬 sort
import numpy as np

arr = np.array([1, 10, 5, 8, 2, 4, 3, 6, 8, 7, 9])
print(arr)

# np.sort() : 오름차순으로 정렬
arr2 = np.sort(arr)
print(arr2)

# np.sort()[::-1] : 내림차순으로 정렬
arr3 = np.sort(arr)[::-1]
print(arr3)

arr.sort()          # arr 자체를 정렬
print(arr)

# 2차원 정렬
arr2d = np.array([[5,6,7,8],[4,3,2,1],[10,9,12,11]])
print(arr2d)

arr2d_1 = np.sort(arr2d, axis=1)          # 열을 정렬 (안쪽)
print(arr2d_1)

arr2d_0 = np.sort(arr2d, axis=0)        # 행을 정렬 (바깥쪽)
print(arr2d_0)

# argsort : 인덱스를 반환
arr2d_arg1 = np.argsort(arr2d, axis=1)      # 열
arr2d_arg0 = np.argsort(arr2d, axis=0)      # 행

print(arr2d_arg1)           # 열정렬 후 인덱스를 반환
print(arr2d_arg0)           # 행정렬 후 인덱스를 반환

# 값은 바뀔 수 있기 때문에 인덱스를 받는 경우가 있다