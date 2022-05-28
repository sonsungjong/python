import urllib.request
from bs4 import BeautifulSoup

# URL 지정
page = urllib.request.urlopen("https://movie.naver.com/movie/sdb/rank/rmovie.naver")
# 읽기
html = page.read()
# 문자열로 변환
str = html.decode()

movie = []

# bs4 사용
soup = BeautifulSoup(str, "html.parser")
# <div class="tit3"> 을 모두 찾아 리스트로 만듦
review_list = soup.find_all("div", class_="tit3")

# <a> 태그 기준으로 나누기
for review in review_list:
    #print(review.find("a").text.strip())
    movie.append(review.find("a").text.strip())

for i in range(50):
    print(i+1,"위:",movie[i])