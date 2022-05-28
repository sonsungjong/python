import matplotlib.pyplot as plt             # pip install matplotlib
from matplotlib import font_manager, rc

# figure = plt.figure()
# axes = figure.add_subplot(1,1,1)

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rc("font", family=font_name)

x = ["월", "화", "수", "목", "금", "토", "일"]             # x축값
y = [8,6,5,4,7,9,5]             # y축값
plt.title('주중 통화수')
plt.xlabel("요일")
plt.ylabel("통화수")
plt.bar(x,y)              # 막대그래프 그리기
plt.show()                  # 보여주기

