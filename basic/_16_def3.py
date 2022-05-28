def 더하기(n1, n2):
    덧셈 = int(n1) + int(n2)
    print(덧셈)

def 빼기(n1, n2):
    뺄셈 = int(n1) - int(n2)
    print(뺄셈)

def 곱하기(n1, n2):
    곱셈 = int(n1) * int(n2)
    print(곱셈)

def 나누기(n1, n2):
    나눗셈 = int(int(n1) / int(n2))
    print(나눗셈)

# =========================================

num1 = input("숫자를 입력하세요>>")
num2 = input("숫자를 입력하세요>>")

더하기(num1, num2)
빼기(num1, num2)
곱하기(num1, num2)
나누기(num1, num2)