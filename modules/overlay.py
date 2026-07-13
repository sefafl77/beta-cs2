import ctypes

import pygame
import win32con
import win32gui


def init_transparent_overlay():
    """
    Buat overlay window yang fully transparent dan click-through.
    Tidak akan mengambil focus dari game.
    """
    pygame.init()
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)

    # Buat pygame window full-screen tanpa frame
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
    hwnd = win32gui.GetActiveWindow()  # Get overlay window handle
    
    if not hwnd:
        hwnd = win32gui.FindWindow(None, pygame.display.get_surface().get_flags().__str__())
    
    # Konfigurasi window style untuk transparency + click-through + always on top
    existing_styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    
    # Add: LAYERED (enable transparency), TRANSPARENT (click-through), TOPMOST (always on top), NOACTIVATE (tidak grab focus)
    new_style = (
        existing_styles
        | win32con.WS_EX_LAYERED        # Enable color transparency
        | win32con.WS_EX_TRANSPARENT    # Pass all mouse/keyboard to window below
        | win32con.WS_EX_TOPMOST        # Always on top
        | win32con.WS_EX_NOACTIVATE     # Don't activate window when clicked
    )
    
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
    
    # Set color key: 0,0,0 (black) = transparent
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_COLORKEY)
    
    # Extra: Pastikan CS2 tetap in focus dengan membuat overlay non-activated
    try:
        cs2_window = win32gui.FindWindow(None, "CS2")
        if not cs2_window:
            cs2_window = win32gui.FindWindow(None, "Counter-Strike 2")
        if cs2_window:
            win32gui.SetForegroundWindow(cs2_window)
    except:
        pass
    
    return screen, width, height