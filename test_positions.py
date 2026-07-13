# test_positions.py
"""Scan all entities with offset 0x4e8"""
import pymem
import struct
from config import config

print("[*] Scanning all entities with offset 0x4E8...\n")

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll")
client_base = client.lpBaseOfDll

entity_list_addr = client_base + config.DW_ENTITY_LIST
entity_list_ptr = pm.read_longlong(entity_list_addr)

test_offset = 0x4e8
found = 0

for i in range(1, 65):
    try:
        chunk_idx = i >> 9
        entity_idx = i & 0x1FF
        
        chunk_addr = entity_list_ptr + (8 * chunk_idx) + 16
        chunk_ptr = pm.read_longlong(chunk_addr)
        
        if chunk_ptr < 0x1000:
            continue
        
        entity_addr = pm.read_longlong(chunk_ptr + 120 * entity_idx)
        
        if entity_addr < 0x1000:
            continue
        
        # Try position read
        data = pm.read_bytes(entity_addr + test_offset, 12)
        x, y, z = struct.unpack('fff', data)
        
        # Only print non-zero
        if x != 0 or y != 0 or z != 0:
            dist = (x**2 + y**2 + z**2) ** 0.5
            print(f"[+] Entity {i}: ({x:.2f}, {y:.2f}, {z:.2f}) - Dist: {dist:.1f}m")
            found += 1
    
    except Exception as e:
        pass

print(f"\n[*] Found {found} entities with non-zero positions at offset 0x{test_offset:X}")

if found == 0:
    print("[*] Offset 0x4E8 seems wrong. Let me check config...")
    print(f"[*] Config says: OFFSET_POSITION=0x{config.OFFSET_POSITION:X}")
    print(f"[*] OFFSET_BODY_COMPONENT=0x{config.OFFSET_BODY_COMPONENT:X}")
    print(f"[*] OFFSET_ABS_ORIGIN=0x{config.OFFSET_ABS_ORIGIN:X}")
