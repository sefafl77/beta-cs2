# modules/memory.py
import json
import os
import pymem
import struct


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


def load_offsets(json_path: str = "offsets.json") -> dict:
    """
    Load offset dari offsets.json
    Coba dari folder dump baru terlebih dahulu, fallback ke root
    
    Args:
        json_path: Path ke file offsets.json
    
    Returns:
        Dictionary berisi offset dari semua DLL
    """
    # Try new dump folder first
    new_dump_path = os.path.join("cs2-dumpernew", "output", "offsets.json")
    if os.path.exists(new_dump_path):
        json_path = new_dump_path
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File {json_path} tidak ditemukan")
    
    with open(json_path, 'r') as f:
        return json.load(f)


# Load offset dari JSON
_OFFSETS = load_offsets()
DW_ENTITY_LIST = _OFFSETS["client.dll"]["dwEntityList"]
DW_VIEW_MATRIX = _OFFSETS["client.dll"]["dwViewMatrix"]
DW_WINDOW_WIDTH = _OFFSETS["engine2.dll"]["dwWindowWidth"]
DW_WINDOW_HEIGHT = _OFFSETS["engine2.dll"]["dwWindowHeight"]


def get_entity_pawn_address(pm: pymem.Pymem, client_base: int, index: int) -> int:
    try:
        entity_list = pm.read_longlong(client_base + DW_ENTITY_LIST)
        if not entity_list:
            return 0

        # Menggunakan rumus chunk index baris
        chunk_ptr = pm.read_longlong(entity_list + (8 * (index >> 9)) + 16)
        if not chunk_ptr:
            return 0

        entity_pawn = pm.read_longlong(chunk_ptr + 120 * (index & 0x1FF))
        return entity_pawn
    except pymem.exception.MemoryReadError:
        return 0


def read_vector3(pm: pymem.Pymem, address: int) -> Vector3:
    try:
        data = pm.read_bytes(address, 12)  # 3 * float (4 bytes) = 12 bytes
        x, y, z = struct.unpack('fff', data)
        return Vector3(x, y, z)
    except (pymem.exception.MemoryReadError, struct.error):
        return Vector3(0.0, 0.0, 0.0)


def read_view_matrix(pm: pymem.Pymem, client_base: int) -> list:
    try:
        data = pm.read_bytes(client_base + DW_VIEW_MATRIX, 64)  # 16 * float = 64 bytes
        return list(struct.unpack('16f', data))
    except pymem.exception.MemoryReadError:
        return [0.0] * 16


def get_game_resolution(pm: pymem.Pymem, engine_base: int) -> tuple:
    """
    Baca resolusi game dari engine2.dll
    
    Args:
        pm: Pymem instance
        engine_base: Base address engine2.dll
    
    Returns:
        (width, height) dari game window
    """
    try:
        width_ptr = pm.read_uint(engine_base + DW_WINDOW_WIDTH)
        height_ptr = pm.read_uint(engine_base + DW_WINDOW_HEIGHT)
        
        # Validate
        if width_ptr < 640 or width_ptr > 4096 or height_ptr < 480 or height_ptr > 2160:
            return 1920, 1080  # Fallback
        
        return width_ptr, height_ptr
    except:
        return 1920, 1080  # Fallback default