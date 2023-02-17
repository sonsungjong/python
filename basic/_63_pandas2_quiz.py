import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# https://www.data.go.kr/
# 공공데이터포털 -> 파일데이터 -> 주택도시보증공사_전국 신규 민간아파트 분양가격 동향 -> 다운로드

# https://bit.ly/ds-house-price
# 주택도시보증공사_전국 신규 민간아파트 분양가격 동향_20211231.csv
df = pd.read_csv('house-price.csv', encoding='cp949')
print(df.head())

# column명 재정의
df = df.rename(columns={'분양가격(제곱미터)':'분양가격', '규모구분':'규모'})
print(df.head())

# 빈값과 데이터형태 확인하기
print(df.info())

# 통계값 확인
print(df.describe())

# 공백데이터 제거 (0으로 넣어주기)
df.loc[df['분양가격'] == '', '분양가격'] = '0'
df.loc[df['분양가격'] == ' ', '분양가격'] = '0'
df.loc[df['분양가격'] == '  ', '분양가격'] = '0'

# null 제거 (0)
df['분양가격'] = df['분양가격'].fillna('0')

# , 콤마 제거
df['분양가격'] = df['분양가격'].str.replace(',','0')

df['분양가격'] = df['분양가격'].astype(int)
print(df.info())

# '전용면적' 문구 제거
df['규모'] = df['규모'].str.replace('전용면적','')

print(df.value_counts())

# 지역명 별로 평균 분양가격을 확인하자
result = df.groupby('지역명')['분양가격'].mean()
print(result)