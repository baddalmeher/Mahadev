import os
import sys
import math
import random

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
except NameError:
    pass

import pygame
from PIL import Image
IMAGE_PATH = "shivji.jpg"
PHRASE = ["ॐ", "गं", "ग", "ण", "प", "त", "ये", "न", "मो", "न", "मः"]


BACKGROUND_COLOR = (10, 10, 12)  
TEXT_COLOR = (240, 240, 255)     
PROCESSING_WIDTH = 130 
def get_best_devanagari_font(target_size):
 
    try:
        fonts_dir = "/system/fonts/"
        if os.path.exists(fonts_dir):
            for f in os.listdir(fonts_dir):
                if "devanagari" in f.lower() and f.endswith(".ttf"):
                    return pygame.font.Font(os.path.join(fonts_dir, f), target_size)
    except:
        pass

   
    android_paths = [
        "/system/fonts/DroidSansFallback.ttf",
        "/system/fonts/NotoSans-Regular.ttf"
    ]
    for path in android_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, target_size)
            except:
                pass
    for font_name in ['notosansdevanagari', 'mangal', 'aparajita', 'freesans']:
        match = pygame.font.match_font(font_name)
        if match:
            try:
                return pygame.font.Font(match, target_size)
            except:
                pass
    return pygame.font.SysFont(None, target_size)

def process_image_for_screen(screen_w, screen_h):
    if not os.path.exists(IMAGE_PATH):
        return None, None, f"ERROR: Cannot find '{IMAGE_PATH}'"

    try:
        img = Image.open(IMAGE_PATH).convert("L")
    except Exception as e:
        return None, None, f"ERROR loading image: {e}"

    orig_w, orig_h = img.size
    margin = 0.05
    avail_w = screen_w * (1 - margin)
    avail_h = screen_h * (1 - margin)

    scale = min(avail_w / orig_w, avail_h / orig_h)
    draw_w = orig_w * scale
    draw_h = orig_h * scale

    proc_w = min(PROCESSING_WIDTH, int(screen_w / 6)) 
    proc_h = int(proc_w * (orig_h / orig_w))

    img_small = img.resize((proc_w, proc_h), Image.Resampling.LANCZOS)
    threshold = 150
    dark_pixels = []
    
    for y in range(proc_h):
        for x in range(proc_w):
            if img_small.getpixel((x, y)) < threshold:
                dark_pixels.append((x, y))

    start_x = (screen_w - draw_w) / 2
    start_y = (screen_h - draw_h) / 2
    step_x = draw_w / proc_w
    step_y = draw_h / proc_h

    font_size = int(max(step_x, step_y) * 1.6)

    mapped_coordinates = []
    for x, y in dark_pixels:
        screen_x = start_x + (x * step_x)
        screen_y = start_y + (y * step_y)
        mapped_coordinates.append((screen_x, screen_y))

    random.shuffle(mapped_coordinates)
    return mapped_coordinates, font_size, None

def show_debug_error_screen(screen, screen_w, screen_h, error_msg):
    screen.fill((50, 0, 0))
    cwd = os.getcwd()
    try:
        files = os.listdir('.')
        file_list = ", ".join(files[:6]) + ("..." if len(files) > 6 else "")
    except Exception as e:
        file_list = "Cannot read directory."

    font = pygame.font.SysFont(None, max(24, int(screen_w * 0.03)))
    messages = [
        error_msg, "", f"Looking in folder: {cwd}",
        f"Files found here: {file_list}", "",
        "SOLUTION: Save this script and your image", "in the EXACT SAME folder."
    ]
    
    start_y = screen_h // 3
    for i, msg in enumerate(messages):
        color = (255, 100, 100) if "ERROR" in msg else (200, 200, 200)
        surf = font.render(msg, True, color)
        rect = surf.get_rect(center=(screen_w // 2, start_y + (i * 40)))
        screen.blit(surf, rect)
        
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                waiting = False

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_w, screen_h = screen.get_size()
    
    mapped_pixels, font_size, error_msg = process_image_for_screen(screen_w, screen_h)
    
    if error_msg:
        show_debug_error_screen(screen, screen_w, screen_h, error_msg)
        pygame.quit()
        sys.exit()

    font = get_best_devanagari_font(font_size)
    cached_characters = []
    for char in PHRASE:
        surf = font.render(char, True, TEXT_COLOR)
        cached_characters.append(surf)

    clock = pygame.time.Clock()
    total_pixels = len(mapped_pixels)
    drawn_count = 0
    state = "ANIMATING"
    
    TARGET_SECONDS = 16.5
    FPS = 60
    TOTAL_FRAMES = TARGET_SECONDS * FPS 
    
    batch_p1 = max(1, int((total_pixels * 0.10) / (TOTAL_FRAMES * 0.20))) 
    batch_p2 = max(1, int((total_pixels * 0.45) / (TOTAL_FRAMES * 0.40))) 
    batch_p3 = max(1, int((total_pixels * 0.45) / (TOTAL_FRAMES * 0.40))) 
    
    phase1_end = int(total_pixels * 0.10)
    phase2_end = int(total_pixels * 0.55) 
    
    screen.fill(BACKGROUND_COLOR)
    pygame.display.flip()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r: 
                    drawn_count = 0
                    screen.fill(BACKGROUND_COLOR)
                    pygame.display.flip()
                    state = "ANIMATING"
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if state == "FINISHED":
                    drawn_count = 0
                    screen.fill(BACKGROUND_COLOR)
                    pygame.display.flip()
                    state = "ANIMATING"
                elif state == "ANIMATING":
                    drawn_count = total_pixels - 1 

        if state == "ANIMATING":
            if drawn_count < total_pixels:
                
                if drawn_count < phase1_end:
                    batch_size = batch_p1    
                elif drawn_count < phase2_end:
                    batch_size = batch_p2   
                else:
                    batch_size = batch_p3   
                
                update_rects = []
                for _ in range(batch_size):
                    if drawn_count >= total_pixels:
                        break
                        
                    px, py = mapped_pixels[drawn_count]
                    char_surf = random.choice(cached_characters)
                    
                    rect = char_surf.get_rect(center=(px, py))
                    screen.blit(char_surf, rect)
                    update_rects.append(rect)
                    
                    drawn_count += 1
                
                if update_rects:
                    pygame.display.update(update_rects)
                clock.tick(FPS) 
                
            else:
                state = "FINISHED"
                ui_font = pygame.font.SysFont(None, max(24, int(screen_h * 0.025)))
                msg_surf = ui_font.render("@Baddalmeher", True, (100, 100, 100))
                msg_rect = msg_surf.get_rect(center=(screen_w // 2, screen_h - max(40, int(screen_h * 0.05))))
                screen.blit(msg_surf, msg_rect)
                pygame.display.update(msg_rect)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
