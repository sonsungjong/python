import numpy as np
import pandas as pd

# groupby : 데이터를 그룹으로 묶어 분석할 때
df = pd.read_csv('http://bit.ly/ds-korean-idol')

print(df.head())

# 소속사별 모든 컬럼마다 각 갯수
r1 = df.groupby('소속사').count()
# 그룹별 평균 (산술통계 가능한 컬럼만 계산)
r2 = df.groupby('그룹').mean()
# 성별별 합계 (산술통계 가능한 컬럼만 계산)
r3 = df.groupby('성별').sum()

# 특정 열만 알고 싶다면
r4 = df.groupby('혈액형')['키'].mean()

print(r1)
print(r2)
print(r3)
print(r4)