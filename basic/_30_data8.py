import matplotlib.pyplot as plt             # pip install matplotlib
from matplotlib import font_manager, rc
import random

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rc("font", family=font_name)

x = []             # x축값
y = []             # y축값

for i in range(100):
    x.append(random.uniform(0, 50))
    y.append(random.uniform(0, 50))

plt.title('산포그래프')
plt.xlabel("X")
plt.ylabel("Y")
plt.scatter(x,y, s=40)              # 산포그래프 그리기
plt.show()                  # 보여주기

