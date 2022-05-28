# 키와 값
dic = {1:"김김김", 2:"나나나", 30:"하하하", "A-1":"에이일"}
print(dic[30])

print(dic.get(2))

print(30 in dic)        # True
print(3 in dic)        # False

dic["A-2"] = "에이투"           # 키는 A-2, 값은 에이투
print(dic)

# 삭제
del dic["A-1"]
print(dic)

# Key만 확인
print(dic.keys())

# 값만 확인
print(dic.values())

# key와 value 확인
print(dic.items())

# 모두 지우기
dic.clear()