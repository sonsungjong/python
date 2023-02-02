import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# 조건에 맞는 데이터만 뽑아온다
df[df['키'] > 170]          # 키가 170 이상인 row만 셀렉
df[df['키'] > 180]          # 키가 180 이상인 row만 선택

r0 = df[df['키'] > 180]['이름']
r1 = df[df['키'] > 180]['이름','키']

r2 = df.loc[df['키'] > 180, '이름']                     # 특정 한개의 컬럼 (키 180 이상만)
r3 = df.loc[df['키'] > 180, '이름':'성별']              # 컬럼 범위 지정 (키 180 이상만)
r4 = df.loc[df['키'] > 180, ['이름','키']]              # 특정 컬럼만 (키 180 이상만)

print(r0)
print(r1)
print(r2)
print(r3)
print(r4)

# isin 을 활용한 색인
# isin : 내가 조건을 걸고자하는 값이 내가 정의한 list에 있을 때만 색인하려는 경우
my_condition = ['플레디스','SM']
n1 = df['소속사'].isin(my_condition)
n2 = df.loc[df['소속사'].isin(my_condition)]
n3 = df.loc[df['소속사'].isin(my_condition), '소속사']

print(n1)
print(n2)
print(n3)