f = open("Sample.txt", "r", encoding="UTF-8")

lines = f.readlines()

for line in lines:
    print(line, end="")

f.close()


# w : 쓰기모드
# r : 읽기모드
# a : 추가모드
# x : 신규작성모드
# w+ : 갱신을 위한 쓰기모드
# r+ : 갱신을 위한 읽기모드
# a+ : 갱신을 위한 추가모드
# f.write(문자열) : 쓰기
# f.writelines(시퀀스) : 여러줄쓰기
# f.readline() : 한줄읽기
# f.readlines() : 여러줄 읽기(리스트)
# f.read(크기) : 크기만큼 읽기
# f.seek(위치) : 읽고 쓰는 위치를 이동
# f.tell() : 현재 읽고 쓰는 위치를 얻음
# f.close() : 파일닫기