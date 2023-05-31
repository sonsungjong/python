# 최대공약수
def 최대공약수(a, b):
    while b > 0:
        a, b = b, a % b
    return a

# 최소공배수
def 최소공배수(a, b):
    return a * b //  이
    
