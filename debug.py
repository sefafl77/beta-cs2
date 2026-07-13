# debug.py
import sys
from datetime import datetime

class DebugLevel:
    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3

class Debug:
    """Simple debug logging system"""
    
    def __init__(self, level=DebugLevel.DEBUG):
        self.level = level
        self.enabled = True
    
    def _format_msg(self, level_name, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] [{level_name:8}] {msg}"
    
    def error(self, msg):
        if self.enabled:
            print(self._format_msg("ERROR", msg), file=sys.stderr)
    
    def warning(self, msg):
        if self.enabled and self.level >= DebugLevel.WARNING:
            print(self._format_msg("WARN", msg))
    
    def info(self, msg):
        if self.enabled and self.level >= DebugLevel.INFO:
            print(self._format_msg("INFO", msg))
    
    def debug(self, msg):
        if self.enabled and self.level >= DebugLevel.DEBUG:
            print(self._format_msg("DEBUG", msg))
    
    def set_level(self, level):
        self.level = level

# Global instance
debug = Debug(DebugLevel.DEBUG)
