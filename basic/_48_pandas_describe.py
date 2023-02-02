import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

통계값 = df.describe()
'''
count : 해당 컬럼의 row갯수 (null 갯수 제외)
mean : 평균
std : 표준편차
min : 최소값
max : 최대값
25% : 4등분을 하여 아래서 25%

'''

print(통계값)

df['키'].min()
df['키'].max()
df['키'].sum()
df['키'].mean()

# 분산과 표준편차는 평균으로부터 얼마나 떨어져있는지 정도를 나타냄
# 분산 = (데이터 - 평균) ** 2 를 모두 합한 값
# 표준편차(std) == 분산의 루트

data_01 = np.array([1,3,5,7,9])
data_02 = np.array([3,4,5,6,7])

# 평균은 동일하지만
print(data_01.mean())
print(data_02.mean())

# 분산은 다를 수 있다
print(data_01.var())
print(data_02.var())

# 표준편차 (분산에 루트를 씌운다) : 데이터가 평균으로부터 얼마나 퍼져있는지 정도를 나타냄
print(np.sqrt(data_01.var()))
print(np.sqrt(data_02.var()))

df['키'].var()          # 분산
df['키'].std()          # 표준편차
df['키'].count()            # 갯수
df['키'].median()           # 중앙값 (오름차순 정렬 후 가운데 있는 값)
df['키'].mode()             # 가장 많이 있는 값
