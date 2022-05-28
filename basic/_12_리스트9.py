import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
font_path = "C:\\Windows\\Fonts\\H2GTRE.TTF"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

data = []

while True:
    num = int(input("데이터를 입력하세요(0은 입력종료)>>>"))
    if(num == 0):
        break
    data.append(num)

plt.title("제목")
plt.xlabel("x축")
plt.ylabel("y축")
plt.hist(data)
plt.show()