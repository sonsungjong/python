import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# null(NaN)의 정도 확인
print(df.info())

# 데이터 전처리 방안1 : 결측값에 0을 넣을수도 있고 평균값을 넣을수도 있고 비슷한 유형만 groupby해서 평균값을 넣을수도 있고...

# fillna : 결측값 채우기 (데이터 전치리 과정 중 null값을 제거하는 과정)
# 키의 정보가 누락되어 있다면 -1로 채워보도록 하자
df['키'].fillna(-1)

# 결측값 제거1
df2 = df.copy()
df2['키'].fillna(-1, inplace=True)          # 결측값 변경을 지속적으로 유지하겠다

# 결측값 제거2
df3 = df.copy()
df3['키'] = df3['키'].fillna(-1)            # 결측값을 변경하고 리턴을 자기자신에 대입하겠다
print(df3)

df4 = df.copy()
df4['키'] = df4['키'].fillna(df4['키'].mean())          # 키에서 결측값을 평균값으로 대체하겠다
print(df4)
