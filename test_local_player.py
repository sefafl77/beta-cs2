# test_local_player.py
"""Test reading local player to find correct position offset"""
import pymem
import struct
from config import config

print("[*] Testing local player reading...\n")

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll")
client_base = client.lpBaseOfDll

# Read local player pawn
local_player_addr = client_base + config.DW_LOCAL_PLAYER_PAWN
print(f"[+] DW_LOCAL_PLAYER_PAWN offset: 0x{config.DW_LOCAL_PLAYER_PAWN:X}")
print(f"[+] Address: 0x{local_player_addr:X}")

try:
    local_player_ptr = pm.read_longlong(local_player_addr)
    print(f"[+] Local player pointer: 0x{local_player_ptr:X}\n")
    
    if local_player_ptr > 0x1000:
        # Try different position offsets on local player
        offsets_to_try = [0xf8, 0x80, 0xc8, 0x130, 0x4e8, 0x568, 0x700, 0x1224]
        
        print("Testing position offsets on local player:\n")
        
        for offset in offsets_to_try:
            try:
                data = pm.read_bytes(local_player_ptr + offset, 12)
                x, y, z = struct.unpack('fff', data)
                
                # Check if reasonable
                if abs(x) < 100000 and abs(y) < 100000 and abs(z) < 100000:
                    dist = (x**2 + y**2 + z**2) ** 0.5
                    print(f"[+] Offset 0x{offset:03X}: ({x:10.2f}, {y:10.2f}, {z:10.2f}) - Dist: {dist:.1f}m")
                else:
                    print(f"[-] Offset 0x{offset:03X}: Out of range")
            except:
                print(f"[-] Offset 0x{offset:03X}: Read error")
    else:
        print(f"[-] Invalid local player pointer")

except Exception as e:
    print(f"[-] Error: {e}")
