import struct, hashlib, itertools

with open('1.xlsx', 'rb') as f:
    drm1 = f.read()
with open('2.xlsx', 'rb') as f:
    drm2 = f.read()
with open('no_1.xlsx', 'rb') as f:
    clean = f.read()

# 헤더 키 (0x17C-0x19B, 32 bytes)
key1 = drm1[0x17C:0x19C]
key2 = drm2[0x17C:0x19C]

print(f'Key1: {key1.hex()}')
print(f'Key2: {key2.hex()}')
print(f'Clean size: {len(clean)}')

# 키스트림 추출 (DRM body XOR clean)
# body 시작: 0x1A0 (헤더+키+메타 이후)
body_off = 0x1A0
body1 = drm1[body_off:]
ks_len = min(len(body1), len(clean))
keystream = bytes(body1[i] ^ clean[i] for i in range(ks_len))

print(f'\nKeystream (first 64 bytes):')
for i in range(0, 64, 16):
    chunk = keystream[i:i+16]
    print(f'  {i:04X}: {" ".join(f"{b:02X}" for b in chunk)}')

# === TEST 1: keystream = key1 반복? ===
print('\n=== TEST 1: keystream == key1 repeated? ===')
key_repeated = (key1 * (ks_len // len(key1) + 1))[:ks_len]
match = sum(1 for a, b in zip(keystream, key_repeated) if a == b)
print(f'  Match: {match}/{ks_len} ({match/ks_len*100:.1f}%)')

# === TEST 2: keystream = key1 XOR position 기반? ===
print('\n=== TEST 2: keystream[i] = key1[i%32] XOR i? ===')
test = bytes(key1[i % 32] ^ (i & 0xFF) for i in range(ks_len))
match = sum(1 for a, b in zip(keystream, test) if a == b)
print(f'  Match: {match}/{ks_len} ({match/ks_len*100:.1f}%)')

# === TEST 3: keystream = MD5/SHA chain from key? ===
print('\n=== TEST 3: keystream = hash chain? ===')
for hash_name in ['md5', 'sha1', 'sha256']:
    h = hashlib.new(hash_name, key1).digest()
    match = sum(1 for a, b in zip(keystream[:len(h)], h) if a == b)
    print(f'  {hash_name}(key1) vs keystream[0:]: {match}/{len(h)} match')
    
    # hash(key1 + counter)
    h2 = hashlib.new(hash_name, key1 + b'\x00').digest()
    match2 = sum(1 for a, b in zip(keystream[:len(h2)], h2) if a == b)
    print(f'  {hash_name}(key1+0x00) vs keystream[0:]: {match2}/{len(h2)} match')

# === TEST 4: RC4 with key1 as key? ===
print('\n=== TEST 4: RC4 decryption? ===')
def rc4(key, data):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(byte ^ S[(S[i] + S[j]) % 256])
    return bytes(out)

# RC4 decrypt body with key1
for boff in [0x174, 0x1A0, 0x2D0]:
    rc4_result = rc4(key1, drm1[boff:boff+16])
    is_pk = rc4_result[:4] == b'\x50\x4B\x03\x04'
    match = sum(1 for a, b in zip(rc4_result, clean[:16]) if a == b)
    print(f'  RC4(key1, DRM[0x{boff:X}:]): {"PK found!" if is_pk else "no PK"}, match={match}/16')
    if is_pk or match > 8:
        print(f'    Result: {rc4_result.hex()}')

# Also try with different key regions
for kstart in [0x174, 0x17C, 0x184, 0x18C]:
    for klen in [16, 24, 32]:
        if kstart + klen > len(drm1):
            continue
        k = drm1[kstart:kstart+klen]
        for boff in [0x174, 0x1A0, 0x2D0]:
            r = rc4(k, drm1[boff:boff+16])
            if r[:2] == b'\x50\x4B' or r[:4] == clean[:4]:
                print(f'  *** RC4 HIT! key=0x{kstart:X}:{klen}, body=0x{boff:X} => {r[:16].hex()}')

# === TEST 5: AES-ECB with key derived from header? ===
print('\n=== TEST 5: AES with key derivations ===')
try:
    from Crypto.Cipher import AES
    
    # Try various key derivations
    derivations = [
        ('raw key1[0:16]', key1[:16]),
        ('raw key1[16:32]', key1[16:32]),
        ('MD5(key1)', hashlib.md5(key1).digest()),
        ('SHA256(key1)[:16]', hashlib.sha256(key1).digest()[:16]),
        ('key1 XOR key1[16:]', bytes(a ^ b for a, b in zip(key1[:16], key1[16:32]))),
        ('reversed key1[:16]', key1[:16][::-1]),
    ]
    
    for desc, aes_key in derivations:
        for mode_name, mode_fn in [('ECB', lambda k: AES.new(k, AES.MODE_ECB))]:
            cipher = mode_fn(aes_key)
            for boff in [0x174, 0x1A0, 0x2D0]:
                ct = drm1[boff:boff+16]
                pt = cipher.decrypt(ct)
                is_pk = pt[:4] == b'\x50\x4B\x03\x04'
                match = sum(1 for a, b in zip(pt, clean[:16]) if a == b)
                if is_pk or match >= 8:
                    print(f'  *** AES HIT! {desc}, body=0x{boff:X} => {pt.hex()}')
        
        # AES-CBC with zero IV
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=b'\x00'*16)
        for boff in [0x1A0, 0x2D0]:
            ct = drm1[boff:boff+16]
            pt = cipher.decrypt(ct)
            if pt[:4] == b'\x50\x4B\x03\x04':
                print(f'  *** AES-CBC HIT! {desc}, body=0x{boff:X} => {pt.hex()}')
    
    # Try using OTHER header regions as IV
    print('\n  --- AES with header-derived IV ---')
    for key_off in [0x17C]:
        aes_key = drm1[key_off:key_off+16]
        for iv_off in [0x18C, 0x21C, 0x2D8]:
            if iv_off + 16 > len(drm1):
                continue
            iv = drm1[iv_off:iv_off+16]
            cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
            for boff in [0x1A0, 0x2D0, 0x313]:
                ct = drm1[boff:boff+16]
                pt = cipher.decrypt(ct)
                if pt[:2] == b'\x50\x4B' or pt[:4] == clean[:4]:
                    print(f'  *** key=0x{key_off:X}, iv=0x{iv_off:X}, body=0x{boff:X} => {pt.hex()}')
    
except ImportError:
    print('  pycryptodome not installed')

# === TEST 6: Simple operations between key and keystream ===
print('\n=== TEST 6: Key-Keystream relationship ===')
# Check if keystream[i] = f(key1[i%32]) for some simple f
for i in range(min(32, ks_len)):
    kb = key1[i % 32]
    ksb = keystream[i]
    print(f'  pos {i:>2}: key=0x{kb:02X} ks=0x{ksb:02X} xor=0x{kb^ksb:02X} sum=0x{(kb+ksb)&0xFF:02X} diff=0x{(ksb-kb)&0xFF:02X}')

# Check if XOR of key and keystream is constant
xor_vals = [key1[i%32] ^ keystream[i] for i in range(min(256, ks_len))]
print(f'\n  key XOR keystream unique values (first 256): {len(set(xor_vals))}')

# Check if keystream is key + some constant per block
print('\n=== TEST 7: Block-wise key relationship ===')
for block in range(0, min(256, ks_len), 32):
    ks_block = keystream[block:block+32]
    if len(ks_block) < 32:
        break
    xor_with_key = bytes(a ^ b for a, b in zip(ks_block, key1))
    all_same = len(set(xor_with_key)) == 1
    print(f'  block {block//32}: ks_xor_key = {xor_with_key[:16].hex()}... {"CONSTANT!" if all_same else ""}')
