# gui.py
import pygame
import ctypes
import win32con
import win32gui
from debug import debug


class Button:
    """Clickable button"""
    def __init__(self, x, y, width, height, text, color_text, color_bg, color_hover):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color_text = color_text
        self.color_bg = color_bg
        self.color_hover = color_hover
        self.hovered = False
    
    def draw(self, screen, font):
        """Draw button"""
        color = self.color_hover if self.hovered else self.color_bg
        pygame.draw.rect(screen, color, self.rect, 2)
        
        text_surf = font.render(self.text, True, self.color_text)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def update_hover(self, pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos):
        """Check if clicked"""
        return self.rect.collidepoint(pos)


class OverlayGUI:
    """Pygame overlay untuk ESP - D3D menu style"""
    
    def __init__(self):
        pygame.init()
        
        # Get screen resolution
        self.width = ctypes.windll.user32.GetSystemMetrics(0)
        self.height = ctypes.windll.user32.GetSystemMetrics(1)
        
        debug.info(f"Screen resolution: {self.width}x{self.height}")
        
        # Create overlay window
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        pygame.display.set_caption("CS2 ESP")
        
        # Setup window for transparency + click-through
        self.hwnd = win32gui.GetActiveWindow()
        self._setup_transparency()
        
        # Fonts
        self.font_small = pygame.font.Font(None, 18)
        self.font_menu = pygame.font.Font(None, 24)
        self.font_button = pygame.font.Font(None, 20)
        
        # Colors
        self.COLOR_BG = (0, 0, 0)  # Black (transparent)
        self.COLOR_BOX = (0, 255, 0)  # Green
        self.COLOR_HEAD = (255, 0, 0)  # Red
        self.COLOR_TEXT = (0, 255, 255)  # Cyan
        self.COLOR_MENU = (0, 255, 0)  # Green
        self.COLOR_MENU_BG = (20, 20, 20)  # Dark gray
        self.COLOR_INFO = (200, 200, 200)  # Gray
        self.COLOR_DEBUG = (255, 255, 0)  # Yellow
        self.COLOR_BUTTON = (0, 200, 0)  # Light green
        self.COLOR_BUTTON_HOVER = (0, 255, 0)  # Bright green
        
        # Menu state
        self.menu_visible = False
        
        # Create buttons
        menu_x = 50
        menu_y = 100
        self.btn_esp_toggle = Button(menu_x, menu_y, 120, 40, "ESP: ON", self.COLOR_TEXT, self.COLOR_BUTTON, self.COLOR_BUTTON_HOVER)
        self.btn_debug = Button(menu_x, menu_y + 60, 120, 40, "DEBUG: OFF", self.COLOR_TEXT, self.COLOR_BUTTON, self.COLOR_BUTTON_HOVER)
        self.btn_exit = Button(menu_x, menu_y + 120, 120, 40, "EXIT", self.COLOR_TEXT, self.COLOR_BUTTON, self.COLOR_BUTTON_HOVER)
        
        debug.info("OverlayGUI initialized")
    
    def _setup_transparency(self):
        """Setup pygame window for transparency and click-through"""
        try:
            if self.hwnd:
                existing = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
                new_style = (
                    existing
                    | win32con.WS_EX_LAYERED
                    | win32con.WS_EX_TRANSPARENT
                    | win32con.WS_EX_TOPMOST
                    | win32con.WS_EX_NOACTIVATE
                )
                win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, new_style)
                ctypes.windll.user32.SetLayeredWindowAttributes(self.hwnd, 0, 0, win32con.LWA_COLORKEY)
                debug.info("Transparency setup complete")
        except Exception as e:
            debug.warning(f"Failed to setup transparency: {e}")
    
    def toggle_transparency(self, enable_transparency):
        """Toggle click-through mode"""
        try:
            if self.hwnd:
                existing = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
                
                if enable_transparency:
                    # Enable click-through
                    new_style = existing | win32con.WS_EX_TRANSPARENT
                else:
                    # Disable click-through (allow mouse interaction)
                    new_style = existing & ~win32con.WS_EX_TRANSPARENT
                
                win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, new_style)
        except Exception as e:
            debug.debug(f"Failed to toggle transparency: {e}")
    
    def toggle_menu(self):
        """Toggle menu visibility"""
        self.menu_visible = not self.menu_visible
        self.toggle_transparency(not self.menu_visible)  # Disable transparency when menu is open
        pygame.mouse.set_visible(self.menu_visible)
        debug.info(f"Menu: {'OPEN' if self.menu_visible else 'CLOSED'}")
    
    
    def draw_entity(self, screen_pos, entity_index):
        """Draw entity ESP box"""
        if not screen_pos:
            return
        
        x, y = screen_pos
        
        # Draw box around entity (simple wallhack)
        box_w, box_h = 40, 80
        pygame.draw.rect(self.screen, self.COLOR_BOX, (x - box_w//2, y - box_h//2, box_w, box_h), 2)
    
    def draw_menu_panel(self, esp_enabled, entity_count, debug_mode):
        """Draw interactive menu panel"""
        if not self.menu_visible:
            return
        
        # Draw semi-transparent background
        s = pygame.Surface((280, 200))
        s.set_alpha(180)
        s.fill(self.COLOR_MENU_BG)
        self.screen.blit(s, (40, 90))
        
        # Draw title
        title = self.font_menu.render("CS2 ESP Menu", True, self.COLOR_MENU)
        self.screen.blit(title, (50, 100))
        
        # Update button states
        mouse_pos = pygame.mouse.get_pos()
        self.btn_esp_toggle.update_hover(mouse_pos)
        self.btn_debug.update_hover(mouse_pos)
        self.btn_exit.update_hover(mouse_pos)
        
        # Update button text
        self.btn_esp_toggle.text = f"ESP: {'ON' if esp_enabled else 'OFF'}"
        self.btn_debug.text = f"DEBUG: {'ON' if debug_mode else 'OFF'}"
        
        # Draw buttons
        self.btn_esp_toggle.draw(self.screen, self.font_button)
        self.btn_debug.draw(self.screen, self.font_button)
        self.btn_exit.draw(self.screen, self.font_button)
        
        # Draw info
        info_text = self.font_small.render(f"Entities: {entity_count}", True, self.COLOR_INFO)
        self.screen.blit(info_text, (50, 260))
    
    def draw_hud(self, esp_enabled, entity_count):
        """Draw compact HUD when menu is closed"""
        if self.menu_visible:
            return
        
        status = f"ESP: {'ON' if esp_enabled else 'OFF'} | Entities: {entity_count}"
        text = self.font_menu.render(status, True, self.COLOR_MENU)
        self.screen.blit(text, (10, 10))
        
        info = "PageUp=Menu | F2=Exit"
        text = self.font_small.render(info, True, self.COLOR_INFO)
        self.screen.blit(text, (10, 40))
    
    def draw_menu(self, esp_enabled, entity_count, debug_mode):
        """Draw menu (combined HUD + panel)"""
        self.draw_hud(esp_enabled, entity_count)
        self.draw_menu_panel(esp_enabled, entity_count, debug_mode)
    
    def clear(self):
        """Clear screen"""
        self.screen.fill(self.COLOR_BG)
    
    def update(self):
        """Update display"""
        pygame.display.update()
    
    def get_events(self):
        """Get pygame events"""
        return pygame.event.get()
    
    def handle_click(self):
        """Handle mouse clicks on buttons"""
        if not self.menu_visible:
            return None
        
        mouse_pos = pygame.mouse.get_pos()
        
        if self.btn_esp_toggle.is_clicked(mouse_pos):
            return "toggle_esp"
        elif self.btn_debug.is_clicked(mouse_pos):
            return "toggle_debug"
        elif self.btn_exit.is_clicked(mouse_pos):
            return "exit"
        
        return None
    
    def close(self):
        """Close overlay"""
        pygame.quit()
        debug.info("GUI closed")
