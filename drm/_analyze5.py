import struct
from collections import Counter
import math

def entropy(data):
    if not data:
        return 0
    freq = Counter(data)
    n = len(data)
    return -sum((c/n) * math.log2(c/n) for c in freq.values())

def hexdump(data, max_bytes=128):
    lines = []
    for i in range(0, min(len(data), max_bytes), 16):
        chunk = data[i:i+16]
        h = ' '.join(f'{b:02X}' for b in chunk)
        a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'  {i:04X}: {h:<48}  {a}')
    return '\n'.join(lines)

def analyze_pair(drm_path, clean_path, label):
    with open(drm_path, 'rb') as f:
        drm = f.read()
    with open(clean_path, 'rb') as f:
        clean = f.read()

    diff = len(drm) - len(clean)
    print(f'\n{"="*70}')
    print(f'  {label}')
    print(f'{"="*70}')
    print(f'DRM:   {len(drm):>10,} bytes (0x{len(drm):X})')
    print(f'Clean: {len(clean):>10,} bytes (0x{len(clean):X})')
    print(f'Diff:  {diff:>10,} bytes ({diff/1024:.1f} KB)')

    # DRM 헤더
    print(f'\n--- DRM Header (first 256 bytes) ---')
    print(hexdump(drm, 256))

    print(f'\n--- Clean Header (first 64 bytes) ---')
    print(hexdump(clean, 64))

    # DRM 헤더 필드 (BE u32)
    print(f'\n--- DRM Header Fields (non-zero BE u32) ---')
    header_fields = {}
    for off in range(0x44, 0xA0, 4):
        if off + 4 <= len(drm):
            val = struct.unpack('>I', drm[off:off+4])[0]
            if val != 0 and val < 0x30000000:  # ASCII 문자열 제외
                header_fields[off] = val
                print(f'  0x{off:04X}: {val:>10,} (0x{val:08X})')

    # 세그먼트 테이블 해석
    print(f'\n--- Segment Table ---')
    segments = []
    for i in range(0x74, 0xA0, 8):
        if i + 8 <= len(drm):
            seg_off = struct.unpack('>I', drm[i:i+4])[0]
            seg_size = struct.unpack('>I', drm[i+4:i+8])[0]
            if seg_off > 0 and seg_size > 0 and seg_off < len(drm):
                segments.append((seg_off, seg_size))
                print(f'  off=0x{seg_off:X} ({seg_off}), size=0x{seg_size:X} ({seg_size})')

    # 0x174 근처의 키 후보 영역
    print(f'\n--- Key candidate region (0x174-0x1A0) ---')
    key_region = drm[0x174:0x1A0]
    print(hexdump(key_region, 64))
    print(f'  Hex: {key_region.hex()}')

    # 본문 암호화 분석
    # 가능한 body 시작점들
    body_starts = set()
    if segments:
        body_starts.add(segments[0][0])
        for seg_off, seg_size in segments:
            body_starts.add(seg_off)
    body_starts.update([0x174, 0x1A0, 0x2D0, diff])

    print(f'\n--- Body alignment & XOR analysis ---')
    for bstart in sorted(body_starts):
        if bstart + 16 > len(drm):
            continue
        body = drm[bstart:]
        cmp_len = min(len(body), len(clean))
        if cmp_len < 64:
            continue
        xor_result = bytes(a ^ b for a, b in zip(body[:cmp_len], clean[:cmp_len]))

        # 통계
        zero_count = sum(1 for x in xor_result[:4096] if x == 0)
        total_check = min(4096, cmp_len)
        unique = len(set(xor_result[:total_check]))

        # 완전 일치 체크
        if all(x == 0 for x in xor_result):
            print(f'  offset 0x{bstart:04X}: *** PERFECT MATCH (no encryption!) ***')
            continue

        print(f'  offset 0x{bstart:04X}: zeros={zero_count}/{total_check} ({zero_count/total_check*100:.1f}%), unique={unique}/256')

    # 엔트로피
    print(f'\n--- Entropy ---')
    print(f'  DRM body (0x1A0~): {entropy(drm[0x1A0:]):.2f} bits')
    print(f'  Clean full:        {entropy(clean):.2f} bits')

    return drm, clean


print('FASOO DRM MULTI-FILE ANALYSIS')
print('Known-Plaintext Attack Feasibility Study')

drm1, clean1 = analyze_pair('yes_drm.pptx', 'no_drm.pptx', 'PAIR 1: PPTX')
drm2, clean2 = analyze_pair('yes_drm_hwp.hwp', 'no_drm_hwp.hwp', 'PAIR 2: HWP')

# === CROSS-FILE COMPARISON ===
print(f'\n{"="*70}')
print(f'  CROSS-FILE COMPARISON')
print(f'{"="*70}')

# 1. 헤더 비교: 두 DRM 파일의 헤더가 같은 구조인지
print('\n--- Header comparison (PPTX vs HWP) ---')
for off in range(0, 0x44):
    if drm1[off] != drm2[off]:
        print(f'  First diff at 0x{off:02X}: PPTX=0x{drm1[off]:02X} HWP=0x{drm2[off]:02X}')
        break
else:
    print('  Header text (0x00-0x43) is IDENTICAL')

# 2. 헤더 필드 비교
print('\n--- Header fields comparison ---')
for off in range(0x44, 0xA0, 4):
    v1 = struct.unpack('>I', drm1[off:off+4])[0]
    v2 = struct.unpack('>I', drm2[off:off+4])[0]
    if v1 != v2 and (v1 != 0 or v2 != 0):
        print(f'  0x{off:04X}: PPTX={v1:>10,}  HWP={v2:>10,}  {"SAME" if v1==v2 else "DIFF"}')

# 3. 키 후보 영역 비교 (0x174-0x1A0)
print('\n--- Key region comparison (0x174-0x1A0) ---')
kr1 = drm1[0x174:0x1A0]
kr2 = drm2[0x174:0x1A0]
print(f'  PPTX: {kr1.hex()}')
print(f'  HWP:  {kr2.hex()}')
print(f'  Same? {kr1 == kr2}')
if kr1 != kr2:
    xor_keys = bytes(a ^ b for a, b in zip(kr1, kr2))
    print(f'  XOR:  {xor_keys.hex()}')

# 4. 패딩 영역 비교 (0xA0-0x174)
print('\n--- Padding region comparison (0xA0-0x174) ---')
pad1 = drm1[0xA0:0x174]
pad2 = drm2[0xA0:0x174]
print(f'  Same? {pad1 == pad2}')

# 5. 동일 오프셋에서 두 파일의 암호문 패턴 비교
print('\n--- Ciphertext pattern comparison ---')
# clean1[0:16]의 XOR 패턴 vs clean2[0:16]의 XOR 패턴
# 두 파일 모두 0x2D0부터 본문이라 가정
for bstart in [0x174, 0x1A0, 0x2D0]:
    xor1 = bytes(drm1[bstart+i] ^ clean1[i] for i in range(min(32, len(clean1), len(drm1)-bstart)))
    xor2 = bytes(drm2[bstart+i] ^ clean2[i] for i in range(min(32, len(clean2), len(drm2)-bstart)))
    print(f'  offset 0x{bstart:X}:')
    print(f'    PPTX XOR: {xor1.hex()}')
    print(f'    HWP  XOR: {xor2.hex()}')
    same = xor1 == xor2
    print(f'    Same XOR pattern? {same}')
    if not same and len(xor1) == len(xor2):
        match_count = sum(1 for a, b in zip(xor1, xor2) if a == b)
        print(f'    Match: {match_count}/{len(xor1)}')

# 6. 핵심: 키가 헤더의 특정 필드에서 유도되는지
print('\n--- Key derivation hypothesis ---')
# 0x17C에 있는 16바이트가 AES 키?
potential_key_1 = drm1[0x17C:0x18C]
potential_key_2 = drm2[0x17C:0x18C]
print(f'  PPTX 0x17C-0x18C (potential AES key): {potential_key_1.hex()}')
print(f'  HWP  0x17C-0x18C (potential AES key): {potential_key_2.hex()}')
print(f'  Same? {potential_key_1 == potential_key_2}')

# AES-128 복호화 시도 (pycryptodome 필요하지만 없을 수 있으므로 패턴만 분석)
print('\n--- AES ECB mode test (if key is in header) ---')
try:
    from Crypto.Cipher import AES
    for name, drm_data, clean_data, key in [
        ('PPTX', drm1, clean1, potential_key_1),
        ('HWP', drm2, clean2, potential_key_2),
    ]:
        for body_off in [0x174, 0x1A0, 0x2D0]:
            cipher = AES.new(key, AES.MODE_ECB)
            ct_block = drm_data[body_off:body_off+16]
            try:
                pt = cipher.decrypt(ct_block)
                pt_expected = clean_data[:16]
                if pt == pt_expected:
                    print(f'  *** {name} AES-ECB MATCH at 0x{body_off:X}! Key found! ***')
                else:
                    match = sum(1 for a, b in zip(pt, pt_expected) if a == b)
                    if match > 4:
                        print(f'  {name} 0x{body_off:X}: partial match {match}/16')
            except:
                pass
    
    # 키 후보 더 시도: 0x180-0x190, 0x18C-0x19C 등
    print('\n--- Extended AES key search ---')
    for name, drm_data, clean_data in [('PPTX', drm1, clean1), ('HWP', drm2, clean2)]:
        found = False
        for key_off in range(0x174, 0x1A0):
            if key_off + 16 > len(drm_data):
                break
            key = drm_data[key_off:key_off+16]
            for body_off in [0x174, 0x1A0, 0x2D0]:
                for mode_name, mode in [('ECB', AES.MODE_ECB)]:
                    cipher = AES.new(key, mode)
                    ct = drm_data[body_off:body_off+16]
                    pt = cipher.decrypt(ct)
                    if pt == clean_data[:16]:
                        print(f'  *** {name}: KEY at 0x{key_off:X}, body at 0x{body_off:X}, mode={mode_name} ***')
                        print(f'      Key: {key.hex()}')
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if not found:
            print(f'  {name}: No AES-ECB key found in header region')

    # AES-CBC 시도 (IV = 0x00*16)
    print('\n--- AES-CBC with zero IV ---')
    for name, drm_data, clean_data in [('PPTX', drm1, clean1), ('HWP', drm2, clean2)]:
        found = False
        for key_off in range(0x174, 0x1A0):
            if key_off + 16 > len(drm_data):
                break
            key = drm_data[key_off:key_off+16]
            for body_off in [0x174, 0x1A0, 0x2D0]:
                iv = b'\x00' * 16
                cipher = AES.new(key, AES.MODE_CBC, iv=iv)
                ct = drm_data[body_off:body_off+16]
                pt = cipher.decrypt(ct)
                if pt == clean_data[:16]:
                    print(f'  *** {name}: KEY at 0x{key_off:X}, body at 0x{body_off:X}, CBC+zeroIV ***')
                    found = True
                    break
            if found:
                break
        if not found:
            print(f'  {name}: No AES-CBC (zero IV) key found')

except ImportError:
    print('  pycryptodome not installed. Install with: pip install pycryptodome')
    print('  Skipping AES decryption tests.')

print('\n' + '='*70)
print('CONCLUSION')
print('='*70)
