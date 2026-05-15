import struct, os

def hexdump(data, n=64):
    lines = []
    for i in range(0, min(len(data), n), 16):
        chunk = data[i:i+16]
        h = ' '.join(f'{b:02X}' for b in chunk)
        a = ''.join(chr(b) if 32<=b<127 else '.' for b in chunk)
        lines.append(f'    {i:04X}: {h:<48}  {a}')
    return '\n'.join(lines)

# Load all files
pairs = {
    'XLSX': ('1.xlsx', 'no_1.xlsx'),
    'PPTX': ('yes_drm.pptx', 'no_drm.pptx'),
    'HWP':  ('yes_drm_hwp.hwp', 'no_drm_hwp.hwp'),
}
extras = ['2.xlsx', '3.xlsx']

data = {}
for name in list(sum(pairs.values(), ())) + extras:
    if os.path.isfile(name):
        with open(name, 'rb') as f:
            data[name] = f.read()

print('='*70)
print('  COMPREHENSIVE FASOO DRM PATTERN ANALYSIS')
print('='*70)

# ============================================================
# PART 1: Identical/Different region map (1.xlsx vs 2.xlsx vs 3.xlsx)
# ============================================================
print('\n' + '='*70)
print('  PART 1: BYTE-LEVEL SAME/DIFF MAP (1.xlsx vs 2.xlsx)')
print('='*70)

d1 = data['1.xlsx']
d2 = data['2.xlsx']
d3 = data['3.xlsx']

cmp_len = min(len(d1), len(d2))

# Build same/diff map
regions = []
current_same = (d1[0] == d2[0])
start = 0
for i in range(1, cmp_len):
    is_same = (d1[i] == d2[i])
    if is_same != current_same:
        regions.append((start, i-1, current_same))
        start = i
        current_same = is_same
regions.append((start, cmp_len-1, current_same))

print(f'\nTotal regions: {len(regions)}')
print(f'{"Start":>8} {"End":>8} {"Size":>8}  {"Type":>6}  First 16 bytes (1.xlsx)')
print('-'*80)
same_total = 0
diff_total = 0
for rstart, rend, is_same in regions:
    size = rend - rstart + 1
    rtype = 'SAME' if is_same else '>>DIFF'
    if is_same:
        same_total += size
    else:
        diff_total += size
    preview = d1[rstart:rstart+16]
    ph = ' '.join(f'{b:02X}' for b in preview[:8])
    print(f'  0x{rstart:04X}  0x{rend:04X}  {size:>6}   {rtype}  {ph}')

print(f'\n  SAME total: {same_total:,} bytes ({same_total/cmp_len*100:.1f}%)')
print(f'  DIFF total: {diff_total:,} bytes ({diff_total/cmp_len*100:.1f}%)')

# Also check 1 vs 3
same_13 = sum(1 for i in range(cmp_len) if d1[i] == d3[i])
print(f'\n  1 vs 3: SAME={same_13:,}/{cmp_len:,} ({same_13/cmp_len*100:.1f}%)')

# ============================================================
# PART 2: Segment table for each file type
# ============================================================
print('\n' + '='*70)
print('  PART 2: SEGMENT TABLE PER FILE')
print('='*70)

seg_info = {}
for label, (drm_name, _) in pairs.items():
    drm = data[drm_name]
    segs = []
    for i in range(0x74, 0xA0, 8):
        seg_off = struct.unpack('>I', drm[i:i+4])[0]
        seg_size = struct.unpack('>I', drm[i+4:i+8])[0]
        if seg_off > 0 and seg_size > 0:
            segs.append((seg_off, seg_size))
    seg_info[label] = segs
    print(f'\n  {label} ({drm_name}: {len(drm):,} bytes, clean: {len(data[pairs[label][1]]):,} bytes)')
    for seg_off, seg_size in segs:
        seg_end = seg_off + seg_size
        print(f'    Seg: 0x{seg_off:04X} - 0x{seg_end:04X} (size={seg_size})')

# ============================================================
# PART 3: Keystream extraction from XLSX pair, apply to ALL
# ============================================================
print('\n' + '='*70)
print('  PART 3: KEYSTREAM CROSS-FILE APPLICATION')
print('='*70)

# Extract keystream from 1.xlsx <-> no_1.xlsx at offset 0x1A0
xlsx_drm = data['1.xlsx']
xlsx_clean = data['no_1.xlsx']
body_off = 0x1A0
ks_len = min(len(xlsx_drm) - body_off, len(xlsx_clean))
keystream_xlsx = bytes(xlsx_drm[body_off+i] ^ xlsx_clean[i] for i in range(ks_len))

print(f'\n  XLSX keystream extracted: {ks_len} bytes (from offset 0x1A0)')

# Apply to 2.xlsx, 3.xlsx
for name in ['2.xlsx', '3.xlsx']:
    drm = data[name]
    body = drm[body_off:]
    dec_len = min(len(body), ks_len, len(xlsx_clean))
    decrypted = bytes(body[i] ^ keystream_xlsx[i] for i in range(dec_len))
    match = sum(1 for i in range(dec_len) if decrypted[i] == xlsx_clean[i])
    print(f'\n  {name}: match={match}/{dec_len} ({match/dec_len*100:.1f}%)')
    # Map which blocks match
    block_size = 256
    print(f'    Block-level match (block={block_size}):')
    for blk in range(0, dec_len, block_size):
        blk_end = min(blk + block_size, dec_len)
        blk_match = sum(1 for i in range(blk, blk_end) if decrypted[i] == xlsx_clean[i])
        pct = blk_match / (blk_end - blk) * 100
        bar = '#' * int(pct/5) + '.' * (20 - int(pct/5))
        clean_off = blk
        print(f'      clean[0x{clean_off:04X}]: [{bar}] {pct:5.1f}%')

# Extract keystream from PPTX pair
pptx_drm = data['yes_drm.pptx']
pptx_clean = data['no_drm.pptx']
ks_pptx_len = min(len(pptx_drm) - body_off, len(pptx_clean))
keystream_pptx = bytes(pptx_drm[body_off+i] ^ pptx_clean[i] for i in range(ks_pptx_len))

# Cross-apply: XLSX keystream -> PPTX
print(f'\n  XLSX keystream -> PPTX:')
pptx_body = pptx_drm[body_off:]
cross_len = min(len(pptx_body), ks_len, len(pptx_clean))
cross_dec = bytes(pptx_body[i] ^ keystream_xlsx[i] for i in range(cross_len))
cross_match = sum(1 for i in range(cross_len) if cross_dec[i] == pptx_clean[i])
print(f'    match={cross_match}/{cross_len} ({cross_match/cross_len*100:.1f}%)')
print(f'    First 32 bytes: {cross_dec[:32].hex()}')

# Cross-apply: PPTX keystream -> XLSX
print(f'\n  PPTX keystream -> 1.xlsx:')
xlsx_body = xlsx_drm[body_off:]
cross_len2 = min(len(xlsx_body), ks_pptx_len, len(xlsx_clean))
cross_dec2 = bytes(xlsx_body[i] ^ keystream_pptx[i] for i in range(cross_len2))
cross_match2 = sum(1 for i in range(cross_len2) if cross_dec2[i] == xlsx_clean[i])
print(f'    match={cross_match2}/{cross_len2} ({cross_match2/cross_len2*100:.1f}%)')

# ============================================================
# PART 4: DIFF regions deep analysis - is there a key relationship?
# ============================================================
print('\n' + '='*70)
print('  PART 4: DIFF REGION KEY RELATIONSHIP')
print('='*70)

# For each DIFF region between 1.xlsx and 2.xlsx,
# check if there's a constant XOR between them
for rstart, rend, is_same in regions:
    if is_same:
        continue
    size = rend - rstart + 1
    if size < 4:
        continue
    
    chunk1 = d1[rstart:rend+1]
    chunk2 = d2[rstart:rend+1]
    xor_vals = bytes(a ^ b for a, b in zip(chunk1, chunk2))
    
    # Check if constant XOR
    unique_xor = len(set(xor_vals))
    
    # Check if repeating pattern
    best_period = None
    for period in [1, 2, 4, 8, 16, 32]:
        if period >= size:
            break
        pattern = xor_vals[:period]
        matches = sum(1 for i in range(0, size - period, period) 
                     if xor_vals[i:i+period] == pattern)
        total = max(1, (size - period) // period)
        if matches / total > 0.9:
            best_period = period
            break
    
    print(f'\n  DIFF 0x{rstart:04X}-0x{rend:04X} ({size} bytes):')
    print(f'    Unique XOR values: {unique_xor}/256')
    if best_period:
        print(f'    *** Repeating XOR pattern (period={best_period}): {xor_vals[:best_period].hex()} ***')
    elif unique_xor <= 3:
        from collections import Counter
        c = Counter(xor_vals)
        print(f'    Few unique XORs: {[(f"0x{v:02X}", cnt) for v, cnt in c.most_common()]}')
    else:
        # Show first few XOR bytes
        print(f'    XOR[0:16]: {xor_vals[:16].hex()}')

# ============================================================
# PART 5: Does segment table position correlate with diff/same regions?
# ============================================================
print('\n' + '='*70)
print('  PART 5: SEGMENT TABLE vs SAME/DIFF REGIONS')
print('='*70)

xlsx_segs = seg_info['XLSX']
print('\n  XLSX segment boundaries:')
for seg_off, seg_size in xlsx_segs:
    seg_end = seg_off + seg_size
    print(f'    0x{seg_off:04X} - 0x{seg_end:04X}')

print('\n  DIFF regions:')
for rstart, rend, is_same in regions:
    if not is_same:
        size = rend - rstart + 1
        # Check which segment this falls into
        in_seg = None
        for seg_off, seg_size in xlsx_segs:
            if rstart >= seg_off and rend < seg_off + seg_size:
                in_seg = f'Seg@0x{seg_off:X}'
                break
        print(f'    0x{rstart:04X}-0x{rend:04X} ({size:>5} bytes) {in_seg or "outside segments"}')
