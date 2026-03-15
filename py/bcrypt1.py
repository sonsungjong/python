import bcrypt

def check_password(password: str, hashed_password: str) -> bool:
    """입력한 비밀번호가 해싱된 비밀번호와 일치하는지 검증"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


if __name__ == "__main__":

    # -------------------------------------------------------
    # 1. DB에 저장된 bcrypt 해시값을 여기에 붙여넣으세요
    # -------------------------------------------------------
    # stored_hash = "$2a$10$v2LPYcsHYhV/2EtaMJSNzekXlQZI16.edbVFOffMKBOw/dQkhbGHO"
    stored_hash = "$2a$10$/Em5ZBBU3s/2DICQtfX61OyvbiixoabN.7d8mbk9BvsnFmpgeDWtm"
    

    # -------------------------------------------------------
    # 2. 유저가 사용할 법한 비밀번호 후보를 넣으세요
    # -------------------------------------------------------
    candidates = [
        "1234",
        "eovhqud",
        "대포병",
        "rnrwl",
        "h8769",
        "1111",
        "2222",
        "2424",
        "0000",
        "test1",
        "test2",
        "test1234",
        "test2222",
        "test",
        "테스트2",
        "테스트1",
    ]

    # -------------------------------------------------------
    # 3. 비밀번호 찾기
    # -------------------------------------------------------
    print(f"🔍 {len(candidates)}개의 후보 비밀번호를 검사합니다...\n")

    found = False
    for pw in candidates:
        match = check_password(pw, stored_hash)
        result = "✅ 일치!" if match else "❌"
        print(f"  {result}  {pw}")

        if match:
            print(f"\n🎉 비밀번호 찾았습니다: {pw}")
            found = True
            break

    if not found:
        print("\n❌ 일치하는 비밀번호를 찾지 못했습니다. 후보를 추가해보세요.")
