states_of_korea = ["서울", "인천", "경기",
"강원", "제주", "충남", "충북", "전남", "전북", 
"경남", "경북", "부산", "세종", "울산"
]

# 첫번쨰
print(states_of_korea[0])
# 첫번째 값 변경
states_of_korea[0] = "서울2"
print(states_of_korea[0])
# 뒤부터
print(states_of_korea[-1])
# 맨뒤에 추가하기
states_of_korea.append("창원")
print(states_of_korea)

# 리스트와 리스트 붙이기
states_of_korea.extend(["강화", "대전"])
print(states_of_korea)

# 문자열을 기준점을 통해 리스트로 만들기
str_inp = "Hello, World, Python"
str_list = str_inp.split(", ")
print(str_list)
