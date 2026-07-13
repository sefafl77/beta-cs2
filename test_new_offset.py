# test_new_offset.py
"""Test with derived position offset"""
import pymem
import struct
from config import config

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll")
client_base = client.lpBaseOfDll

entity_list_addr = client_base + config.DW_ENTITY_LIST
entity_list_ptr = pm.read_longlong(entity_list_addr)

print("[*] Testing derived position offsets...\n")

# Test both direct offset and pointer chain
test_cases = [
    ("Direct 0x38", 0x38, False),
    ("Direct 0x100", 0x100, False),
    ("Pointer chain: 0x38 -> +0xC8", 0x38, True),
]

for name, offset, is_pointer in test_cases:
    valid_count = 0
    examples = []
    
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
            
            if is_pointer:
                # Read pointer, dereference, then read position
                ptr_addr = pm.read_longlong(entity_addr + offset)
                if ptr_addr > 0x1000:
                    data = pm.read_bytes(ptr_addr + 0xC8, 12)
                else:
                    continue
            else:
                # Direct read
                data = pm.read_bytes(entity_addr + offset, 12)
            
            x, y, z = struct.unpack('fff', data)
            
            if abs(x) < 100000 and abs(y) < 100000 and abs(z) < 100000:
                mag = abs(x) + abs(y) + abs(z)
                if mag > 0.01:
                    valid_count += 1
                    if len(examples) < 3:
                        dist = (x**2 + y**2 + z**2) ** 0.5
                        examples.append((entity_index, x, y, z, dist))
        except:
            pass
    
    print(f"[*] {name}: {valid_count} entities")
    for ent, x, y, z, d in examples:
        print(f"    E{ent}: ({x:8.1f}, {y:8.1f}, {z:8.1f}) dist={d:.1f}")
    print()
