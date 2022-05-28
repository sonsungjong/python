import matplotlib.pyplot as plt             # pip install matplotlib
from matplotlib import font_manager, rc

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rc("font", family=font_name)

x = [1,2,3,4,5,6]             # x축값
y = [6,4,1,2,7,5]             # y축값
area = [50, 100, 150, 200, 250, 300]        # 점의 크기
color = ["red", "green", "blue","orange","aqua","crimson"]
plt.title('산포그래프')
plt.xlabel("x축")
plt.ylabel("y축")
plt.scatter(x,y, s=area, c=color)              # 산포그래프 그리기
plt.show()                  # 보여주기

