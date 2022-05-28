import urllib.request
from bs4 import BeautifulSoup

# URL 지정
page = urllib.request.urlopen("https://movie.naver.com/movie/bi/mi/basic.naver?code=161967")
# 읽기
html = page.read()
# 문자열로 변환
str = html.decode()

# bs4 사용
soup = BeautifulSoup(str, "html.parser")
# <div class="score_reple"> 을 모두 찾아 리스트로 만듦
review_list = soup.find_all("div", class_="score_reple")

# <p> 태그 기준으로 나누기
for review in review_list:
    print(review.find("p").text.strip())