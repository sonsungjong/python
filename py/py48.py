# class : 변수 + 함수
class 메모장:
    경로 = ""

    # 함수 정의
    def 메모장쓰기(self, text):
        f = open(self.경로, "w", encoding="UTF-8")
        f.write(text)    # 메모장 들어갈 내용
        f.close()

    def 메모장추가쓰기(self, text):
        f = open(self.경로, "a", encoding="UTF-8")
        f.write(text)    # 메모장 들어갈 내용
        f.close()

    def 메모장연속쓰기(self):
        while True:
            myText = input("입력할 문자 (0입력하면 탈출)>>>")
            if myText == "0":
                break
            else:
                self.메모장추가쓰기('\n'+myText)

    def 메모장읽기(self):
        f = open(self.경로, "r", encoding="UTF-8")
        lines = f.readlines()
        for line in lines:
            print(line, end="")
        f.close()

    def __init__(self, path="memo.txt"):
        # 클래스를 변수에 담을 때(객체화) 자동으로 사용되는 함수
        # 클래스를 사용하는 사람이 처음에 해줘야하는 작업을 빼먹는 경우가 많아 개발
        self.경로 = path
        # self : 클래스 안에 있는
# 클래스 사용
memo = 메모장("C:\\users\\administrator\\Desktop\\memo.txt")
# 경로
# memo.경로 = "memo.txt"
memo.메모장쓰기('필요한 내용')
# 쓸 내용
memo.메모장연속쓰기()

#page 269 예제
# page 276 예제
a = 3
class USB:
    # a = 3
    # capacity = 64
    def __init__(self, capacity):       # 생성자(변수화할때 사용되는 함수)
        self.capacity = capacity
        b = 3
        self.a = 3

    def info(self):
        self.a
        print(self.capacity, "GB USB")

usb = USB(64)           # __init__ 함수가 자동사용
usb.info()              # info() 함수 사용