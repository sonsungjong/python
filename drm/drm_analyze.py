# DRM 파일 구조 분석 도구
# 사용법: DRM 걸린 원본 파일과 .iso (복호화된) 파일을 비교하여
#         DRM 헤더/래퍼 구조를 파악합니다.
#
# 실행: python drm_analyze.py <drm_file> <iso_file>
# 예시: python drm_analyze.py test.xlsx test.iso

import sys
import os


def analyze_files(drm_path, iso_path):
    with open(drm_path, "rb") as f:
        drm_data = f.read()
    with open(iso_path, "rb") as f:
        iso_data = f.read()

    drm_size = len(drm_data)
    iso_size = len(iso_data)
    diff = drm_size - iso_size

    print("=" * 60)
    print("DRM 파일 구조 분석")
    print("=" * 60)
    print(f"DRM 파일: {drm_path} ({drm_size:,} bytes)")
    print(f"ISO 파일: {iso_path} ({iso_size:,} bytes)")
    print(f"크기 차이: {diff:,} bytes ({diff/1024:.1f} KB)")
    print()

    # 1. DRM 파일 헤더 분석 (처음 64바이트)
    print("── DRM 파일 헤더 (처음 64 bytes) ──")
    print_hex(drm_data[:64])
    print()

    print("── ISO 파일 헤더 (처음 64 bytes) ──")
    print_hex(iso_data[:64])
    print()

    # 2. ISO 파일 내용이 DRM 파일 안에 있는지 검색
    # ISO 파일의 처음 32바이트가 DRM 파일 어디에 위치하는지 찾기
    iso_header = iso_data[:32]
    offset = drm_data.find(iso_header)

    if offset >= 0:
        print(f"★ ISO 파일 시작부분이 DRM 파일의 offset {offset} (0x{offset:X}) 에서 발견됨!")
        print(f"  → DRM 헤더 크기: {offset} bytes ({offset/1024:.1f} KB)")
        print()

        # DRM 헤더 부분만 별도 출력
        print(f"── DRM 헤더 (0 ~ {offset-1}, {offset} bytes) ──")
        print_hex(drm_data[:min(offset, 256)])
        if offset > 256:
            print(f"  ... (중간 {offset - 256} bytes 생략) ...")
        print()

        # 나머지 부분이 ISO와 동일한지 검증
        drm_body = drm_data[offset:]
        if drm_body == iso_data:
            print("✅ DRM 파일에서 헤더를 제거하면 ISO 파일과 100% 동일합니다!")
            print(f"   → 단순히 처음 {offset} bytes를 잘라내면 복호화 완료")
        elif drm_body[:iso_size] == iso_data:
            tail = drm_data[offset + iso_size:]
            print(f"✅ 본문은 동일! 뒤에 {len(tail)} bytes 꼬리(footer)가 추가됨")
            print(f"   → 처음 {offset} bytes 헤더 + 끝 {len(tail)} bytes 꼬리 제거하면 복호화 완료")
            print()
            print(f"── DRM 꼬리 (마지막 {min(len(tail), 128)} bytes) ──")
            print_hex(tail[:128])
        else:
            # 부분 비교로 어디부터 다른지 찾기
            mismatch_pos = find_first_mismatch(drm_body, iso_data)
            print(f"⚠️  헤더 이후 본문이 ISO와 다릅니다 (offset {mismatch_pos}에서 불일치)")
            print("   → 본문도 암호화되어 있을 가능성 있음")
    else:
        print("⚠️  ISO 파일 시작부분을 DRM 파일에서 찾지 못했습니다.")
        print("   → 본문이 암호화되어 있거나 다른 구조일 수 있음")
        print()

        # 부분 매칭 시도 - ISO 끝 부분이 DRM 끝에 있는지
        iso_tail = iso_data[-32:]
        tail_offset = drm_data.rfind(iso_tail)
        if tail_offset >= 0:
            print(f"  ISO 끝부분이 DRM 파일 offset {tail_offset}에서 발견됨")
        else:
            print("  ISO 끝부분도 DRM 파일에서 찾지 못함 → 본문 암호화 확실")

    # 3. 알려진 파일 시그니처 확인
    print()
    print("── 파일 시그니처 분석 ──")
    check_signature("DRM 파일", drm_data)
    check_signature("ISO 파일", iso_data)


def print_hex(data, cols=16):
    """헥사 덤프 출력"""
    for i in range(0, len(data), cols):
        chunk = data[i:i+cols]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {i:04X}: {hex_part:<{cols*3}}  {ascii_part}")


def find_first_mismatch(a, b):
    """두 바이트열에서 처음 다른 위치 찾기"""
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            return i
    return min_len


def check_signature(label, data):
    """알려진 파일 시그니처 확인"""
    sigs = {
        b"\x50\x4B\x03\x04": "ZIP/OOXML (xlsx/docx/pptx/hwpx)",
        b"\xD0\xCF\x11\xE0": "OLE2 (xls/doc/ppt/hwp)",
        b"\x48\x57\x50\x20": "HWP (한글)",
        b"\x25\x50\x44\x46": "PDF",
        b"\xFF\xD8\xFF": "JPEG",
        b"\x89\x50\x4E\x47": "PNG",
    }
    header = data[:4]
    found = False
    for sig, name in sigs.items():
        if data[:len(sig)] == sig:
            print(f"  {label}: {name} (시그니처: {sig.hex().upper()})")
            found = True
            break
    if not found:
        print(f"  {label}: 알 수 없는 형식 (처음 4 bytes: {header.hex().upper()})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python drm_analyze.py <DRM파일> <ISO파일>")
        print("  예: python drm_analyze.py 문서.xlsx 문서.iso")
        sys.exit(1)

    drm_path = sys.argv[1]
    iso_path = sys.argv[2]

    if not os.path.isfile(drm_path):
        print(f"파일 없음: {drm_path}")
        sys.exit(1)
    if not os.path.isfile(iso_path):
        print(f"파일 없음: {iso_path}")
        sys.exit(1)

    analyze_files(drm_path, iso_path)
