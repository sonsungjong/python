import pandas as pd
from openpyxl.workbook import Workbook

숫자 = [1,2,3,4,5,6]

data = {
    '한글' : ['가', '나', '다', '라', '마', '바'],
    '영어' : ['a', 'b', 'c', 'd', 'e', 'f'],
    '숫자' : [1,2,3,4,5,6]
}

df = pd.DataFrame(data, index=숫자)

print(df['숫자'])
print(df['숫자'][0:3])
print(df)
# CSV파일로 저장
df.to_csv('myData.csv', encoding='UTF-8-SIG', index=False)
# txt파일로 저장
df.to_csv('myTxt.txt', sep='\t')
# excel파일로 저장
df.to_excel('myExcel.xlsx', index=False)

df2 = pd.read_excel('myExcel.xlsx')
print(df2)

df2.to_csv('myTxt2.txt', index=False, sep='\t')

print(df.loc[df['숫자'] >= 3, ['숫자','영어']])