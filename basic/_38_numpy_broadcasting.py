import numpy as np

a = np.array([[1,2,3],[2,3,4]])
b = np.array([[3,3,3],[3,3,3]])

# 모든 요소에 3을 더하고 싶다면
print(a+b)
print()

# Broadcasting : numpy에 상수를 연산하면 전체 요소에 각각 계산이 된다
print('모두 3 더해줘:',a+3)
print('모두 3 빼줘:',a-3)
print('모두 3 곱해줘:',a*3)
print('모두 3 나눠줘:',a/3)
