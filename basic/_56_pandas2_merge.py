import numpy as np
import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')
df2 = pd.read_csv('http://bit.ly/ds-korean-idol-2')

# 병합하기 merge
# pd.merge(left, right, on='기준column', how='left')
pd.merge(df, df2, on='이름', how='left')            # left인자를 기준으로 행을 구성하여 NaN 대입
pd.merge(df, df2, on='이름', how='right')            # right인자를 기준
pd.merge(df, df2, on='이름', how='inner')            # 둘 다 있는 경우에만 (교집합)
pd.merge(df, df2, on='이름', how='outer')            # 기존값이 없으면 NaN (합집합)

pd.merge(df, df2, left_on='이름', right_on='이름', how='outer')            # 기존값이 없으면 NaN (합집합)

