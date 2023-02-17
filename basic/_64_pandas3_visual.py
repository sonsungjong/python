# 시각화 : 수많은 숫자 + 문자열 데이터로부터 사람이 이해하기 쉽도록 시각적 정보로 제공
# EDA : 탐색적 데이터 분석(Exploratory Data Analysis), 수집한 데이터가 들어왔을 때 이를 다양한 각도에서 관찰 및 이해하는 과정

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

font_path = "C:\\Windows\\Fonts\\H2GTRE.TTF"
font = font_manager.FontProperties(fname=font_path, size=10).get_name()
rc('font', family=font)

df = pd.read_csv('https://bit.ly/ds-house-price-clean')
# df = pd.read_csv('house-price.csv', encoding='cp949')
print(df.head())

df.plot()
plt.rcParams['figure.figsize'] = (12,9)         # 크기조정이 안먹힘
plt.show()