import struct
from collections import Counter

def hexdump(data, n=128):
    lines = []
    for i in range(0, min(len(data), n), 16):
        chunk = data[i:i+16]
        h = ' '.join(f'{b:02X}' for b in chunk)
        a = ''.join(chr(b) if 32<=b<127 else '.' for b in chunk)
        lines.append(f'  {i:04X}: {h:<48}  {a}')
    return '\n'.join(lines)

# 파일 로드
files = {}
for name in ['1.xlsx', '2.xlsx', '3.xlsx', 'no_1.xlsx']:
    with open(name, 'rb') as f:
        files[name] = f.read()

drm1 = files['1.xlsx']
drm2 = files['2.xlsx']
drm3 = files['3.xlsx']
clean = files['no_1.xlsx']

print('='*70)
print('  FASOO DRM: SAME-CONTENT MULTI-FILE ANALYSIS')
print('='*70)

# 1. 기본 크기
print('\n--- File sizes ---')
for name, data in files.items():
    print(f'  {name}: {len(data):>10,} bytes')
print(f'  1.xlsx - no_1.xlsx diff: {len(drm1)-len(clean):,} bytes')
print(f'  2.xlsx - no_1.xlsx diff: {len(drm2)-len(clean):,} bytes')
print(f'  3.xlsx - no_1.xlsx diff: {len(drm3)-len(clean):,} bytes')

# 2. DRM 헤더 비교 (3개 DRM 파일)
print('\n--- DRM Header comparison (0x00-0x43: magic text) ---')
print(f'  1 vs 2: {"SAME" if drm1[:0x44]==drm2[:0x44] else "DIFF"}')
print(f'  1 vs 3: {"SAME" if drm1[:0x44]==drm3[:0x44] else "DIFF"}')
print(f'  2 vs 3: {"SAME" if drm2[:0x44]==drm3[:0x44] else "DIFF"}')

# 3. 설정 영역 비교 (0x44-0x9F)
print('\n--- Config fields (0x44-0x9F) ---')
print(f'  1 vs 2: {"SAME" if drm1[0x44:0xA0]==drm2[0x44:0xA0] else "DIFF"}')
print(f'  1 vs 3: {"SAME" if drm1[0x44:0xA0]==drm3[0x44:0xA0] else "DIFF"}')

# 4. 패딩 영역 비교 (0xA0-0x174)
print('\n--- Padding (0xA0-0x174) ---')
print(f'  1 vs 2: {"SAME" if drm1[0xA0:0x174]==drm2[0xA0:0x174] else "DIFF"}')
print(f'  1 vs 3: {"SAME" if drm1[0xA0:0x174]==drm3[0xA0:0x174] else "DIFF"}')

# 5. ★ 키 영역 비교 (0x174-0x1A0) ★
print('\n--- KEY REGION (0x174-0x1A0) ---')
kr1 = drm1[0x174:0x1A0]
kr2 = drm2[0x174:0x1A0]
kr3 = drm3[0x174:0x1A0]
print(f'  1.xlsx: {kr1.hex()}')
print(f'  2.xlsx: {kr2.hex()}')
print(f'  3.xlsx: {kr3.hex()}')
print(f'  1 vs 2: {"*** SAME KEY! ***" if kr1==kr2 else "DIFFERENT"}')
print(f'  1 vs 3: {"*** SAME KEY! ***" if kr1==kr3 else "DIFFERENT"}')
print(f'  2 vs 3: {"*** SAME KEY! ***" if kr2==kr3 else "DIFFERENT"}')

# 6. ★ 전체 DRM 파일 비교 ★
print('\n--- Full DRM file comparison ---')
print(f'  1 vs 2: {"IDENTICAL!" if drm1==drm2 else "DIFFERENT"}')
print(f'  1 vs 3: {"IDENTICAL!" if drm1==drm3 else "DIFFERENT"}')
print(f'  2 vs 3: {"IDENTICAL!" if drm2==drm3 else "DIFFERENT"}')

# 7. 바이트별 상세 비교 (1 vs 2)
if drm1 != drm2:
    print('\n--- Byte-by-byte: 1.xlsx vs 2.xlsx ---')
    cmp_len = min(len(drm1), len(drm2))
    diffs = []
    for i in range(cmp_len):
        if drm1[i] != drm2[i]:
            diffs.append(i)
    print(f'  Total different bytes: {len(diffs)} / {cmp_len}')
    if len(diffs) <= 100:
        print(f'  Different positions: {[f"0x{d:X}" for d in diffs[:50]]}')
        # 차이 구간 요약
        if diffs:
            print(f'  First diff: 0x{diffs[0]:X}')
            print(f'  Last diff: 0x{diffs[-1]:X}')
            # 연속 구간
            ranges = []
            start = diffs[0]
            prev = diffs[0]
            for d in diffs[1:]:
                if d == prev + 1:
                    prev = d
                else:
                    ranges.append((start, prev))
                    start = d
                    prev = d
            ranges.append((start, prev))
            print(f'  Diff ranges: {[(f"0x{s:X}-0x{e:X}", e-s+1) for s, e in ranges]}')
    else:
        print(f'  First 20 diff positions: {[f"0x{d:X}" for d in diffs[:20]]}')
        # 차이가 시작되는 영역
        print(f'  First diff at: 0x{diffs[0]:X}')
        # 연속 구간 분석
        ranges = []
        start = diffs[0]
        prev = diffs[0]
        for d in diffs[1:]:
            if d == prev + 1:
                prev = d
            else:
                ranges.append((start, prev))
                start = d
                prev = d
            if len(ranges) > 20:
                break
        ranges.append((start, prev))
        print(f'  First diff ranges: {[(f"0x{s:X}-0x{e:X}", e-s+1) for s, e in ranges[:20]]}')

# 8. ★ 핵심: 키스트림 추출 및 교차 적용 ★
print('\n' + '='*70)
print('  KEYSTREAM CROSS-APPLICATION TEST')
print('='*70)

# 1.xlsx의 키스트림 추출 (가능한 body 시작점)
for body_off in [0x174, 0x1A0, 0x2D0]:
    body1 = drm1[body_off:]
    cmp_len = min(len(body1), len(clean))
    if cmp_len < 16:
        continue
    
    # 키스트림 = DRM XOR clean
    keystream1 = bytes(a ^ b for a, b in zip(body1[:cmp_len], clean[:cmp_len]))
    
    # 이 키스트림을 2.xlsx, 3.xlsx에 적용
    for other_name, other_drm in [('2.xlsx', drm2), ('3.xlsx', drm3)]:
        other_body = other_drm[body_off:]
        other_len = min(len(other_body), cmp_len)
        
        # 키스트림 적용 → 복호화 시도
        decrypted = bytes(a ^ b for a, b in zip(other_body[:other_len], keystream1[:other_len]))
        
        # 결과가 clean과 같은지 확인
        match_with_clean = (decrypted[:len(clean)] == clean[:other_len])
        
        # PK 시그니처 확인
        has_pk = decrypted[:4] == b'\x50\x4B\x03\x04'
        
        # 일치율
        match_count = sum(1 for a, b in zip(decrypted[:min(other_len, len(clean))], clean[:min(other_len, len(clean))]) if a == b)
        match_pct = match_count / min(other_len, len(clean)) * 100
        
        print(f'\n  body_off=0x{body_off:X}: 1.xlsx keystream -> {other_name}')
        print(f'    Decrypted starts with PK? {has_pk}')
        print(f'    Match with clean: {match_count}/{min(other_len, len(clean))} ({match_pct:.1f}%)')
        if match_with_clean:
            print(f'    *** PERFECT MATCH! KEYSTREAM REUSE CONFIRMED! ***')
        elif has_pk:
            print(f'    PK signature found! Partial success.')
            print(f'    First 64 bytes:')
            print(hexdump(decrypted, 64))

# 9. 암호문 직접 비교 (본문 영역)
print('\n' + '='*70)
print('  CIPHERTEXT DIRECT COMPARISON (body region)')
print('='*70)
for body_off in [0x1A0, 0x2D0]:
    b1 = drm1[body_off:body_off+64]
    b2 = drm2[body_off:body_off+64]
    b3 = drm3[body_off:body_off+64]
    print(f'\n  At 0x{body_off:X}:')
    print(f'    1.xlsx: {b1[:32].hex()}')
    print(f'    2.xlsx: {b2[:32].hex()}')
    print(f'    3.xlsx: {b3[:32].hex()}')
    print(f'    1==2? {b1==b2}  1==3? {b1==b3}  2==3? {b2==b3}')
