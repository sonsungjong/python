# 넘파이의 인덱싱과 슬라이싱
import numpy as np

# 슬라이싱 (Slicing)
arr = np.array([0,1,2,3,4,5,6,7,8,9])

print(arr[0])           # 맨 앞
print(arr[1])           # 2번째
print(arr[-1])          # 맨 뒤
print(arr[-2])          # 맨 뒤에서 2번째

# 범위를 벗어나면 프로그램이 강제종료됨

# 2차원 array
arr2d = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12]])
print(arr2d[0,2])              # 0행 2열
print(arr2d[2,1])              # 10

# 범위 색인(검색)
arr[1:]         # 1 ~ 끝
arr[:5]          # 처음 ~ 5미만
arr[1:5]         # 1 ~ 5미만
arr[:-1]          # 처음 ~ -1전까지

arr2d[0, :]         # 0행에서 모두 가져와라
arr2d[:, 2]         # 모든 행에서 2열을 가져와라
arr2d[:2, 2:]           # 처음~2미만 행까지, 2~끝열을 가져와라

# fancy 인덱싱 (리스트 형태로 인덱싱)
arr = np.array([10, 23, 2, 7, 90, 65, 32, 66, 70])
idx = [1,3,5]           # 추출하고 싶은 인덱스만 리스트형태로 요청
print(arr[idx])

print()
print(arr2d[[0,1],:])
print()
print(arr2d[:,[1,2,3]])

# boolean 인덱싱
# 조건을 통해 필터링 (True 인것만 추출)
myTrue = [False, False, True, True, True, False, True, True, False]
print(arr[myTrue])

arr2d[arr2d > 2]

print()
print(arr2d[arr2d > 5])
