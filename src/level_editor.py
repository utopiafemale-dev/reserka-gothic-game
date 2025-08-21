#!/usr/bin/env python3
"""
Reserka Gothic - Level Editor
A visual editor for creating custom levels
"""

import pygame
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Initialize Pygame
pygame.init()

# Configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRID_SIZE = 20
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

class EditMode(Enum):
    PLATFORM = "platform"
    ENEMY = "enemy"
    SPAWN = "spawn"
    ERASE = "erase"

class EnemyType(Enum):
    FIRE_SKULL = "fire_skull"
    DEMON = "demon"
    HELL_HOUND = "hell_hound"

class LevelEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Reserka Gothic - Level Editor")
        self.clock = pygame.time.Clock()
        
        # Editor state
        self.mode = EditMode.PLATFORM
        self.current_enemy = EnemyType.FIRE_SKULL
        self.grid_visible = True
        self.snap_to_grid = True
        
        # Level data
        self.platforms = []
        self.enemies = []
        self.player_spawn = (100, 500)
        
        # UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Mouse state
        self.mouse_pressed = False
        self.drag_start = None
        self.drag_end = None
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
    def snap_to_grid_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Snap position to grid if enabled"""
        x, y = pos
        if self.snap_to_grid:
            x = (x // GRID_SIZE) * GRID_SIZE
            y = (y // GRID_SIZE) * GRID_SIZE
        return x, y
    
    def world_to_screen(self, world_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        x, y = world_pos
        return x - self.camera_x, y - self.camera_y
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
        x, y = screen_pos
        return x + self.camera_x, y + self.camera_y
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Mode switching
                if event.key == pygame.K_1:
                    self.mode = EditMode.PLATFORM
                elif event.key == pygame.K_2:
                    self.mode = EditMode.ENEMY
                elif event.key == pygame.K_3:
                    self.mode = EditMode.SPAWN
                elif event.key == pygame.K_4:
                    self.mode = EditMode.ERASE
                
                # Enemy type cycling
                elif event.key == pygame.K_TAB and self.mode == EditMode.ENEMY:
                    enemy_types = list(EnemyType)
                    current_index = enemy_types.index(self.current_enemy)
                    self.current_enemy = enemy_types[(current_index + 1) % len(enemy_types)]
                
                # Toggle options
                elif event.key == pygame.K_g:
                    self.grid_visible = not self.grid_visible
                elif event.key == pygame.K_s:
                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        self.save_level()
                    else:
                        self.snap_to_grid = not self.snap_to_grid
                elif event.key == pygame.K_l and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.load_level()
                elif event.key == pygame.K_c and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.clear_level()
                
                # Camera movement
                elif event.key == pygame.K_LEFT:
                    self.camera_x -= 50
                elif event.key == pygame.K_RIGHT:
                    self.camera_x += 50
                elif event.key == pygame.K_UP:
                    self.camera_y -= 50
                elif event.key == pygame.K_DOWN:
                    self.camera_y += 50
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_pressed = True
                    world_pos = self.screen_to_world(event.pos)
                    world_pos = self.snap_to_grid_pos(world_pos)
                    
                    if self.mode == EditMode.PLATFORM:
                        self.drag_start = world_pos
                    elif self.mode == EditMode.ENEMY:
                        self.add_enemy(world_pos)
                    elif self.mode == EditMode.SPAWN:
                        self.player_spawn = world_pos
                    elif self.mode == EditMode.ERASE:
                        self.erase_at_position(world_pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.mouse_pressed:
                    self.mouse_pressed = False
                    if self.mode == EditMode.PLATFORM and self.drag_start:
                        world_pos = self.screen_to_world(event.pos)
                        world_pos = self.snap_to_grid_pos(world_pos)
                        self.add_platform(self.drag_start, world_pos)
                    self.drag_start = None
                    self.drag_end = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed and self.mode == EditMode.PLATFORM and self.drag_start:
                    world_pos = self.screen_to_world(event.pos)
                    self.drag_end = self.snap_to_grid_pos(world_pos)
        
        return True
    
    def add_platform(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """Add a platform between two points"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Ensure positive width and height
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Minimum size
        if width < GRID_SIZE:
            width = GRID_SIZE
        if height < GRID_SIZE:
            height = GRID_SIZE
        
        self.platforms.append({
            'x': x,
            'y': y,
            'width': width,
            'height': height
        })
    
    def add_enemy(self, pos: Tuple[int, int]):
        """Add an enemy at the given position"""
        x, y = pos
        self.enemies.append({
            'x': x,
            'y': y,
            'type': self.current_enemy.value
        })
    
    def erase_at_position(self, pos: Tuple[int, int]):
        """Erase objects at the given position"""
        x, y = pos
        
        # Remove platforms
        self.platforms = [p for p in self.platforms 
                         if not (p['x'] <= x <= p['x'] + p['width'] and 
                                p['y'] <= y <= p['y'] + p['height'])]
        
        # Remove enemies (with some tolerance)
        tolerance = 30
        self.enemies = [e for e in self.enemies
                       if not (abs(e['x'] - x) <= tolerance and abs(e['y'] - y) <= tolerance)]
    
    def save_level(self):
        """Save the current level to a JSON file"""
        level_data = {
            'platforms': self.platforms,
            'enemies': self.enemies,
            'player_spawn': self.player_spawn
        }
        
        levels_dir = Path(__file__).parent.parent / "levels"
        levels_dir.mkdir(exist_ok=True)
        
        filename = levels_dir / "custom_level.json"
        with open(filename, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        print(f"Level saved to {filename}")
    
    def load_level(self):
        """Load a level from a JSON file"""
        levels_dir = Path(__file__).parent.parent / "levels"
        filename = levels_dir / "custom_level.json"
        
        if filename.exists():
            with open(filename, 'r') as f:
                level_data = json.load(f)
            
            self.platforms = level_data.get('platforms', [])
            self.enemies = level_data.get('enemies', [])
            self.player_spawn = tuple(level_data.get('player_spawn', (100, 500)))
            
            print(f"Level loaded from {filename}")
        else:
            print("No custom level file found")
    
    def clear_level(self):
        """Clear the current level"""
        self.platforms.clear()
        self.enemies.clear()
        self.player_spawn = (100, 500)
        print("Level cleared")
    
    def draw_grid(self):
        """Draw the editing grid"""
        if not self.grid_visible:
            return
        
        # Calculate visible grid range
        start_x = (self.camera_x // GRID_SIZE) * GRID_SIZE
        start_y = (self.camera_y // GRID_SIZE) * GRID_SIZE
        end_x = start_x + SCREEN_WIDTH + GRID_SIZE
        end_y = start_y + SCREEN_HEIGHT + GRID_SIZE
        
        # Draw vertical lines
        for x in range(start_x, end_x, GRID_SIZE):
            screen_x = x - self.camera_x
            pygame.draw.line(self.screen, GRAY, (screen_x, 0), (screen_x, SCREEN_HEIGHT))
        
        # Draw horizontal lines
        for y in range(start_y, end_y, GRID_SIZE):
            screen_y = y - self.camera_y
            pygame.draw.line(self.screen, GRAY, (0, screen_y), (SCREEN_WIDTH, screen_y))
    
    def draw_platforms(self):
        """Draw all platforms"""
        for platform in self.platforms:
            screen_pos = self.world_to_screen((platform['x'], platform['y']))
            rect = pygame.Rect(screen_pos[0], screen_pos[1], platform['width'], platform['height'])
            pygame.draw.rect(self.screen, (100, 50, 0), rect)
            pygame.draw.rect(self.screen, (150, 75, 0), rect, 2)
    
    def draw_enemies(self):
        """Draw all enemies"""
        enemy_colors = {
            'fire_skull': RED,
            'demon': PURPLE,
            'hell_hound': (100, 0, 0)
        }
        
        for enemy in self.enemies:
            screen_pos = self.world_to_screen((enemy['x'], enemy['y']))
            color = enemy_colors.get(enemy['type'], WHITE)
            
            # Draw enemy as a circle
            pygame.draw.circle(self.screen, color, screen_pos, 15)
            pygame.draw.circle(self.screen, WHITE, screen_pos, 15, 2)
            
            # Draw enemy type text
            text = self.small_font.render(enemy['type'], True, WHITE)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] + 25))
            self.screen.blit(text, text_rect)
    
    def draw_player_spawn(self):
        """Draw the player spawn point"""
        screen_pos = self.world_to_screen(self.player_spawn)
        pygame.draw.circle(self.screen, GREEN, screen_pos, 20)
        pygame.draw.circle(self.screen, WHITE, screen_pos, 20, 3)
        
        text = self.font.render("SPAWN", True, WHITE)
        text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] + 35))
        self.screen.blit(text, text_rect)
    
    def draw_drag_preview(self):
        """Draw preview of platform being dragged"""
        if self.drag_start and self.drag_end and self.mode == EditMode.PLATFORM:
            x1, y1 = self.world_to_screen(self.drag_start)
            x2, y2 = self.world_to_screen(self.drag_end)
            
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            # Minimum size
            if width < GRID_SIZE:
                width = GRID_SIZE
            if height < GRID_SIZE:
                height = GRID_SIZE
            
            rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(self.screen, YELLOW, rect, 2)
    
    def draw_ui(self):
        """Draw the user interface"""
        # Mode indicator
        mode_text = f"Mode: {self.mode.value.title()}"
        if self.mode == EditMode.ENEMY:
            mode_text += f" ({self.current_enemy.value})"
        
        mode_surface = self.font.render(mode_text, True, WHITE)
        self.screen.blit(mode_surface, (10, 10))
        
        # Instructions
        instructions = [
            "1: Platform Mode  2: Enemy Mode  3: Spawn Mode  4: Erase Mode",
            "TAB: Cycle Enemy Type (in Enemy Mode)",
            "G: Toggle Grid  S: Toggle Snap  Ctrl+S: Save  Ctrl+L: Load  Ctrl+C: Clear",
            "Arrow Keys: Move Camera",
            f"Grid: {'ON' if self.grid_visible else 'OFF'}  Snap: {'ON' if self.snap_to_grid else 'OFF'}",
            f"Objects: {len(self.platforms)} platforms, {len(self.enemies)} enemies"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text_surface, (10, 40 + i * 20))
        
        # Mode-specific cursor info
        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.screen_to_world(mouse_pos)
        if self.snap_to_grid:
            world_pos = self.snap_to_grid_pos(world_pos)
        
        cursor_info = f"World: ({world_pos[0]}, {world_pos[1]})"
        cursor_surface = self.small_font.render(cursor_info, True, WHITE)
        self.screen.blit(cursor_surface, (10, SCREEN_HEIGHT - 30))
    
    def draw(self):
        """Draw the entire editor"""
        self.screen.fill(BLACK)
        
        # Draw grid
        self.draw_grid()
        
        # Draw level objects
        self.draw_platforms()
        self.draw_enemies()
        self.draw_player_spawn()
        
        # Draw preview
        self.draw_drag_preview()
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """Main editor loop"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    try:
        editor = LevelEditor()
        editor.run()
    except Exception as e:
        print(f"Error running level editor: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
