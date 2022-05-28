sale = [80, 60, 22, 50, 75]

print(sale)
print(sale[0])
print("길이는",len(sale),"입니다")

for s in sale:
    print(s)

i = int(input("몇 번째 데이터를 변경합니까?"))
num = int(input("변경 후의 데이터를 입력하세요"))

print(i,"번 데이터", sale[i], "를 변경합니다.")

sale[i] = num

print(i, "번 데이터는", sale[i], "로 변경되었습니다.")