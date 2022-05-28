import matplotlib.pyplot as plt             # pip install matplotlib
from matplotlib import font_manager, rc

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rc("font", family=font_name)

x = ["봄", "여름", "가을", "겨울"]             # x축값
y = [20.5,30.5,15.5,1.5]             # y축값
plt.plot(x,y)              # 꺾은선 그리기
plt.show()                  # 보여주기

