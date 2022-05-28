시험점수 = [74, 85, 77, 81]
_80이상 = []
print(max(시험점수))
print(min(시험점수))
print(sum(시험점수)/len(시험점수))
print(sorted(시험점수))
print(sorted(시험점수, reverse=True))

for i in 시험점수:
    if i >= 80:
        _80이상.append(i)
    
print(len(_80이상))
print(_80이상)
