import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# 데이터 전처리 방안2 : null이 있는 행을 제거하겠다
df_drop_null = df.dropna()              # null값이 있으면 그 행을 지우겠다
df_drop_null = df.dropna(axis=0)              # null값이 있으면 그 행을 지우겠다
df_drop_null_col = df.dropna(axis=1)              # null값이 있으면 그 열을 지우겠다

# 데이터 전처리 방안3 : 중복값을 제거한다
df_drop_dupl = df['키'].drop_duplicates()              # column에서 중복값이 있으면 제거한다 (첫번째만 유지)
