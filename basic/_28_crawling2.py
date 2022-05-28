import urllib.request
from html.parser import HTMLParser

# HTMLParser 클래스를 상속받아 사용
class SampleHTMLParser(HTMLParser):
    # 생성자
    def __init__(self):
        HTMLParser.__init__(self)
        self.title = False
    
    # 시작태그 해석
    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.title = True
    
    # HTML안에 있는 데이터를 추출
    def handle_data(self, data):
        if self.title is True:
            print("타이틀:",data)
            self.title = False

# URL 지정
page = urllib.request.urlopen("https://movie.naver.com/movie/bi/mi/basic.naver?code=161967")
# 읽기
html = page.read()
# 문자열로 변환
str = html.decode()

# 객체화
p = SampleHTMLParser()
# 페이지 해석
p.feed(str)

# 정상종료
p.close()