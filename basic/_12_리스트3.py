sale = [80, 60, 22, 50, 75]

print("현재 데이터는", sale, "입니다.")

print("끝에 100을 추가합니다.")
sale.append(100)            # 맨뒤에 추가
print("현재 데이터는", sale, "입니다.")

print("sale[2]에 25를 삽입합니다.")
sale.insert(2, 25)          # 해당 위치에 삽입
print("현재 데이터는", sale, "입니다.")

print("맨 앞의 데이터를 삭제합니다.")
del sale[0]                 # 해당 인덱스 삭제
print("현재 데이터는", sale, "입니다.")

print("22 값을 삭제합니다.")
sale.remove(22)             # 일치하는 값 삭제
print("현재 데이터는", sale, "입니다.")