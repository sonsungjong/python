import numpy as np
import pandas as pd

# 데이터 프레임
df = pd.DataFrame({
    '통계':[60, 70, 80, 85, 75],
    '미술':[50, 55, 80, 100, 95],
    '체육':[70, 65, 50, 95, 100]
})
print(df)

# Column과 Column 연산 (Series간의 연산)
df['통계'] + df['미술'] + df['체육']
df['통계'] - df['미술']
df['통계'] * df['미술']
df['통계'] / df['미술']
df['통계'] % df['미술']

# Column과 숫자 연산
df['통계'] + 10
df['통계'] - 10
df['통계'] * 10
df['통계'] / 10
df['통계'] % 10

# 복합 연산
df['통계미술합계'] = df['통계'] + df['미술'] + 10
print(df)

각column의평균 = df.mean(axis=0)
각row의평균= df.mean(axis=1)
각column의합 = df.sum(axis=0)
각row의합 = df.sum(axis=1)

# NaN값과의 연산 ==> NaN
df = pd.DataFrame({
    '통계':[60, 70, np.nan, 85, 75],
    '미술':[50, np.nan, 80, 100, 95],
    '체육':[70, 65, 50, np.nan, 100]
})

df['통계'] / 2
1000 / df['통계']
df['통계'] / np.nan
np.nan / df['통계']

# DataFrame과 DataFrame 연산
df1 = pd.DataFrame({
    '미술':[10,20,30,40,50],
    '통계':[60,70,80,90,100]
})
df2 = pd.DataFrame({
    '통계':[10,20,30,40,50],
    '미술':[60,70,80,90,100]
})

# 문자열 column은 제거를 하고 연산을 시켜줘야함 / 
df3 = df1 + df2
print(df3)