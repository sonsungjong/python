import pandas as pd

# csv파일 읽어오기
# CSV : Comma Separated Value (쉼표로 구분된 파일)
df1 = pd.read_csv('myData.csv')
print(df1.head())           # 위에서 5행만 조사

# 엑셀파일 읽어오기
df2 = pd.read_excel('myExcel.xlsx')
print(df2.head())

