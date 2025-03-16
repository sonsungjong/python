import bcrypt

def hash_password(password: str, rounds: int = 12) -> str:
    """
    주어진 비밀번호를 BCrypt 해시로 변환합니다.
    :param password: 원본 비밀번호
    :param rounds: 해싱 강도 (기본값: 12)
    :return: 해싱된 비밀번호 (문자열)
    """
    salt = bcrypt.gensalt(rounds)  # 자동 Salt 생성
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()  # 바이트 -> 문자열 변환

def check_password(password: str, hashed_password: str) -> bool:
    """
    입력한 비밀번호가 해싱된 비밀번호와 일치하는지 검증합니다.
    :param password: 원본 비밀번호
    :param hashed_password: 저장된 해싱된 비밀번호
    :return: 검증 결과 (True/False)
    """
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# 실행
if __name__ == "__main__":
    # 예시 비밀번호
    raw_password = "1234"
    
    # 비밀번호 암호화
    hashed_password = hash_password(raw_password)
    print("🔒 해싱된 비밀번호:", hashed_password)

    # 비밀번호 검증
    is_valid = check_password(raw_password, hashed_password)
    print("✅ 비밀번호 일치 여부:", is_valid)