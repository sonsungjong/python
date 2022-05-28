def 더하기(n1, n2):
    덧셈 = int(n1) + int(n2)
    return 덧셈

def 빼기(n1, n2):
    뺄셈 = int(n1) - int(n2)
    return 뺄셈

def 곱하기(n1, n2):
    곱셈 = int(n1) * int(n2)
    return 곱셈

def 나누기(n1, n2):
    나눗셈 = int(int(n1) / int(n2))
    return 나눗셈

# =========================================

num1 = input("숫자를 입력하세요>>")
num2 = input("숫자를 입력하세요>>")

sum = 더하기(num1, num2)
sub = 빼기(num1, num2)
mul = 곱하기(num1, num2)
div = 나누기(num1, num2)

print(sum)