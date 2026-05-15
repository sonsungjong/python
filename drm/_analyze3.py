import struct

with open('yes_drm.pptx', 'rb') as f:
    drm = f.read()
with open('no_drm.pptx', 'rb') as f:
    clean = f.read()

print(f'DRM:   {len(drm):,} bytes (0x{len(drm):X})')
print(f'Clean: {len(clean):,} bytes (0x{len(clean):X})')
print(f'Diff:  {len(drm)-len(clean):,} bytes')
print()

# DRM 헤더 구조 상세 분석
print('=== DRM Header Structure ===')
print(f'0x00-0x01: Magic byte 0x{drm[0]:02X}')
print(f'0x01-0x42: "{drm[1:0x42].decode("ascii", errors="replace")}"')

# 헤더 필드 분석 (Big Endian)
print()
print('=== Header Fields (Big Endian u32) ===')
fields = {}
for off in range(0x44, 0xA0, 4):
    val = struct.unpack('>I', drm[off:off+4])[0]
    if val != 0:
        fields[off] = val
        print(f'  0x{off:04X}: {val:>10,} (0x{val:08X})')

# DRM 헤더 영역에서 clean 파일 크기가 적혀있는지 확인
print()
print(f'=== Searching for clean file size ({len(clean)}) in DRM header ===')
clean_size_be = struct.pack('>I', len(clean))
clean_size_le = struct.pack('<I', len(clean))
for i in range(min(len(drm), 1024)):
    if drm[i:i+4] == clean_size_be:
        print(f'  Found (BE) at offset 0x{i:04X}')
    if drm[i:i+4] == clean_size_le:
        print(f'  Found (LE) at offset 0x{i:04X}')

# DRM body size search
drm_body_size = len(drm) - 256  # possible body after 0x100 header
print(f'=== Searching for body sizes in header ===')
for candidate in [len(clean), len(drm)-len(clean), len(drm)]:
    for i in range(0, 256):
        be_val = struct.unpack('>I', drm[i:i+4])[0] if i+4 <= len(drm) else 0
        le_val = struct.unpack('<I', drm[i:i+4])[0] if i+4 <= len(drm) else 0
        if be_val == candidate:
            print(f'  0x{i:04X}: {candidate:,} (BE) - matches {"clean_size" if candidate==len(clean) else "diff" if candidate==len(drm)-len(clean) else "drm_size"}')
        if le_val == candidate:
            print(f'  0x{i:04X}: {candidate:,} (LE) - matches {"clean_size" if candidate==len(clean) else "diff" if candidate==len(drm)-len(clean) else "drm_size"}')

# 암호화 구간 분석
# DRM 0xA0 이후에 반복되는 0xFF 패턴 -> 패딩 영역
# 0x175 이후에 데이터 시작 -> 실제 암호화된 본문?
print()
print('=== Encryption region analysis ===')

# 0xA0-0x160 구간: 패딩 (0x00...0xFF 반복)
padding_end = 0
for i in range(0xA0, len(drm)):
    if drm[i] != 0x00 and drm[i] != 0xFF:
        padding_end = i
        break
print(f'Padding (00/FF) ends at: 0x{padding_end:04X} ({padding_end})')

# 0x160 이후 실제 데이터 시작점
for i in range(0x160, min(0x200, len(drm))):
    if drm[i] != 0x00:
        print(f'Non-zero data starts at: 0x{i:04X} ({i})')
        break

# 세그먼트 분석: 헤더의 오프셋/크기 필드 해석
print()
print('=== Segment table interpretation ===')
# 0x74: 0x174 (372) - 아마 첫 번째 세그먼트 시작
# 0x78: 0x15C (348) - 첫 번째 세그먼트 크기?
# 0x84: 0x2D0 (720) - 두 번째 세그먼트 시작?
# 0x88: 0xAD0 (2768) - 두 번째 세그먼트 크기?
# 0x94: 0xDA0 (3488) - 세 번째 세그먼트 시작?
# 0x98: 0x8BC (2236) - 세 번째 세그먼트 크기?
segments = [
    (0x74, 0x78),
    (0x84, 0x88),
    (0x94, 0x98),
]
for off_off, size_off in segments:
    seg_off = struct.unpack('>I', drm[off_off:off_off+4])[0]
    seg_size = struct.unpack('>I', drm[size_off:size_off+4])[0]
    print(f'  Segment: offset=0x{seg_off:X} ({seg_off}), size=0x{seg_size:X} ({seg_size})')
    print(f'    DRM[{seg_off}:{seg_off+32}] = {drm[seg_off:seg_off+32].hex()}')
    # 해당 구간과 clean 비교
    if seg_off < len(clean):
        c = clean[seg_off:seg_off+32]
        d = drm[seg_off:seg_off+32]
        xor = bytes(a^b for a,b in zip(d, c))
        print(f'    clean[{seg_off}:{seg_off+32}]  = {c.hex()}')
        print(f'    XOR = {xor.hex()}')

# 엔트로피 분석: 구간별 바이트 분포
print()
print('=== Entropy by region (DRM file) ===')
import math
def entropy(data):
    if not data:
        return 0
    freq = [0]*256
    for b in data:
        freq[b] += 1
    ent = 0
    n = len(data)
    for f in freq:
        if f > 0:
            p = f / n
            ent -= p * math.log2(p)
    return ent

regions = [
    ('Header 0x00-0xFF', drm[0:0x100]),
    ('Padding 0x100-0x174', drm[0x100:0x174]),
    ('Meta 0x174-0x1A0', drm[0x174:0x1A0]),
    ('Body 0x1A0-end', drm[0x1A0:]),
]
for name, data in regions:
    print(f'  {name}: entropy={entropy(data):.2f} bits, len={len(data)}')

print()
print('=== Clean file entropy ===')
print(f'  Full: entropy={entropy(clean):.2f} bits')
