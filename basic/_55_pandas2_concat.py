import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')
df2 = pd.read_csv('http://bit.ly/ds-korean-idol-2')

# concat : 합친다
print(df.head())
print(df2.head())

df3 = df.copy()

# df 와 df3를 합친다 -> 인덱스를 리셋한다
df4 = pd.concat([df, df3], sort=False)          # 밑으로 붙인다 (row)
df4 = df4.reset_index(drop=True)
print(df4)

df5 = pd.concat([df, df2], axis=1)           # 옆으로 붙인다 (column)
print(df5)
