from re import I
import urllib.request
from bs4 import BeautifulSoup

# URL 지정
page = urllib.request.urlopen("https://movie.naver.com/movie/sdb/rank/rpeople.nhn")
# 읽기
html = page.read()
# 문자열로 변환
str = html.decode()

#movie_in = []

# bs4 사용
soup = BeautifulSoup(str, "html.parser")
# <td class="title"> 을 모두 찾아 리스트로 만듦
review_list = soup.find_all("td", class_="title")

# <a> 태그 기준으로 나누기
for review in review_list:
    print(review.find("a").text.strip())
    #movie_in.append(review.find("a").text.strip())

# for i in movie_in:
#     print(i)