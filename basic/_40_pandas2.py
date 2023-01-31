import pandas as pd

lst = [['가','나','다'], [1,2,3], ['A','B','C']]
df1 = pd.DataFrame(lst)
df1.columns = ['I','II','III']              # column 명 바꾸기

print(df1)
print()

print(df1['II'])        # 해당 컬럼만 가져오기
print()

# index (row) 명 바꾸기
idx = ['a','b','c']
df1.index = idx
print(df1)
