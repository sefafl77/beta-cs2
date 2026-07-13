# test_offset.py
"""
Simple debug script untuk test offset dan entity reading
"""
import pymem
import struct
from config import config
from debug import debug

print("[*] Testing CS2 Offset Reading\n")

# Connect
try:
    pm = pymem.Pymem("cs2.exe")
    print("[+] Connected to CS2")
except:
    print("[-] CS2 not found")
    exit()

# Get modules
try:
    client = pymem.process.module_from_name(pm.process_handle, "client.dll")
    engine = pymem.process.module_from_name(pm.process_handle, "engine2.dll")
    print(f"[+] client.dll: 0x{client.lpBaseOfDll:X}")
    print(f"[+] engine2.dll: 0x{engine.lpBaseOfDll:X}\n")
except Exception as e:
    print(f"[-] Error getting modules: {e}")
    exit()

client_base = client.lpBaseOfDll
engine_base = engine.lpBaseOfDll

# Test resolution read
print("[*] Testing game resolution read...")
try:
    width_val = pm.read_uint(engine_base + config.DW_WINDOW_WIDTH)
    height_val = pm.read_uint(engine_base + config.DW_WINDOW_HEIGHT)
    print(f"[+] Resolution: {width_val}x{height_val}\n")
except Exception as e:
    print(f"[-] Failed: {e}\n")

# Test view matrix read
print("[*] Testing view matrix read...")
try:
    matrix_addr = client_base + config.DW_VIEW_MATRIX
    matrix_data = pm.read_bytes(matrix_addr, 64)
    matrix = list(struct.unpack('16f', matrix_data))
    print(f"[+] Matrix addr: 0x{matrix_addr:X}")
    print(f"[+] First 4 values: {matrix[:4]}")
    print(f"[+] Matrix valid: {not all(v == 0.0 for v in matrix)}\n")
except Exception as e:
    print(f"[-] Failed: {e}\n")

# Test entity list read
print("[*] Testing entity list reading...")
try:
    entity_list_addr = client_base + config.DW_ENTITY_LIST
    print(f"[+] EntityList offset: 0x{config.DW_ENTITY_LIST:X}")
    print(f"[+] EntityList addr: 0x{entity_list_addr:X}")
    
    entity_list_ptr = pm.read_longlong(entity_list_addr)
    print(f"[+] EntityList pointer: 0x{entity_list_ptr:X}")
    
    if entity_list_ptr < 0x1000:
        print(f"[-] Invalid pointer!\n")
    else:
        print(f"[+] Pointer valid\n")
        
        # Try to read first entity
        print("[*] Testing first entity read...")
        chunk_addr = entity_list_ptr + 16
        chunk_ptr = pm.read_longlong(chunk_addr)
        print(f"[+] Chunk addr: 0x{chunk_addr:X}")
        print(f"[+] Chunk pointer: 0x{chunk_ptr:X}")
        
        if chunk_ptr > 0x1000:
            # Try to read entity address
            entity_addr = pm.read_longlong(chunk_ptr)
            print(f"[+] First entity addr: 0x{entity_addr:X}")
            
            if entity_addr > 0x1000:
                # Try to read position
                pos_addr = entity_addr + config.OFFSET_POSITION
                pos_data = pm.read_bytes(pos_addr, 12)
                x, y, z = struct.unpack('fff', pos_data)
                print(f"[+] First entity position: ({x:.2f}, {y:.2f}, {z:.2f})")
except Exception as e:
    print(f"[-] Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n[*] Done")
