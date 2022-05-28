v = False

for i in range(5):
    for j in range(3):
        if v is False:
            print("*", end= " ")
            v = True
        else:
            print("-", end = " ")
            v = False
    print()


for i in range(10):
    if i%2 == 1:
        print(i+1)

for i in range(2, 11, 2):
    print(i)

for i in range(1, 10):
    print(i*1,"\t",i*2,"\t",i*3,"\t",i*4,"\t",i*5,"\t",i*6,"\t",i*7,"\t",i*8,"\t",i*9,"\t")

for i in range(5):
    print("*"*(i+1))