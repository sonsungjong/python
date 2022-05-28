import urllib.request

# URL 지정
page = urllib.request.urlopen("https://www.python.org/")

# 읽기
html = page.read()
# 문자열로 변환
str = html.decode()

print(str)