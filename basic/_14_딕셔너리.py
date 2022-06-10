# 딕셔너리 = {}
dic = {1:"김김김", 2:"나나나", 30:"하하하", "A-1":"에이일"}

# 추가
dic[3] = "다다다"
dic[4] = "라라라"
dic["update"] = 44

# 조회
print(dic[30])
print(dic.get(2))

print(30 in dic)        # True
print(4 in dic)        # False

# 삭제
dic.pop(30)
del dic["A-1"]
print(dic)

# 수정
dic[1] = "김밥나라"
dic.update(update="11")         # 없는 키를 적으면 추가

# 전체 조회
for i in dic:
    print(i,":",dic.get(i))

# 전체 조회2
for i, k in dic.items():
    print(i,":",k)

# 모두 지우기
dic.clear()