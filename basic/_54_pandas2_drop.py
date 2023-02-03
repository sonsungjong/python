import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# pandas 행과 열을 제거하기

# column 제거하기
df2 = df.drop('그룹', axis=1)         # 그룹 열을 제거한다
df3 = df.drop(['그룹', '소속사'], axis=1)               # 그룹과 소속사를 제거한다

# row 제거하기
df4 = df.drop(3, axis=0)          # 3번 index 행을 제거한다
df5 = df.drop([3,5], axis=0)            # 3과 5번 index 행을 제거한다
