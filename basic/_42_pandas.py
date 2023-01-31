import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')
print(df.head())
print(df.tail())

# 열 제목 조회
print(df.columns)

# 열 제목 바꾸기
df.columns = ['name', 'group', 'company', 'gender', 'birth', 'height', 'blood type', 'brand rate']
print(df)

# 행 제목 조회
print(df.index)

# pd.info() : null갯수와 데이터 타입을 조회할 때 사용하는 메서드
print(df.info())

# pd.describe() : 통계 정보 보기 (산술연산이 가능한 컬럼만 계산해서 출력해줌)
print(df.describe())

'''
count : 해당 row의 갯수
mean : 평균
std : 표준편차
min : 최소값
max : 최대값
'''

print(df.shape)         # shape 행 렬 갯수

df_desc = df.sort_index(ascending=False)          # 내림차순으로 정렬
print(df_desc)

# 키값을 기준으로 오름차순 정렬
df_height = df.sort_values('height')
print(df_height)

# 키로 정렬을 하고 동일하다면 브랜드지수로 정렬
df_sort2 = df.sort_values(['height', 'brand rate'])
print(df_sort2)