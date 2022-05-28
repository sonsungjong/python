#문제1
score = int(input("점수를 입력하세요>>>"))
if score > 90:
    print("점수는",score,"이고, 학점은 A학점입니다.")
elif score >80:
    print("점수는",score,"이고, 학점은 B학점입니다.")
elif score >70:
    print("점수는",score,"이고, 학점은 C학점입니다.")
elif score>60:
    print("점수는",score,"이고, 학점은 D학점입니다.")
else:
    print("점수는",score,"이고, 학점은 F학점입니다.")

#문제2
# num = int(input("정수를 입력하세요>>>"))
# if(num %3 == 0):
#     print(num,"는(은) 3의 배수입니다.")
# else:
#     print(num,"는(은) 3의 배수가 아닙니다.")


#문제3
# int1 = int(input("정수1 입력 >>>"))
# int2 = int(input("정수2 입력 >>>"))
# int3 = int(input("정수3 입력 >>>"))
# if int1 >= int2 and int1 >= int3:
#     print("가장 큰 수는", int1, "입니다.")
# elif int2 >= int1 and int2 >= int3:
#     print("가장 큰 수는", int2, "입니다.")
# else:
#     print("가장 큰 수는", int3, "입니다.")


# 문제4
# num = input("차량번호를 입력하세요")

# if int(num[-1]) %2 == 1:
#     print("홀수")
# else:
#     print("짝수")