# import random

# names = input("\", \"로 이름들을 입력하세요>>>")
# names = names.split(", ")
# names_num = len(names)

# random_choice = random.randint(0, names_num-1)
# print(f"{names[random_choice]} is go")

row1 = ["a", "b", "c"]
row2 = ["d", "e", "f"]
row3 = ["g", "h", "i"]
map = [row1, row2, row3]



position = int(input('Where do you want to put the treasure?'))
row_num = int(position/10)
column_num = position % 10

map[column_num-1][row_num-1] = "X"
print(f"{row1}\n{row2}\n{row3}")
