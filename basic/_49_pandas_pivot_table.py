# pivot_table : 엑셀의 피벗테이블
# 데이터 열 중 두개의 열을 각각 행과 열로 사용하여 데이터를 재구성
import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

# 행=소속사,열=혈액형,데이터값=키
pv = pd.pivot_table(df, index='소속사', columns='혈액형', values='키')
print(pv)

# index=행
# columns=열
# values=조회하고 싶은 값

# aggfunc=계산옵션 (기본값은 평균)
pv2 = pd.pivot_table(df, index='그룹', columns='혈액형', values='브랜드평판지수', aggfunc=np.mean)
pv3 = pd.pivot_table(df, index='그룹', columns='혈액형', values='브랜드평판지수', aggfunc=np.sum)
print(pv2)
print(pv3)