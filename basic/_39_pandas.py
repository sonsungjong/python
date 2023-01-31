# pandas : 데이터 분석을 위한 패키지

# 엑셀, DB, pdf 읽기
# 크롤링 (웹 정보 수집)
# Database 핸들링
# 시각화

import pandas as pd

# Series : 1차원 데이터 배열 (column)
# DataFrame : 2차원 데이터 배열 (row, column)


# Series 가 모여서 DataFrame 을 구성
data1 = pd.Series([1,2,3,4])

a = [1,2,3,4]
data2 = pd.Series(a)

print(data1)
print(data2)

# Data Frame
company = [['삼성',2000, '스마트폰'], ['현대',1000,'자동차'], ['네이버', 500, '포털']]
df1 = pd.DataFrame(company)
print(df1)

# data frame에 제목 추가
df1.columns = ['기업명','매출액','업종']
print(df1)

# 딕셔너리로 data frame 만들기
company2 = {'기업명':['삼성','현대','네이버'], '매출액':[2000, 1000, 500], '업종':['스마트폰','자동차','포털']}
df2 = pd.DataFrame(company2)
print(df2)
