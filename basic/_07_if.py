# 조건 분기
# if 조건:
#     실행 명령문

# 날씨에 따라서 챙겨야하는 준비물
weather = input("오늘 날씨는 어때요? ")

if weather == "비":
    print("우산을 챙기세요")
elif weather == "미세먼지":
    print("마스크를 챙기세요")
else:
    print("준비물이 없어요")


temp = int(input("기온은 어때요? "))
if temp >= 30:
    print("날씨가 너무 더워요")
elif temp >= 10 and temp < 30:
    print("괜찮은 날씨에요")
elif 0 <= temp < 10:
    print("쌀쌀한 날씨에요")
else:
    print("날씨가 너무 추워요")