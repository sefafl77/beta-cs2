# test_entities.py
"""Test multiple entities"""
import pymem
import struct
from config import config

print("[*] Scanning entities for valid positions...\n")

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll")
client_base = client.lpBaseOfDll

entity_list_addr = client_base + config.DW_ENTITY_LIST
entity_list_ptr = pm.read_longlong(entity_list_addr)

# Try different offsets
offsets_to_try = [0xf8, 0x80, 0xc8, 0x130, 0x4e8, 0x568, 0x700]

print("Testing different offsets on entity 1:\n")

for test_offset in offsets_to_try:
    try:
        chunk_ptr = pm.read_longlong(entity_list_ptr + 16)
        entity_addr = pm.read_longlong(chunk_ptr)
        
        if entity_addr > 0x1000:
            data = pm.read_bytes(entity_addr + test_offset, 12)
            x, y, z = struct.unpack('fff', data)
            
            # Check if values are reasonable (between -100000 and 100000)
            if abs(x) < 100000 and abs(y) < 100000 and abs(z) < 100000:
                dist = (x**2 + y**2 + z**2) ** 0.5
                if dist > 0:  # Not all zeros
                    print(f"[+] Offset 0x{test_offset:02X}: ({x:.2f}, {y:.2f}, {z:.2f}) - Dist: {dist:.1f}m")
            else:
                print(f"[-] Offset 0x{test_offset:02X}: Values too large - {(x, y, z)}")
    except Exception as e:
        print(f"[-] Offset 0x{test_offset:02X}: Error - {e}")

