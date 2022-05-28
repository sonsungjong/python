import csv

f = open("D:\\Sample.csv", "w",newline='')
wr = csv.writer(f)

wr.writerow([1, '서울','노트'])

f.close()