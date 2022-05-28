class 동물:
    def sound(self):
        print(self.say)
    def eat(self):
        print(self.feed,"을(를) 먹는다.")
    def setProperties(self, say, feed):
        self.say = say
        self.feed = feed
    def __init__(self):
        self.say = ""
        self.feed = ""

class 강아지(동물):
    def __init__(self):
        print("강아지를 샀습니다.")
        super().setProperties("멍멍", "개밥")

class 고양이(동물):
    def __init__(self):
        print("고양이를 샀습니다.")
        super().setProperties("야옹", "츄르")

# 더이상 동물이 추가되어도 부담이 덜함

pet1 = 고양이()
pet1.eat()

pet2 = 강아지()
pet2.eat()