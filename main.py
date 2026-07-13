# main.py - Simple working version
import sys
import pymem
import pygame
import math
import struct
from debug import debug
from config import config
from gui import OverlayGUI
from math_utils import world_to_screen, Vector3


def connect_to_game():
    """Connect to CS2 process"""
    try:
        pm = pymem.Pymem("cs2.exe")
        debug.info("Connected to CS2")
        
        client = pymem.process.module_from_name(pm.process_handle, "client.dll")
        engine = pymem.process.module_from_name(pm.process_handle, "engine2.dll")
        
        debug.info(f"client.dll base: 0x{client.lpBaseOfDll:X}")
        debug.info(f"engine2.dll base: 0x{engine.lpBaseOfDll:X}")
        
        return pm, client.lpBaseOfDll, engine.lpBaseOfDll
    except pymem.exception.ProcessNotFound:
        debug.error("CS2 process not found. Please launch CS2 first.")
        return None, None, None


def read_entity_address(pm, client_base, index):
    """Simple entity address reader"""
    try:
        entity_list = pm.read_longlong(client_base + config.DW_ENTITY_LIST)
        if not entity_list:
            return 0
        
        chunk_idx = index >> 9
        entity_idx = index & 0x1FF
        
        chunk_ptr = pm.read_longlong(entity_list + (8 * chunk_idx) + 16)
        if not chunk_ptr:
            return 0
        
        entity_addr = pm.read_longlong(chunk_ptr + 120 * entity_idx)
        return entity_addr if entity_addr > 0x1000 else 0
    except:
        return 0


def read_vector3(pm, address):
    """Read 3D vector from memory"""
    try:
        data = pm.read_bytes(address, 12)
        x, y, z = struct.unpack('fff', data)
        
        # Validate - floats should be reasonable
        if abs(x) < 100000 and abs(y) < 100000 and abs(z) < 100000:
            return Vector3(x, y, z)
    except:
        pass
    
    return Vector3(0, 0, 0)


def read_view_matrix(pm, client_base):
    """Read view matrix"""
    try:
        addr = client_base + config.DW_VIEW_MATRIX
        data = pm.read_bytes(addr, 64)
        return list(struct.unpack('16f', data))
    except:
        return [0.0] * 16


def get_game_resolution(pm, engine_base):
    """Read game resolution"""
    try:
        width = pm.read_uint(engine_base + config.DW_WINDOW_WIDTH)
        height = pm.read_uint(engine_base + config.DW_WINDOW_HEIGHT)
        
        if 640 < width < 4096 and 480 < height < 2160:
            return width, height
    except:
        pass
    
    return 1920, 1080


def main():
    debug.info("=== CS2 ESP Starting ===")
    
    # Connect
    pm, client_base, engine_base = connect_to_game()
    if not pm:
        sys.exit(1)
    
    # Get resolution
    game_width, game_height = get_game_resolution(pm, engine_base)
    debug.info(f"Game resolution: {game_width}x{game_height}")
    
    # Init GUI
    try:
        gui = OverlayGUI()
    except Exception as e:
        debug.error(f"Failed to initialize GUI: {e}")
        sys.exit(1)
    
    esp_enabled = True
    debug_mode = False
    clock = pygame.time.Clock()
    running = True
    
    debug.info("=== Ready ===")
    debug.info("PageUp = Toggle Menu")
    debug.info("F2 = Exit\n")
    
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    gui.toggle_menu()
                elif event.key == pygame.K_F2:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Left click
                action = gui.handle_click()
                if action == "toggle_esp":
                    esp_enabled = not esp_enabled
                    debug.info(f"ESP: {'ON' if esp_enabled else 'OFF'}")
                elif action == "toggle_debug":
                    debug_mode = not debug_mode
                    debug.info(f"Debug: {'ON' if debug_mode else 'OFF'}")
                elif action == "exit":
                    running = False
        
        gui.clear()
        
        entity_count = 0
        
        # Render ESP
        if esp_enabled:
            try:
                matrix = read_view_matrix(pm, client_base)
                
                # Loop all entities
                for entity_index in range(1, 65):
                    entity_addr = read_entity_address(pm, client_base, entity_index)
                    if not entity_addr:
                        continue
                    
                    # Read position using correct offset
                    pos = read_vector3(pm, entity_addr + config.OFFSET_POSITION)
                    
                    if pos and not pos.is_zero():
                        screen_pos = world_to_screen(pos, matrix, game_width, game_height)
                        
                        if screen_pos:
                            entity_count += 1
                            gui.draw_entity(screen_pos, entity_index)
                            
                            if debug_mode and entity_count <= 3:
                                debug.debug(f"Entity {entity_index}: {pos}")
            except Exception as e:
                debug.debug(f"Render error: {e}")
        
        gui.draw_menu(esp_enabled, entity_count, debug_mode)
        gui.update()
        clock.tick(144)
    
    gui.close()
    debug.info("=== Program closed ===")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        debug.info("Interrupted by user")
    except Exception as e:
        debug.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

import json
import os
import pymem
import pygame
import sys

# Mengambil fungsi dari folder modules yang sudah kita buat tadi
from modules.memory import (
    get_entity_pawn_address,
    get_game_resolution,
    load_offsets,
    read_vector3,
    read_view_matrix,
)
from modules.math3d import calculate_target_angles, world_to_screen
from modules.overlay import init_transparent_overlay

def connect_to_process():
    try:
        # Menghubungkan ke proses CS2
        pm = pymem.Pymem("cs2.exe") 
        client_module = pymem.process.module_from_name(pm.process_handle, "client.dll")
        engine_module = pymem.process.module_from_name(pm.process_handle, "engine2.dll")
        return pm, client_module.lpBaseOfDll, engine_module.lpBaseOfDll
    except pymem.exception.ProcessNotFound:
        print("[Error] Proses target tidak ditemukan. Harap jalankan aplikasi target terlebih dahulu.")
        return None, None, None

def main():
    # 0. Load offset dari JSON (offsets.json)
    try:
        offsets = load_offsets("offsets.json")
        print(f"[OK] Offset dimuat dari cs2-dumpernew/output")
        print(f"[OK] Available keys: {list(offsets['client.dll'].keys())[:5]}...")
    except FileNotFoundError as e:
        print(f"[Error] {e}")
        sys.exit(1)
    
    # 1. Koneksi ke memori aplikasi
    pm, client_base, engine_base = connect_to_process()
    if not pm:
        sys.exit(1)
        
    # 2. Setup Overlay Jendela Grafis Transparan
    screen, screen_w, screen_h = init_transparent_overlay()
    
    # 3. Baca resolusi game dari engine2.dll
    game_width, game_height = get_game_resolution(pm, engine_base)
    print(f"[OK] Game Resolution: {game_width}x{game_height}")
    print(f"[OK] Overlay Resolution: {screen_w}x{screen_h}")
    
    # 4. Setup font untuk menu text
    font_small = pygame.font.Font(None, 18)
    font_menu = pygame.font.Font(None, 24)
    
    # 5. State variables
    esp_enabled = True
    debug_mode = False
    show_distance = True
    entity_count = 0
    
    clock = pygame.time.Clock()
    running = True
    
    print("\n[CONTROLS]")
    print("  PageUp  → Toggle ESP ON/OFF")
    print("  F1      → Toggle Debug Mode")
    print("  F2      → Toggle Distance Display")
    print("  Ctrl+C  → Exit")
    print("\n[STARTING] Sistem telemetri berjalan...\n")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    esp_enabled = not esp_enabled
                    status = 'ON' if esp_enabled else 'OFF'
                    print(f"[TOGGLE] ESP: {status}")
                elif event.key == pygame.K_F1:
                    debug_mode = not debug_mode
                    print(f"[TOGGLE] Debug Mode: {'ON' if debug_mode else 'OFF'}")
                elif event.key == pygame.K_F2:
                    show_distance = not show_distance
                    print(f"[TOGGLE] Distance Display: {'ON' if show_distance else 'OFF'}")
                
        # Reset background (Warna 0,0,0 / Hitam diatur sebagai Transparan di Windows)
        screen.fill((0, 0, 0))
        
        entity_count = 0
        
        # 6. Ekstraksi Data & Proyeksi Real-Time (hanya jika ESP enabled)
        if esp_enabled:
            matrix = read_view_matrix(pm, client_base)
            
            # Membaca entitas dengan range lebih besar (1-64 untuk max player count)
            for entity_index in range(1, 65):
                entity_addr = get_entity_pawn_address(pm, client_base, entity_index)
                if not entity_addr:
                    continue
                    
                # Offset ke m_vecAbsOrigin (0x30 + 0xc8 = 0xf8)
                obj_3d_pos = read_vector3(pm, entity_addr + 0xf8)
                
                # Skip jika posisi 0,0,0 (entity tidak valid/inactive)
                if obj_3d_pos.x == 0.0 and obj_3d_pos.y == 0.0 and obj_3d_pos.z == 0.0:
                    continue
                
                entity_count += 1
                
                # Proyeksi koordinat 3D ke 2D
                screen_coords = world_to_screen(obj_3d_pos, matrix, game_width, game_height)
                
                if screen_coords:
                    x, y = screen_coords
                    
                    # Draw body box (hijau)
                    box_width, box_height = 40, 80
                    pygame.draw.rect(screen, (0, 255, 0), (x - box_width//2, y - box_height//2, box_width, box_height), 2)
                    
                    # Draw head circle (estimasi head 60px dari body)
                    head_y = y - 65
                    pygame.draw.circle(screen, (255, 0, 0), (x, head_y), 15, 2)
                    
                    # Distance display (jika enabled)
                    if show_distance:
                        import math
                        distance = math.sqrt(obj_3d_pos.x**2 + obj_3d_pos.y**2 + obj_3d_pos.z**2)
                        dist_text = font_small.render(f"{distance:.0f}m", True, (0, 255, 255))
                        screen.blit(dist_text, (x - 20, y + 50))
                    
                    # Debug: tampilkan koordinat 3D di overlay
                    if debug_mode:
                        debug_text = f"[{entity_index}] {obj_3d_pos.x:.0f},{obj_3d_pos.y:.0f},{obj_3d_pos.z:.0f}"
                        text_surface = font_small.render(debug_text, True, (255, 255, 0))
                        screen.blit(text_surface, (x - 40, y - 100))
        
        # 7. Render Menu UI
        menu_status = f"ESP: {'ON' if esp_enabled else 'OFF'} | Distance: {'ON' if show_distance else 'OFF'} | Entities: {entity_count}"
        menu_text = font_menu.render(menu_status, True, (0, 255, 0))
        screen.blit(menu_text, (10, 10))
        
        # Info text
        info_text = font_small.render("PageUp=Toggle | F1=Debug | F2=Distance", True, (200, 200, 200))
        screen.blit(info_text, (10, 40))
        
        if debug_mode:
            debug_info = f"Game: {game_width}x{game_height} | Overlay: {screen_w}x{screen_h}"
            debug_text = font_small.render(debug_info, True, (255, 255, 0))
            screen.blit(debug_text, (10, 65))
        
        pygame.display.update()
        clock.tick(144)  # 144 Hz frame rate loop
        
    pygame.quit()
    print("\n[EXIT] Program closed.")

if __name__ == "__main__":
    main()