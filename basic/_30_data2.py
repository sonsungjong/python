import matplotlib.pyplot as plt             # pip install matplotlib

figure = plt.figure()
axes = figure.add_subplot(1,1,1)            # 1행 1열 1번째 subplot
x = [0,1,2,3,4]             # x축값
y = [4,1,3,5,2]             # y축값
axes.plot(x,y)              # 꺾은선 그리기
plt.show()                  # 보여주기

