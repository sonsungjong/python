# page 195
'''
커피자판기 프로그램
1. 돈과 주문할 커피를 입력
2. 없는 커피면 돈을 그대로 반환
3. 아메리카노:1000, 카페라떼:1500, 카푸치노:2000
4. 금액이 부족하면 돈을 그대로 반환
5. 정상주문이면 커피와 잔돈 반환
'''

def coffee_machine(money, pick):
    print('{}원에 {}를 선택하셨습니다.'.format(money, pick))
    menu = {'아메리카노':1000, '카페라떼':1500, '카푸치노':2000}

    if pick not in menu:
        print('{}는 판매하지 않습니다.'.format(pick))
        return money, '없는 메뉴'
    elif menu[pick] > money:
        print('{}는 {}원입니다.'.format(pick, menu[pick]))
        return money, '금액 부족'
    else:
        return money - menu[pick], pick

order = input("커피를 선택하세요 (아메리카노, 카페라떼, 카푸치노)>>>")
pay = int(input("얼마를 내시나요?>>>"))

change, coffee = coffee_machine(pay, order)
print('잔돈 {}원, 커피 {}'.format(change, coffee))



