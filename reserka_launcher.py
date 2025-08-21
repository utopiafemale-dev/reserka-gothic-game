#!/usr/bin/env python3
"""
Reserka Gothic - Game Launcher
Main launcher for the game with options to start game or level editor
"""

import pygame
import sys
import subprocess
from pathlib import Path
from enum import Enum

# Initialize Pygame
pygame.init()

# Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
DARK_BLUE = (25, 25, 112)
RED = (139, 0, 0)

class LauncherOption(Enum):
    PLAY_GAME = 0
    LEVEL_EDITOR = 1
    QUIT = 2

class GameLauncher:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Reserka Gothic - Launcher")
        self.clock = pygame.time.Clock()
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        # Menu state
        self.selected_option = LauncherOption.PLAY_GAME
        self.options = [
            ("Play Game", LauncherOption.PLAY_GAME),
            ("Level Editor", LauncherOption.LEVEL_EDITOR),
            ("Quit", LauncherOption.QUIT)
        ]
        
        # Background animation
        self.background_particles = []
        self.init_particles()
    
    def init_particles(self):
        """Initialize background particles for atmosphere"""
        import random
        for _ in range(50):
            particle = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vel_x': random.uniform(-0.5, 0.5),
                'vel_y': random.uniform(-1, -0.1),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150)
            }
            self.background_particles.append(particle)
    
    def update_particles(self):
        """Update background particles"""
        for particle in self.background_particles:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            # Reset particle if it goes off screen
            if particle['y'] < -10:
                particle['y'] = SCREEN_HEIGHT + 10
                import random
                particle['x'] = random.randint(0, SCREEN_WIDTH)
            
            if particle['x'] < -10 or particle['x'] > SCREEN_WIDTH + 10:
                particle['x'] = SCREEN_WIDTH // 2
    
    def draw_particles(self):
        """Draw atmospheric particles"""
        for particle in self.background_particles:
            # Create surface with alpha for particle
            particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            particle_surf.set_alpha(particle['alpha'])
            particle_surf.fill(GOLD)
            
            self.screen.blit(particle_surf, 
                           (int(particle['x']), int(particle['y'])))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_index = self.selected_option.value
                    new_index = (current_index - 1) % len(self.options)
                    self.selected_option = LauncherOption(new_index)
                
                elif event.key == pygame.K_DOWN:
                    current_index = self.selected_option.value
                    new_index = (current_index + 1) % len(self.options)
                    self.selected_option = LauncherOption(new_index)
                
                elif event.key == pygame.K_RETURN:
                    return self.handle_selection()
                
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def handle_selection(self):
        """Handle menu selection"""
        if self.selected_option == LauncherOption.PLAY_GAME:
            return self.launch_game()
        elif self.selected_option == LauncherOption.LEVEL_EDITOR:
            return self.launch_level_editor()
        elif self.selected_option == LauncherOption.QUIT:
            return False
        
        return True
    
    def launch_game(self):
        """Launch the ultimate enhanced game"""
        try:
            game_path = Path(__file__).parent / "src" / "reserka_gothic_ultimate.py"
            subprocess.run([sys.executable, str(game_path)])
        except Exception as e:
            print(f"Error launching ultimate game: {e}")
        return True
    
    def launch_level_editor(self):
        """Launch the level editor"""
        try:
            editor_path = Path(__file__).parent / "src" / "level_editor.py"
            subprocess.run([sys.executable, str(editor_path)])
        except Exception as e:
            print(f"Error launching level editor: {e}")
        return True
    
    def draw_title(self):
        """Draw the game title"""
        title = self.large_font.render("RESERKA", True, GOLD)
        subtitle = self.font.render("Gothic Edition", True, WHITE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        
        # Draw title shadow
        shadow_title = self.large_font.render("RESERKA", True, BLACK)
        shadow_subtitle = self.font.render("Gothic Edition", True, BLACK)
        
        self.screen.blit(shadow_title, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(shadow_subtitle, (subtitle_rect.x + 2, subtitle_rect.y + 2))
        
        # Draw main title
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
    
    def draw_menu(self):
        """Draw the menu options"""
        start_y = 300
        
        for i, (option_text, option_enum) in enumerate(self.options):
            y_pos = start_y + i * 60
            
            # Determine color based on selection
            if self.selected_option == option_enum:
                color = GOLD
                # Draw selection indicator
                indicator = "► "
            else:
                color = WHITE
                indicator = "  "
            
            # Draw option text
            text = self.font.render(indicator + option_text, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            
            # Draw shadow for selected option
            if self.selected_option == option_enum:
                shadow_text = self.font.render(indicator + option_text, True, BLACK)
                self.screen.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
            
            self.screen.blit(text, text_rect)
    
    def draw_info(self):
        """Draw game information"""
        info_lines = [
            "A dark fantasy action-platformer",
            "Explore gothic castles and fight demons",
            "Use WASD/Arrows to move, SPACE to jump, X to attack",
            "",
            "Controls: ↑↓ to navigate, ENTER to select, ESC to quit"
        ]
        
        start_y = SCREEN_HEIGHT - 150
        for i, line in enumerate(info_lines):
            if line:  # Skip empty lines
                text = self.small_font.render(line, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 20))
                self.screen.blit(text, text_rect)
    
    def draw_version_info(self):
        """Draw version and credits"""
        version_text = "v1.0 - Created with Gothicvania Assets"
        credits_text = "Built with Python & Pygame"
        
        version_surface = self.small_font.render(version_text, True, WHITE)
        credits_surface = self.small_font.render(credits_text, True, WHITE)
        
        self.screen.blit(version_surface, (10, SCREEN_HEIGHT - 40))
        self.screen.blit(credits_surface, (10, SCREEN_HEIGHT - 20))
    
    def draw(self):
        """Draw the launcher"""
        # Fill background with gradient effect
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(DARK_BLUE[0] * (1 - color_ratio))
            g = int(DARK_BLUE[1] * (1 - color_ratio))
            b = int(DARK_BLUE[2] * (1 - color_ratio))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw particles
        self.draw_particles()
        
        # Draw UI elements
        self.draw_title()
        self.draw_menu()
        self.draw_info()
        self.draw_version_info()
        
        pygame.display.flip()
    
    def run(self):
        """Main launcher loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update_particles()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    try:
        launcher = GameLauncher()
        launcher.run()
    except Exception as e:
        print(f"Error running launcher: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
