# config.py
import json
import os

class Config:
    """Centralize semua offset dan konfigurasi"""
    
    def __init__(self):
        self.offsets = self._load_offsets()
        self.classes = self._load_classes()
        
    def _load_offsets(self):
        """Load dari cs2-dumpernew"""
        dump_path = os.path.join("cs2-dumpernew", "output", "offsets.json")
        root_path = "offsets.json"
        
        path = dump_path if os.path.exists(dump_path) else root_path
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Offset file not found: {path}")
        
        with open(path) as f:
            return json.load(f)
    
    def _load_classes(self):
        """Load class definitions dari client_dll.json"""
        dump_path = os.path.join("cs2-dumpernew", "output", "client_dll.json")
        root_path = "client_dll.json"
        
        path = dump_path if os.path.exists(dump_path) else root_path
        
        if not os.path.exists(path):
            return {}
        
        with open(path) as f:
            data = json.load(f)
        return data.get("client.dll", {}).get("classes", {})
    
    # client.dll offsets
    @property
    def DW_ENTITY_LIST(self):
        return self.offsets["client.dll"]["dwEntityList"]
    
    @property
    def DW_VIEW_MATRIX(self):
        return self.offsets["client.dll"]["dwViewMatrix"]
    
    @property
    def DW_LOCAL_PLAYER_PAWN(self):
        return self.offsets["client.dll"]["dwLocalPlayerPawn"]
    
    @property
    def DW_LOCAL_PLAYER_CONTROLLER(self):
        return self.offsets["client.dll"]["dwLocalPlayerController"]
    
    # engine2.dll offsets
    @property
    def DW_WINDOW_WIDTH(self):
        return self.offsets["engine2.dll"]["dwWindowWidth"]
    
    @property
    def DW_WINDOW_HEIGHT(self):
        return self.offsets["engine2.dll"]["dwWindowHeight"]
    
    # Class field offsets
    def get_field_offset(self, class_name, field_name):
        """Get field offset dari class definition"""
        if class_name not in self.classes:
            return None
        
        fields = self.classes[class_name].get("fields", {})
        return fields.get(field_name)
    
    @property
    def OFFSET_BODY_COMPONENT(self):
        """C_BaseEntity.m_CBodyComponent"""
        return self.get_field_offset("C_BaseEntity", "m_CBodyComponent") or 0x30
    
    @property
    def OFFSET_ABS_ORIGIN(self):
        """CGameSceneNode.m_vecAbsOrigin"""
        return self.get_field_offset("CGameSceneNode", "m_vecAbsOrigin") or 0xc8
    
    @property
    def OFFSET_POSITION(self):
        """Entity position offset - empirically verified as 0x2E8"""
        return 0x2E8


# Global instance
config = Config()
