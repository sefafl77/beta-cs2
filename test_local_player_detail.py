# test_local_player_detail.py
"""Test all offsets on local player to find position"""
import pymem
import struct
from config import config

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll")
client_base = client.lpBaseOfDll

# Read local player pawn
local_player_addr = client_base + config.DW_LOCAL_PLAYER_PAWN
local_player_ptr = pm.read_longlong(local_player_addr)

print(f"[*] Local player pawn: 0x{local_player_ptr:X}\n")

if local_player_ptr > 0x1000:
    # Scan entire entity for positions with high magnitude
    try:
        entity_data = pm.read_bytes(local_player_ptr, 4096)
        
        print("[*] Scanning for position-like floats (magnitude 50-10000)...\n")
        
        positions_found = {}
        
        # Scan every 4-byte alignment for 3 floats
        for i in range(0, 4000, 4):
            try:
                vals = struct.unpack('fff', entity_data[i:i+12])
                x, y, z = vals
                
                if (not (-0.0 == x == 0.0) and  # Not exactly zero
                    not any(v != v for v in vals) and  # Not NaN
                    abs(x) < 50000 and abs(y) < 50000 and abs(z) < 50000):
                    
                    mag = (x**2 + y**2 + z**2) ** 0.5
                    
                    # Interest in positions that are "somewhere on map"
                    if 0.1 < mag < 10000:
                        if mag not in positions_found:
                            positions_found[mag] = []
                        positions_found[mag].append((i, x, y, z))
            except:
                pass
        
        # Sort by magnitude
        for mag in sorted(positions_found.keys(), reverse=True)[:15]:
            entries = positions_found[mag]
            for offset, x, y, z in entries[:2]:
                print(f"[+] Offset 0x{offset:03X}: ({x:10.2f}, {y:10.2f}, {z:10.2f}) mag={mag:.1f}")
    
    except Exception as e:
        print(f"[-] Error: {e}")
else:
    print("[-] Invalid local player pointer")
