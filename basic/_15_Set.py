# 집합 (Set)
# 중복 안됨, 순서 없음

my_set = {1,3,3,5,4}
print(my_set)           # 중복되면 무시

korean = {"가", "나", "다"}
lang = set(["가", "나"])

# 교집합 (and)
print(korean & lang)
print(lang.intersection(korean))

# 합집합 (or)
print(korean | lang)
print(korean.union(lang))

# 차집합 (korean에 있지만 lang에 없는 것)
print(korean - lang)
print(korean.difference(lang))

# 추가하기
korean.add("라")
print(korean)

# 빼기
lang.remove("가")
print(lang)