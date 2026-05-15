import struct
from collections import Counter

with open('yes_drm.pptx', 'rb') as f:
    drm = f.read()
with open('no_drm.pptx', 'rb') as f:
    clean = f.read()

# DRM 세그먼트 정보 (헤더에서 추출)
# Seg1: off=0x174, size=0x15C (메타/키)
# Seg2: off=0x2D0, size=0xAD0
# Seg3: off=0xDA0, size=0x8BC

# 가설: DRM 파일 = 헤더(0x174) + seg1(0x15C) + 암호화된_원본
# 즉, 원본 파일은 0x174 + 0x15C = 0x2D0 부터 시작?
# 아니면 세그먼트들이 원본에 삽입된 것?

print("=" * 60)
print("XOR 암호화 패턴 분석")
print("=" * 60)

# 접근 1: DRM[0x2D0:] 와 clean[0:] XOR
print("\n=== 접근 1: DRM[0x2D0:] XOR clean ===")
off = 0x2D0
body = drm[off:]
cmp_len = min(len(body), len(clean))
xor1 = bytes(a ^ b for a, b in zip(body[:cmp_len], clean[:cmp_len]))
print(f"XOR 처음 128 bytes:")
for i in range(0, 128, 16):
    chunk = xor1[i:i+16]
    h = ' '.join(f'{b:02X}' for b in chunk)
    print(f"  {i:04X}: {h}")

# 접근 2: 세그먼트 사이 간격 분석
# DRM에서 세그먼트를 제거하고 남은 부분을 clean과 비교
print("\n=== 접근 2: DRM에서 헤더+세그먼트 제거 후 비교 ===")
# 가설: DRM = [header 0x174] + [seg1_data 0x15C] + [원본 데이터]
# header + seg1 = 0x174 + 0x15C = 0x2D0
# 하지만 seg2는 0x2D0에서 시작... 세그먼트가 원본에 삽입된 것일 수 있음

# 가설 A: 세그먼트 데이터가 원본 사이에 삽입
# DRM 구조 = [header(0~0x173)] + [seg1_meta(0x174~0x2CF)] + [원본_part1] + ... 
# 하지만 크기가 안 맞을 수 있으니 다른 접근

# 접근 3: 단순히 모든 가능한 정렬로 XOR 분석
print("\n=== 접근 3: 다양한 오프셋에서 XOR 키 분석 ===")
for test_off in [0x174, 0x1A0, 0x2D0, 0xDA0]:
    body = drm[test_off:]
    cmp_len = min(len(body), len(clean))
    xor_result = bytes(a ^ b for a, b in zip(body[:cmp_len], clean[:cmp_len]))
    
    # XOR 결과 통계
    counter = Counter(xor_result[:4096])
    most_common = counter.most_common(5)
    unique_vals = len(counter)
    zero_pct = counter[0] / min(4096, cmp_len) * 100
    
    print(f"\n  Offset 0x{test_off:04X}:")
    print(f"    Unique XOR values (first 4096): {unique_vals}/256")
    print(f"    XOR=0x00 count: {counter[0]} ({zero_pct:.1f}%)")
    print(f"    Most common: {[(f'0x{v:02X}', c) for v, c in most_common]}")
    
    # 반복 패턴 체크: XOR 결과에 주기가 있는지
    for period in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
        key_candidate = xor_result[:period]
        matches = 0
        checks = min(4096, cmp_len) // period
        for i in range(checks):
            chunk = xor_result[i*period:(i+1)*period]
            if chunk == key_candidate:
                matches += 1
        if matches > checks * 0.8:  # 80% 이상 일치하면 유의미
            print(f"    *** Period {period} 반복 패턴 발견! ({matches}/{checks} = {matches/checks*100:.0f}% 일치)")
            print(f"    *** Key: {key_candidate.hex()}")

# 접근 4: DRM 본문에서 clean 조각 직접 검색
print("\n=== 접근 4: clean 파일 내 특정 바이트열이 DRM에 존재하는지 ===")
# OOXML의 [Content_Types].xml 문자열 검색
search_strings = [
    b"[Content_Types].xml",
    b"_rels/.rels",
    b"ppt/presentation.xml",
    b"PK\x03\x04",
    b"PK\x05\x06",
]
for s in search_strings:
    idx_clean = clean.find(s)
    idx_drm = drm.find(s)
    status = f"DRM: offset 0x{idx_drm:X}" if idx_drm >= 0 else "DRM: NOT FOUND"
    print(f"  '{s[:30]}': clean=0x{idx_clean:X}, {status}")

# 접근 5: 바이트 주파수 분석
print("\n=== 접근 5: 바이트 주파수 비교 (DRM body vs clean) ===")
drm_body = drm[0x1A0:]
drm_freq = Counter(drm_body)
clean_freq = Counter(clean)

print("  DRM body 상위 10 바이트:")
for val, cnt in drm_freq.most_common(10):
    print(f"    0x{val:02X}: {cnt:>5} ({cnt/len(drm_body)*100:.1f}%)")

print("  Clean 상위 10 바이트:")
for val, cnt in clean_freq.most_common(10):
    print(f"    0x{val:02X}: {cnt:>5} ({cnt/len(clean)*100:.1f}%)")

# 접근 6: 동일한 single-byte XOR 키 테스트
print("\n=== 접근 6: Single-byte XOR brute force ===")
# DRM body가 단일 바이트로 XOR 암호화 되었다면
# clean의 PK 시그니처 (50 4B 03 04)와 XOR해서 키를 추정
for test_off in [0x174, 0x1A0, 0x2D0]:
    d0, d1, d2, d3 = drm[test_off], drm[test_off+1], drm[test_off+2], drm[test_off+3]
    k0 = d0 ^ 0x50  # P
    k1 = d1 ^ 0x4B  # K
    k2 = d2 ^ 0x03
    k3 = d3 ^ 0x04
    print(f"  DRM[0x{test_off:X}] = {d0:02X} {d1:02X} {d2:02X} {d3:02X}")
    print(f"  XOR with PK sig: k0=0x{k0:02X} k1=0x{k1:02X} k2=0x{k2:02X} k3=0x{k3:02X}")
    all_same = (k0 == k1 == k2 == k3)
    print(f"  All same key? {'YES -> single byte XOR = 0x' + f'{k0:02X}' if all_same else 'NO'}")
