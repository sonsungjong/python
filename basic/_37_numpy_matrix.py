import numpy as np

# Matrix : 행(row) + 열(column)
# 행렬 덧셈은 shape(구조)가 같아야한다
# 2x3 과 2x3    ==> 2x3
# 4x4 와 4x4    ==> 4x4

# 행렬 곱셈은 맞닿는 shape가 같아야한다
# 2x3 과 3x2    => 2x2
# 4x2 와 2x1    => 4x1

# 덧셈/뺄셈/곱셈
a = np.array([[1,2,3],[2,3,4]])         # 2x3
b = np.array([[3,4,5],[1,2,3]])         # 2x3
print(a+b)
print(a-b)
print(a*b)

'''
내부 합계 np.sum
'''
result0 = np.sum(a, axis=0)           # row의 합계
result1 = np.sum(a, axis=1)           # column끼리 합계

print('row의 합계:', result0)
print('col의 합계:', result1)

'''
행렬 곱셈 np.dot
    1. * 로 곱셈하면 같은 shape끼리 곱셈을 한다 (같은 위치에 있는 것을 곱하기)
    2. np.dot 을 사용하면 행렬 곱셈을 계산한다 (행렬곱셈)
'''

result = a*b          # 그냥 같은 위치 곱하기
print(result)

c = np.array([[1,2],[3,4],[5,6]])             # 3x2

result = np.dot(a,c)        # 행렬곱셈
print(result)           # 2x2
