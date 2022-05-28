data1 = [1,2,3,4,5]
data2 = data1
print("data1은", data1, "입니다.")
print("data2는", data2, "입니다.")

data1[0] = 10
print("data1을 변경합니다.")
print("data1은", data1, "입니다.")
print("data2은", data2, "입니다.")

# data3 = list(data1)
data3 = data1.copy()
print("data1은", data1, "입니다.")
print("data3은", data3, "입니다.")
data1[0] = 20
print("data1을 변경합니다.")
print("data1은", data1, "입니다.")
print("data3은", data3, "입니다.")