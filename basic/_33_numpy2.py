import numpy as np

arr = np.array([1,2,3,4], dtype=int)
print(type(arr))

mylist1 = [1,2,3,4]
mylist2 = [[1,2,3,4],[5,6,7,8]]

arr1 = np.array(mylist1)
arr2 = np.array(mylist2)

print(arr1.shape)           # (4,) : 4열
print(arr2.shape)           # (2,4) : 2행 4열

# 리스트는 여러개의 자료형을 보관할 수 있지만
# 넘파이는 하나의 자료형을 유지해줘야한다
arr3 = np.array([1, 3.14, '567'], dtype=int)
print(arr3)