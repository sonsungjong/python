class 사칙연산:                 # A회사에 판매
    def 더하기(self, num1, num2):
        result = num1+num2
        print(result)
        return result
    def 빼기(self, num1, num2):
        result = num1 - num2
        print(result)
        return result
    def 곱하기(self, num1, num2):
        result = num1 * num2
        print(result)
        return result
    def 나누기(self, num1, num2):
        result = int(num1 / num2)
        print(result)
        return result

class 사칙연산Ex(사칙연산):               # B회사에 판매
    def 나누기(self, num1, num2):
        if num2 == 0:
            print("0으로는 나눌 수 없습니다.")
            return 0
        result = int(num1 / num2)
        print(result)
        return result

# 코드상으로 복붙하지않고 컴파일러가 복붙하게함
계산 = 사칙연산Ex()
계산.나누기(10,0)