# radar_ui.py
"""
Radar/minimap UI for future use
Currently unused but kept for extensibility
"""

class RadarUI:
    def __init__(self, gui):
        self.gui = gui
        self.enabled = False
    
    def draw(self, entities):
        """Draw radar on screen"""
        if not self.enabled:
            return
        
        # TODO: Implement radar rendering
        pass
