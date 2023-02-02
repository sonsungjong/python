import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# 특정 column 을 선택하는 방법
names = df['이름']
print(names)

# 범위 선택 loc, iloc
print(df[:3])               # 3개의 행
print(df.head(3))           # 3개의 행

df.loc[:3, ['이름','생년월일']]             # 3개의 행을 가져오고 열은 [이름과 생년월일]만
df.loc[:, ['이름']]

df.iloc[:,[0,2]]            # loc는 컬럼명으로, iloc는 인덱스로 열을 선정
print(df.iloc[:5, [0,1,2]])         # 행 범위, 열 인덱스
