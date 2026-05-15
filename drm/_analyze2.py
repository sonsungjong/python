with open('yes_drm.pptx', 'rb') as f:
    drm = f.read()
with open('no_drm.pptx', 'rb') as f:
    clean = f.read()

# offset 0x100에서 시작하면 XOR이 거의 0에 가까움 -> 직접 비교
offset = 0x100  # 256

body = drm[offset:]
print(f'=== DRM[0x100:] vs clean ===')
print(f'body size: {len(body):,}')
print(f'clean size: {len(clean):,}')
print()

# 바이트별 비교
match = 0
total = min(len(body), len(clean))
first_mismatches = []
for i in range(total):
    if body[i] == clean[i]:
        match += 1
    else:
        if len(first_mismatches) < 30:
            first_mismatches.append((i, body[i], clean[i]))

print(f'Match: {match:,} / {total:,} ({match/total*100:.2f}%)')
print(f'Mismatch: {total - match:,}')
print()

if first_mismatches:
    print('First mismatches:')
    for pos, drm_b, clean_b in first_mismatches:
        print(f'  pos {pos:>6} (0x{pos+offset:04X} in DRM): DRM=0x{drm_b:02X} clean=0x{clean_b:02X} XOR=0x{drm_b^clean_b:02X}')

# 본문 XOR 패턴 분석
print()
xor_vals = [body[i] ^ clean[i] for i in range(min(1024, total))]
zero_count = xor_vals.count(0)
print(f'XOR=0 count in first 1024: {zero_count}/1024 ({zero_count/1024*100:.1f}%)')

# 연속 0인 구간 찾기
max_run = 0
cur_run = 0
for x in xor_vals:
    if x == 0:
        cur_run += 1
        max_run = max(max_run, cur_run)
    else:
        cur_run = 0
print(f'Max consecutive XOR=0 run: {max_run}')

# 0x174 offset 테스트
print()
print('=== DRM[0x174:] vs clean ===')
offset2 = 0x174
body2 = drm[offset2:]
match2 = sum(1 for i in range(min(len(body2), len(clean))) if body2[i] == clean[i])
total2 = min(len(body2), len(clean))
print(f'Match: {match2:,} / {total2:,} ({match2/total2*100:.2f}%)')

# 어떤 오프셋이 최적인지 브루트포스
print()
print('=== Brute force: best offset search (check first 64 bytes match) ===')
best_offset = 0
best_match = 0
for try_off in range(0, min(len(drm), 8192)):
    b = drm[try_off:]
    m = sum(1 for i in range(min(64, len(b), len(clean))) if b[i] == clean[i])
    if m > best_match:
        best_match = m
        best_offset = try_off
        if m >= 60:
            print(f'  offset 0x{try_off:04X} ({try_off:>5}): {m}/64 match')
    if m == 64:
        break

print(f'Best: offset 0x{best_offset:04X} ({best_offset}) with {best_match}/64 match')

if best_match >= 60:
    # 전체 비교
    body_best = drm[best_offset:]
    total_best = min(len(body_best), len(clean))
    match_best = sum(1 for i in range(total_best) if body_best[i] == clean[i])
    print(f'Full comparison at best offset: {match_best:,}/{total_best:,} ({match_best/total_best*100:.2f}%)')
    if body_best[:len(clean)] == clean:
        print('*** PERFECT MATCH! ***')
        print(f'DRM header = {best_offset} bytes')
        tail = len(drm) - best_offset - len(clean)
        print(f'DRM tail = {tail} bytes')
