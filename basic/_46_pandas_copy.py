import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')

address_df = df             # 원본 데이터에도 영향이 간다 (주소값)
copy_df = df.copy()         # 원본데이터에는 영향이 가지않도록 복붙

# copy() 메소드를 써야 원본데이터가 유지된다.
