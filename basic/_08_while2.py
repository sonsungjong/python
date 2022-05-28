# 문제1(방법2)
# num = int(input("정수를 입력하세요>>>"))
# while True:
#     if num <= 0:
#         print("잘못된 입력입니다.")
#         break
#     print(num, "번째 Hello")
#     num -= 1

# 문제2
# num = 1
# while num < 100:
#     if num %7 == 0:
#         print(num)
#     num += 1

# 문제3
# money = int(input("자판기에 얼마를 넣을까요? >>> "))
# coffee = 0
# while money >= 300:
#     money -= 300
#     coffee += 1
#     print("커피",coffee,"잔, 잔돈",money,"원")

# 문제4
# flag = 1
# num1 = -1
# num2 = -1
# num3 = -1
# num4 = -1
# num5 = -1
# while flag <= 5:
#     _input = int(input("0~9 사이의 정수를 입력하세요>>>"))
#     if _input < 10 and _input >= 0:
#         if flag == 1:
#             num1 = _input
#             flag += 1
#         elif flag == 2 and _input != num1:
#             num2 = _input
#             flag += 1
#         elif flag == 3 and _input != num1 and _input != num2:
#             num3 = _input
#             flag += 1
#         elif (flag == 4 and _input != num1 and _input != num2 and _input != num3):
#             num4 = _input
#             flag += 1
#         elif (flag == 5 and _input != num1 and _input != num2 and _input != num3 and _input != num4):
#             num5 = _input
#             flag += 1
# print(num1)
# print(num2)
# print(num3)
# print(num4)
# print(num5)

# 문제5
