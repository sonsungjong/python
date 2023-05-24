import pygame
import random
import urllib.request
from bs4 import BeautifulSoup

BLACK = (0, 0, 0)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BALL_SIZE = 25

class Ball:
    '''공을 표현하는 클래스'''
    def __init__(self):
        #공의 중심 좌표를 임의로 지정
        self.x = random.randrange(BALL_SIZE, SCREEN_WIDTH - BALL_SIZE)
        self.y = random.randrange(BALL_SIZE, SCREEN_HEIGHT - BALL_SIZE)

        #다음 이동 방향을 설정
        self.change_x = 0
        while self.change_x == 0 or self.change_y == 0:
            self.change_x = random.randint(-4, 4)
            self.change_y = random.randint(-4, 4)

        #공의 색상을 지정
        r = random.randint(1, 255)
        g = random.randint(1, 255)
        b = random.randint(1, 255)
        self.color = (r, g, b)



# URL 지정
page = urllib.request.urlopen("https://movie.naver.com/movie/sdb/rank/rpeople.nhn")
# 읽기
html = page.read()
# 문자열로 변환
str1 = html.decode()
movie_in = []
# bs4 사용
soup = BeautifulSoup(str1, "html.parser")
# <td class="title"> 을 모두 찾아 리스트로 만듦
review_list = soup.find_all("td", class_="title")
# <a> 태그 기준으로 나누기
for review in review_list:
    # print(review.find("a").text.strip())
    movie_in.append(review.find("a").text.strip())
j = random.randint(0, 49)
print(movie_in[j], ": 공의 게임 (크롤링) ")


title = movie_in[j] + ": 공의 자동 이동(스페이스바를 누르면 공이 더 생깁니다.)"
#메인 프로그램
pygame.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption(title)
clock = pygame.time.Clock()

#여러 볼의 갖는 리스트에 첫 볼을 저장 
lstballs = []
lstballs.append(Ball())

# mySound=pygame.mixer.Sound("bgm.wav")
# mySound.play()

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            #스페이스 바를 누르면 새로운 공이 나오도록 
            if event.key == pygame.K_SPACE:
                lstballs.append(Ball())

    for ball in lstballs:
        #볼의 중심 좌표를 이동
        ball.x += ball.change_x
        ball.y += ball.change_y

        #윈도 벽에 맞고 바운싱
        #x 좌표가 위 이래를 벗어나면   
        if ball.x > SCREEN_WIDTH - BALL_SIZE or ball.x < BALL_SIZE:
            ball.change_x *= -1 #다음 이동 좌표의 증가 값을 부호 변경 
        #y 좌표가 위 이래를 벗어나면   
        if ball.y > SCREEN_HEIGHT - BALL_SIZE or ball.y < BALL_SIZE:
            ball.change_y *= -1 #다음 이동 좌표의 증가 값을 부호 변경 

    screen.fill(BLACK)
    i = 0
    #모든 볼을 그리기
    for ball in lstballs:
        i+=1
        pygame.draw.circle(screen, ball.color, [ball.x, ball.y], BALL_SIZE)
        #텍스트 출력
        font = pygame.font.Font('gulim.ttf', 40) #폰트와 글자 크기
        text1 = font.render(str(i), True, (255,255,255))
        screen.blit(text1, (ball.x-12, ball.y-22))
    text = font.render("바운싱 하는 공의 이동 게임", True, (255,255,255)) #텍스트와 색 지정
    screen.blit(text, (200, 200)) #위치 지정
    # 초당 60 프레임으로 그리기
    clock.tick(60) 
    pygame.display.flip()

pygame.quit()