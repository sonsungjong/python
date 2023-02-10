import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# include : 해당 자료형의 컬럼만 포함
# exclude : 해당 자료형의 컬럼은 제외
df1 = df.select_dtypes(include='object')
df2 = df.select_dtypes(exclude='object')

print(df1)
print('==============================================')
print(df2)

# 해당 데이터프레임에서 문자열을 제거하고 연산해주기
df_int = df.select_dtypes(exclude='object')
df_int = df_int + 10
print(df_int)

# 해당 자료형인 컬럼을 안내
num_cols = df.select_dtypes(exclude='object').columns
print(num_cols)

df4 = df[num_cols]
print(df4)
