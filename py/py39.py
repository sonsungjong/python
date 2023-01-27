# 입력한 돈으로 700원짜리 음료수 몇 잔을 뽑을 수 있는지 확인
def vending_machine(money):
    총갯수 = money // 700
    음료수 = 0
    for i in range(총갯수):
        print("음료수 = {}개, 잔돈 = {}원".format(음료수, money))
        음료수 += 1
        money -= 700
    print("음료수 = {}개, 잔돈 = {}원".format(음료수, money))

# 들어온 숫자를 절댓값(양수)으로 해서 더하기
def 절댓값더하기(숫자1, 숫자2):
    if 숫자1 < 0:
        숫자1 = 숫자1 * -1
        if 숫자2 < 0:
            숫자2 = 숫자2 * -1
    elif 숫자2 < 0:
        숫자2 = 숫자2 * -1
    return 숫자1+숫자2

print(절댓값더하기(3, -1))         # 4
print(절댓값더하기(5, 2))          # 7
print(절댓값더하기(-3, -2))        # 5

vending_machine(3000)
'''
음료수 = 0개 , 잔돈 = 3000원
음료수 = 1개 , 잔돈 = 2300원
음료수 = 2개 , 잔돈 = 1600원
음료수 = 3개 , 잔돈 = 900원
음료수 = 4개 , 잔돈 = 200원
'''
# money // 700 == 최대 갯수

# money = 3000
# can = 0
# while money > 700:
#     print("음료수 = {}개, 잔돈 = {}원".format(can, money))
#     can += 1
#     money -= 700
# print("음료수 = {}개, 잔돈 = {}원".format(can, money))