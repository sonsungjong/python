import urllib.request

# URL 지정
page = urllib.request.urlopen("https://movie.naver.com/movie/bi/mi/basic.naver?code=161967")

# 읽기
html = page.read()
# 문자열로 변환
str = html.decode()

print(str)