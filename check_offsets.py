# check_offsets.py
import json

# Load offsets
with open('cs2-dumpernew/output/offsets.json', 'r') as f:
    offsets_data = json.load(f)

# Load class definitions
with open('cs2-dumpernew/output/client_dll.json', 'r') as f:
    client_data = json.load(f)

# Find C_BaseEntity class
base_entity = None
for cls in client_data['classes']:
    if cls['name'] == 'C_BaseEntity':
        base_entity = cls
        break

if base_entity:
    print("[+] C_BaseEntity found")
    print(f"[+] Size: 0x{base_entity['size']:X}\n")
    
    # Find body component offset
    body_comp = None
    for field in base_entity['fields']:
        if 'CBodyComponent' in field['type']:
            body_comp = field
            break
    
    if body_comp:
        print(f"[+] m_CBodyComponent offset: 0x{body_comp['offset']:X}")
        print(f"[+] Type: {body_comp['type']}\n")
    
    # Look for common position fields
    print("[*] Position-related fields:")
    for field in base_entity['fields']:
        field_name = field['name']
        if 'position' in field_name.lower() or 'origin' in field_name.lower() or 'vec' in field_name.lower():
            print(f"[+] {field_name} @ 0x{field['offset']:X}: {field['type']}")
else:
    print("[-] C_BaseEntity not found")

# Check offsets
print("\n[*] Global offsets:")
if 'client.dll' in offsets_data:
    for key, val in offsets_data['client.dll'].items():
        if 'position' in key.lower() or 'entity' in key.lower():
            print(f"[+] {key}: {val}")

print(f"\n[*] dwLocalPlayerPawn: {offsets_data['client.dll'].get('dwLocalPlayerPawn', 'N/A')}")
print(f"[*] dwEntityList: {offsets_data['client.dll'].get('dwEntityList', 'N/A')}")
