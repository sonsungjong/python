import pandas as pd

# 결측값(Null) : 비어있는 값, 결측값
# NaN 으로 표시 됨 (Not a Number)

df = pd.read_csv('http://bit.ly/ds-korean-idol')
print(df)

# 결측값 갯수 조사 (NaN 갯수 조사)
df.info()

# 결측값 다루기
df.isna()           # True 위치가 Null

# null 인 것 찾기 (True/False)
df['그룹'].isnull()
# null인 것을 조사
df['그룹'][df['그룹'].isnull()]
df.loc[df['그룹'].isnull()]
df.loc[df['그룹'].isnull(), ['키', '혈액형']]


# null 이 아닌 것 찾기 (True/False)
df['그룹'].notnull()
# null이 아닌 값만 추출
df['그룹'][df['그룹'].notnull()]
df.loc[df['그룹'].notnull()]
df.loc[df['그룹'].notnull(), ['키', '혈액형']]
