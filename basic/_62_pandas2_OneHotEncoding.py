# 원핫인코딩 (One-hot-encoding)
# 한개의 요소는 True, 나머지 요소는 False 로 만들어주는 기법

import pandas as pd
import numpy as np

df = pd.DataFrame('http://bit.ly/ds-korean-idol')

blood_map = {
    'A':0,
    'B':1,
    'AB':2,
    'O':3,
}

df['혈액형_code'] = df['혈액형'].map(blood_map)
print(df.head())

df['혈액형_code'].value_counts()
'''
df['혈액형_code']를 머신러닝 알고리즘에 넣으면 해당 컬럼 안에서 값들간의 관계를 스스로 형성해준다
이 상황에서 B형은 1, AB형은 2라고 값을 갖게되고, B형 + AB형 = O형과 같은 잘못된 관계가 형성된다
따라서, 4개의 별도 column을 추가생성하여 1개의 column에는 True를, 나머지는 False를 넣음으로
A,B,AB,O 형의 관계가 독립적이다를 표현해줘야한다
이를 "원핫인코딩" 이라고 한다
'''

# pd.get_dummies(df['혈액형_code'])
pd.get_dummies(df['혈액형_code'], prefix='혈액형')

# get_dummies 로 만든 컬럼들을 원본에 붙이면 된다
