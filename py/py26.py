# 반복문 중단
from time import sleep
i = 0
while True:
    # sleep(1)
    print('무한반복')
    i += 1          # i = i + 1
    if i >= 5:
        break               # break가 실행되면 반복문이 즉시 종료

# break : 반복문 종료

# continue : 반복문 1회 취소 (처음으로 되돌아감)
for i in range(1, 11):          # 1~10, 총 10번
    if i % 2 == 0:
        continue            # continue를 만나는 순간 처음으로 돌아감
    print(i)

