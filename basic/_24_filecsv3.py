import csv

f = open("D:\\Sample.csv", "a",newline='')
ad = csv.writer(f)

ad.writerow([3, '부산','볼펜'])

f.close()