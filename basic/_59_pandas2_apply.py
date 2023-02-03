import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')
df2 = df.copy()
df3 = df.copy()
# apply : 함수를 만들고 DataFrame에 구체적인 로직을 적용한다 (데이터치환)

# 남자/여자 -> 1/2 으로 변경
df2.loc[df['성별'] == '남자', '성별'] = 1
df2.loc[df['성별'] == '여자', '성별'] = 2

print(df2)

# apply에 적용할 함수를 만든다  ==> 데이터치환
# 남자 -> 1, 여자 -> 2
def gender2number(x):
    if x == '남자':
        return 1
    elif x == '여자':
        return 2

df3['성별'] = df3['성별'].apply(gender2number)
print(df3)

# =====================================================================
# '브랜드평판지수 / 키' 를 구해보자
df4 = df.copy()
def brandPerCm(df):
    value = df['브랜드평판지수'] / df['키']
    return value

df4 = df4.apply(brandPerCm, axis=1)
print(df4)

# lambda를 사용 (즉석제작하는 일회용 함수)    ==> 데이터 치환
# 남자 -> 1, 여자 -> 2
df5 = df.copy()
df5['성별'] = df5['성별'].apply(lambda x: 1 if x == '남자' else 0)
df5['키/2'] = df5['키'].apply(lambda x: x/2)
print(df5.head())

# map을 사용 (dict)    ==> 데이터 치환
# 남자 -> 1, 여자 -> 2
df6 = df.copy()
my_map = {'남자':1, '여자':2}
df6['성별'] = df6['성별'].map(my_map)
print(df6.head())
