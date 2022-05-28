class 강아지:
    def sound(self):
        print(self.say)
    def eat(self):
        print(self.feed,"을 먹는다.")
    def __init__(self):
        print("강아지를 샀습니다.")
        self.say = "멍멍"
        self.feed = "개밥"

class 고양이:
    def sound(self):
        print(self.say)
    def eat(self):
        print(self.feed, "를 먹는다.")
    def __init__(self):
        print("고양이를 샀습니다.")
        self.say = "야옹"
        self.feed = "츄르"
    def jump(self):
        print("고양이 점프!")

# 새와 병아리 추가