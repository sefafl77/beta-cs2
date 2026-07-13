# find_nonzero_positions.py
"""Find offset dengan actual non-zero positions"""
import pymem
import struct
from config import config

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll")
client_base = client.lpBaseOfDll

entity_list_addr = client_base + config.DW_ENTITY_LIST
entity_list_ptr = pm.read_longlong(entity_list_addr)

# Test key offsets more thoroughly
test_offsets = [0x80, 0xc8, 0xf8, 0x130, 0x4e8, 0x568, 0x700, 0x900, 0x1224]

print("[*] Scanning for NON-ZERO positions...\n")

for offset in test_offsets:
    nonzero_count = 0
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
            
            data = pm.read_bytes(entity_addr + offset, 12)
            x, y, z = struct.unpack('fff', data)
            
            # Check for non-zero
            if abs(x) < 100000 and abs(y) < 100000 and abs(z) < 100000:
                mag = abs(x) + abs(y) + abs(z)
                if mag > 0.01:  # Not exactly zero
                    nonzero_count += 1
                    if len(examples) < 5:
                        dist = (x**2 + y**2 + z**2) ** 0.5
                        examples.append((entity_index, x, y, z, dist))
        except:
            pass
    
    if nonzero_count > 0:
        print(f"[+] Offset 0x{offset:04X}: {nonzero_count} non-zero")
        for ent, x, y, z, d in examples:
            print(f"    E{ent}: ({x:8.1f}, {y:8.1f}, {z:8.1f}) dist={d:.1f}")
        print()

print("[*] Checking if any entity has non-zero velocity or other data...")

# Maybe position is in velocity/velocity_drift field?
# Try reading at different intervals
for entity_index in range(1, 65):
    try:
        chunk_idx = entity_index >> 9
        entity_idx = entity_index & 0x1FF
        
        chunk_addr = entity_list_ptr + (8 * chunk_idx) + 16
        chunk_ptr = pm.read_longlong(chunk_addr)
        
        if chunk_ptr > 0x1000:
            entity_addr = pm.read_longlong(chunk_ptr + 120 * entity_idx)
            
            if entity_addr > 0x1000:
                # Read first 128 bytes and scan for 3 floats with high magnitude
                data = pm.read_bytes(entity_addr, 128)
                
                for i in range(0, 128-12, 4):
                    try:
                        vals = struct.unpack('fff', data[i:i+12])
                        x, y, z = vals
                        
                        if (abs(x) > 100 and abs(x) < 100000 and
                            abs(y) > 100 and abs(y) < 100000 and
                            abs(z) > 100 and abs(z) < 100000):
                            
                            dist = (x**2 + y**2 + z**2) ** 0.5
                            print(f"[+] Entity {entity_index} at offset 0x{i:02X}: ({x:.1f}, {y:.1f}, {z:.1f}) dist={dist:.1f}")
                    except:
                        pass
    except:
        pass
