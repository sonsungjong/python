try:
    f = open("Sample.txt", "r", encoding="UTF-8")
except FileNotFoundError:
    print("파일을 찾을 수 없습니다.")
except Exception:
    print("파일을 열 수 없습니다.")
else:
    lines = f.readlines()
    for line in lines:
        print(line, end="")
    f.close()
finally:
    print("처리 종료")