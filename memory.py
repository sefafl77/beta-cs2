# memory.py
import struct
import pymem
from debug import debug
from config import config
from math_utils import Vector3


class MemoryReader:
    """Handle semua memory reading operations"""
    
    def __init__(self, pm: pymem.Pymem, client_base: int, engine_base: int):
        self.pm = pm
        self.client_base = client_base
        self.engine_base = engine_base
        debug.info(f"MemoryReader initialized: client=0x{client_base:X}, engine=0x{engine_base:X}")
    
    def read_vector3(self, address: int) -> Vector3:
        """Read Vector3 from memory"""
        try:
            data = self.pm.read_bytes(address, 12)
            x, y, z = struct.unpack('fff', data)
            return Vector3(x, y, z)
        except Exception as e:
            debug.debug(f"Failed to read vector3 at 0x{address:X}: {e}")
            return Vector3(0, 0, 0)
    
    def read_view_matrix(self) -> list:
        """Read 4x4 view matrix from client.dll"""
        try:
            addr = self.client_base + config.DW_VIEW_MATRIX
            data = self.pm.read_bytes(addr, 64)
            matrix = list(struct.unpack('16f', data))
            
            # Validate
            if all(v == 0.0 for v in matrix):
                debug.warning("View matrix is all zeros")
                return [0.0] * 16
            
            return matrix
        except Exception as e:
            debug.debug(f"Failed to read view matrix: {e}")
            return [0.0] * 16
    
    def get_entity_address(self, index: int) -> int:
        """Get entity pawn address by index"""
        try:
            # Read entity list pointer
            entity_list_addr = self.client_base + config.DW_ENTITY_LIST
            entity_list = self.pm.read_longlong(entity_list_addr)
            
            debug.debug(f"[Entity {index}] EntityList addr: 0x{entity_list_addr:X}, pointer: 0x{entity_list:X}")
            
            if not entity_list or entity_list < 0x1000:
                debug.debug(f"[Entity {index}] Invalid entity list pointer: 0x{entity_list:X}")
                return 0
            
            # Calculate chunk and offset
            chunk_idx = index >> 9  # index / 512
            entity_idx = index & 0x1FF  # index % 512
            
            # Read chunk pointer from entity list
            chunk_addr = entity_list + (8 * chunk_idx) + 16
            chunk_ptr = self.pm.read_longlong(chunk_addr)
            
            debug.debug(f"[Entity {index}] Chunk addr: 0x{chunk_addr:X}, pointer: 0x{chunk_ptr:X}")
            
            if not chunk_ptr or chunk_ptr < 0x1000:
                debug.debug(f"[Entity {index}] Invalid chunk pointer: 0x{chunk_ptr:X}")
                return 0
            
            # Read entity pawn address from chunk
            entity_addr_offset = chunk_ptr + (120 * entity_idx)
            entity_addr = self.pm.read_longlong(entity_addr_offset)
            
            debug.debug(f"[Entity {index}] Entity addr offset: 0x{entity_addr_offset:X}, entity: 0x{entity_addr:X}")
            
            return entity_addr if entity_addr > 0x1000 else 0
            
        except Exception as e:
            debug.debug(f"Failed to get entity {index}: {e}")
            return 0
    
    def get_entity_position(self, entity_addr: int) -> Vector3:
        """Get entity position from address"""
        if not entity_addr:
            return Vector3(0, 0, 0)
        
        try:
            # Read position from entity
            pos = self.read_vector3(entity_addr + config.OFFSET_POSITION)
            return pos
        except Exception as e:
            debug.debug(f"Failed to read entity position: {e}")
            return Vector3(0, 0, 0)
    
    def get_game_resolution(self) -> tuple:
        """Read game resolution from engine2.dll"""
        try:
            width_addr = self.engine_base + config.DW_WINDOW_WIDTH
            height_addr = self.engine_base + config.DW_WINDOW_HEIGHT
            
            width = self.pm.read_uint(width_addr)
            height = self.pm.read_uint(height_addr)
            
            # Validate
            if width < 640 or width > 4096 or height < 480 or height > 2160:
                debug.warning(f"Invalid resolution: {width}x{height}, using default")
                return 1920, 1080
            
            debug.info(f"Game resolution: {width}x{height}")
            return width, height
        except Exception as e:
            debug.warning(f"Failed to read resolution: {e}")
            return 1920, 1080
