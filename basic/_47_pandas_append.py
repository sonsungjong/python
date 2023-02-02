import pandas as pd

df = pd.read_csv('http://bit.ly/ds-korean-idol')
# print(df)
# row를 추가
df2 = pd.DataFrame({'이름':['테디'], '그룹':['테디그룹'], '소속사':['좋은소속사'], '성별':['남자'], '생년월일':['1970-01-01'], '키':[195.0], '혈액형':['O'], '브랜드평판지수':[12345678]})
print(df2)

'''행 추가'''
df = df.append(df2, ignore_index=True)
print(df)

# column을 추가
df['국적'] = '대한민국'             # 국적 컬럼을 추가하고 모두 대한민국으로 초기화

df.loc[df['이름'] == '지드래곤', '국적'] = 'korea'
print(df)
