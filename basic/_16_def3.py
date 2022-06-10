# 사칙연산 연산자는 한번에 숫자 2개만 처리할 수 있다.
# 3개를 처리하는 연산자(기능)는 개발자가 직접 만들어 사용하도록 만든게 함수이다.

def 더하기3(n1, n2, n3):
    덧셈 = int(n1) + int(n2) + int(n3)
    print(덧셈)

def 빼기3(n1, n2, n3):
    뺄셈 = int(n1) - int(n2) - int(n3)
    print(뺄셈)

def 곱하기3(n1, n2, n3):
    곱셈 = int(n1) * int(n2) * int(n3)
    print(곱셈)

def 나누기3(n1, n2, n3):
    나눗셈 = int(int(n1) / int(n2)/ int(n3))
    print(나눗셈)

# =========================================

num1 = input("숫자1 입력하세요>>")
num2 = input("숫자2 입력하세요>>")
num3 = input("숫자3 입력하세요>>")

더하기3(num1, num2, num3)
빼기3(num1, num2, num3)
곱하기3(num1, num2, num3)
나누기3(num1, num2, num3)