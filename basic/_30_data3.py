import matplotlib.pyplot as plt             # pip install matplotlib

figure = plt.figure()
axes = figure.add_subplot(1,1,1)            # 1행 1열 1번째 subplot
x = [0,1,2,3,4]             # x축값
y = [4,1,3,5,2]             # y축값
x1 = [0,1,2,3,4]             # x1축값
y1 = [0,8,5,3,1]             # y1축값
axes.plot(x,y)              # 꺾은선 그리기
axes.plot(x1,y1, color='r', linestyle="dashed", marker="^")
plt.show()                  # 보여주기

