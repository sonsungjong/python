# 리스트 []
# 순서를 가지는 객체집합

# 지하철 칸별로 10, 20, 30명씩 있다면
subway1 = 10
subway2 = 20
subway3 = 30

subway = [10, 20, 30]
print(subway)

subway = ["홍길동", "아무개", "김철수"]
print(subway)

# 김철수는 어디에 있는가?
print(subway.index("김철수"))

# 손님1이 추가로 탑승
subway.append("손님1")
print(subway)

# 홍길동이 홍길동과 아무개 사이에 탑승
subway.insert(1, "홍길동")
print(subway)

# 지하철에 있는 사람을 뒤부터 한명씩 꺼냄
print(subway.pop())
print(subway)

# 홍길동이 몇명인지 확인하기
print(subway.count("홍길동"))

num_list = [5,2,3,1,4]
num_list.sort()             # 정렬
print(num_list)

num_list.reverse()          # 반전
print(num_list)

num_list.clear()        # 모두 삭제
print(num_list)

# 다양한 자료형이 가능
mix_list = ["아무개", 12, True]
print(mix_list)

# 리스트 합치기
mix_list.extend(subway)
print(mix_list)