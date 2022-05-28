class MyString:
    name = ""
    age = 0
    def setName(self, name):
        self.name = name
    def setAge(self, age):
        self.age = age
    def printInfo(self):
        print("이름은",self.name, "나이는", self.age)
    def __init__(self, name, age):
        self.setName(name)
        self.setAge(age)


내정보 = MyString("홍길동", 23)           # 결코 빼먹을수가 없음
#내정보.setName("홍길동")          # 뺴먹으면 문제
#내정보.setAge(23)
내정보.printInfo()
