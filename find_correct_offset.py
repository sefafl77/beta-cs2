# find_correct_offset.py
"""Find correct entity position offset by testing all entities"""
import pymem
import struct
from config import config

print("[*] Finding correct entity position offset...\n")

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll")
client_base = client.lpBaseOfDll

entity_list_addr = client_base + config.DW_ENTITY_LIST
entity_list_ptr = pm.read_longlong(entity_list_addr)

# Offsets to test (common ones)
test_offsets = [
    0x80, 0xc8, 0xf8, 0x130, 0x180, 0x200, 0x280, 0x300,
    0x4e8, 0x568, 0x700, 0x800, 0x900, 0x1000, 0x1224,
    0x1320, 0x1400, 0x1500, 0x1600, 0x1800
]

offset_scores = {}

for offset in test_offsets:
    valid_count = 0
    valid_positions = []
    
    for entity_index in range(1, 65):
        try:
            chunk_idx = entity_index >> 9
            entity_idx = entity_index & 0x1FF
            
            chunk_addr = entity_list_ptr + (8 * chunk_idx) + 16
            chunk_ptr = pm.read_longlong(chunk_addr)
            
            if chunk_ptr < 0x1000:
                continue
            
            entity_addr = pm.read_longlong(chunk_ptr + 120 * entity_idx)
            
            if entity_addr < 0x1000:
                continue
            
            # Try to read position
            try:
                data = pm.read_bytes(entity_addr + offset, 12)
                x, y, z = struct.unpack('fff', data)
                
                # Check if reasonable
                if abs(x) < 100000 and abs(y) < 100000 and abs(z) < 100000:
                    if not (x == 0 and y == 0 and z == 0):
                        valid_count += 1
                        if len(valid_positions) < 3:
                            valid_positions.append((entity_index, x, y, z))
            except:
                pass
        except:
            pass
    
    if valid_count > 0:
        offset_scores[offset] = (valid_count, valid_positions)

# Sort by score
sorted_offsets = sorted(offset_scores.items(), key=lambda x: x[1][0], reverse=True)

print(f"Found {len(sorted_offsets)} offsets with valid positions:\n")

for offset, (count, positions) in sorted_offsets[:10]:
    print(f"[+] Offset 0x{offset:04X}: {count} valid entities")
    for entity_idx, x, y, z in positions:
        dist = (x**2 + y**2 + z**2) ** 0.5
        print(f"    Entity {entity_idx}: ({x:10.2f}, {y:10.2f}, {z:10.2f}) dist={dist:.1f}")
    print()

if sorted_offsets:
    best_offset = sorted_offsets[0][0]
    print(f"[*] BEST OFFSET: 0x{best_offset:04X}")
