import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# 이중으로 행을 구성
df2 = df.groupby(['혈액형','성별']).mean()
print(df2)

r1 = df2.unstack('혈액형')
r2 = df2.unstack('성별')

# 인덱스 초기화 (reset_index)
df2 = df2.reset_index()
print(df2)