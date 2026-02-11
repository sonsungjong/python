import bcrypt
import itertools
import string
import time

def check_password(password: str, hashed_password: str) -> bool:
    """입력한 비밀번호가 해싱된 비밀번호와 일치하는지 검증"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


if __name__ == "__main__":

    # -------------------------------------------------------
    # 1. DB에 저장된 bcrypt 해시값
    # -------------------------------------------------------
    # stored_hash = "$2a$10$v2LPYcsHYhV/2EtaMJSNzekXlQZI16.edbVFOffMKBOw/dQkhbGHO"
    stored_hash = "$2a$10$ZFjQvEHCk22FHrN6SbJr5eIt3.E9tdyV6jUOKQKr5ufW1JlOKKXby"

    # -------------------------------------------------------
    # 2. 후보 문자를 직접 넣으세요
    # -------------------------------------------------------
    charset = "1234567890abcdefghijklmnopqrstuvwxyz"

    min_length = 4
    max_length = 4

    # -------------------------------------------------------
    # 3. 브루트포스 시작
    # -------------------------------------------------------
    print(f"🔍 브루트포스 시작")
    print(f"   길이 범위: {min_length} ~ {max_length}자리")

    # 총 조합 수 계산
    total = sum(len(charset) ** l for l in range(min_length, max_length + 1))
    print(f"   총 조합 수: {total:,}개")
    print(f"   ⚠️ bcrypt는 느린 해시라 시간이 오래 걸릴 수 있습니다.")
    print("=" * 60)

    found = False
    count = 0
    start_time = time.time()

    for length in range(min_length, max_length + 1):
        if found:
            break

        combos_for_length = len(charset) ** length
        print(f"\n📏 {length}자리 검사 중... ({combos_for_length:,}개)")

        for combo in itertools.product(charset, repeat=length):
            candidate = "".join(combo)
            count += 1

            # 진행 상황 표시 (1000개마다)
            if count % 1000 == 0:
                elapsed = time.time() - start_time
                speed = count / elapsed if elapsed > 0 else 0
                remaining = (total - count) / speed if speed > 0 else 0
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                print(f"  [{count:,}/{total:,}] 현재: {candidate} | "
                      f"속도: {speed:.0f}개/초 | "
                      f"남은 시간: {hours}시간 {minutes}분")

            if check_password(candidate, stored_hash):
                elapsed = time.time() - start_time
                print(f"\n🎉 비밀번호 찾았습니다!")
                print(f"   비밀번호: {candidate}")
                print(f"   시도 횟수: {count:,}개")
                print(f"   소요 시간: {elapsed:.1f}초")
                found = True
                break

    if not found:
        elapsed = time.time() - start_time
        print(f"\n❌ {count:,}개 전부 검사했지만 찾지 못했습니다.")
        print(f"   소요 시간: {elapsed:.1f}초")
