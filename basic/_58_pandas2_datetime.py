import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# to_datetime() 으로 시간자료형으로 변환가능
print(df['생년월일'])           # object(문자열)
df['생년월일'] = pd.to_datetime(df['생년월일'])             # 문자열을 datetime으로 변환
print(df['생년월일'])           # datetime64

# 년/월/일 분리 등 날짜시간처리가 쉬워짐

print(df['생년월일'].dt.year)
print(df['생년월일'].dt.day)
print(df['생년월일'].dt.second)
print(df['생년월일'].dt.dayofweek)          # 0 ~ 6 : 월 ~ 일


df['생일_년도'] = df['생년월일'].dt.year            # column 추가
print(df.head())
