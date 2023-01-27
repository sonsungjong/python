import urllib.request
from bs4 import BeautifulSoup            # pip install bs4

# 1. url 설정
url = urllib.request.urlopen("")
html = url.read()
문자열 = html.decode()

리스트 = []
soup = BeautifulSoup(문자열, "html.parser")
# 2. 규칙성이 있는 최소단위로 모두 추출
tag = soup.find_all("", class_="")
for i in tag:
    # 3. <>를 기준으로 찾고 <>를 없앤다
    result = i.find("").text.strip()
    # 태그 없애기
    # result = i.text.strip()
    리스트.append(result)

print(리스트)

for j in 리스트:
    print(j)
print("내가 볼 영화는>>",리스트[0])
