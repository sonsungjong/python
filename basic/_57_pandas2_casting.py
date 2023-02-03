import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# astype : 해당 컬럼을 타입변환

print(df.info())
'''
object: 문자열
float: 실수
int: 정수
category: 카테고리
datetime: 시간
'''

print(df['키'].dtypes)
df['키'] = df['키'].fillna(0.0)         # 결측치 제거해야 캐스팅 가능
df['키'] = df['키'].astype(int)            # 결측치(null)이 있으면 fillna로 임의값을 넣어준다음 변환해야함

print(df['키'])