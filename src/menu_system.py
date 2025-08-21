#!/usr/bin/env python3
"""
Complete Menu System for Reserka Gothic
Includes loading screen, title menu, settings, pause menu, and transitions
"""

import pygame
import json
import math
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

# Import GIF support
from gif_loader import GIFManager

class MenuState(Enum):
    LOADING = "loading"
    MAIN_MENU = "main_menu"
    SETTINGS = "settings"
    CHARACTER_SELECT = "character_select"
    PAUSE_MENU = "pause_menu"
    EXIT_CONFIRM = "exit_confirm"

@dataclass
class MenuButton:
    text: str
    x: int
    y: int
    width: int
    height: int
    action: Callable
    enabled: bool = True
    hover: bool = False
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_clicked(self, pos: tuple) -> bool:
        return self.get_rect().collidepoint(pos) and self.enabled

@dataclass
class MenuSlider:
    label: str
    x: int
    y: int
    width: int
    min_value: float
    max_value: float
    value: float
    callback: Callable[[float], None]
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, 30)
    
    def get_handle_pos(self) -> int:
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        return int(self.x + ratio * self.width)

class LoadingScreen:
    """Animated loading screen with progress bar"""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        self.screen = screen
        self.asset_manager = asset_manager
        self.progress = 0.0
        self.loading_text = "Loading Reserka Gothic..."
        self.loading_stages = [
            "Initializing game systems...",
            "Loading textures and environments...",
            "Processing character assets...",
            "Setting up audio system...",
            "Preparing game world...",
            "Final optimizations...",
            "Ready to play!"
        ]
        self.current_stage = 0
        self.animation_time = 0
        self.particles = []
        self.create_particles()
    
    def create_particles(self):
        """Create animated particles for loading screen"""
        import random
        for i in range(30):
            particle = {
                'x': random.randint(0, 1280),
                'y': random.randint(0, 720),
                'dx': random.uniform(-1, 1),
                'dy': random.uniform(-1, 1),
                'size': random.randint(1, 3),
                'color': random.choice([(100, 150, 255), (150, 100, 255), (255, 150, 100)])
            }
            self.particles.append(particle)
    
    def update(self, dt: float, progress: float):
        """Update loading screen with progress"""
        self.animation_time += dt
        self.progress = min(1.0, progress)
        
        # Update current stage based on progress
        stage_index = int(self.progress * len(self.loading_stages))
        self.current_stage = min(stage_index, len(self.loading_stages) - 1)
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Wrap particles around screen
            if particle['x'] < 0:
                particle['x'] = 1280
            elif particle['x'] > 1280:
                particle['x'] = 0
                
            if particle['y'] < 0:
                particle['y'] = 720
            elif particle['y'] > 720:
                particle['y'] = 0
    
    def draw(self):
        """Draw loading screen"""
        # Background
        bg = self.asset_manager.get_ui_element('main_menu_bg')
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((15, 15, 25))
        
        # Draw particles
        for particle in self.particles:
            alpha = int(128 + 127 * math.sin(self.animation_time * 2 + particle['x'] * 0.01))
            color = particle['color']
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), particle['size'])
            self.screen.blit(particle_surface, (particle['x'], particle['y']))
        
        # Logo
        logo = self.asset_manager.get_ui_element('reserka_logo')
        if logo:
            logo_rect = logo.get_rect(center=(640, 200))
            self.screen.blit(logo, logo_rect)
        
        # Loading text
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        
        loading_surface = font_large.render(self.loading_text, True, (255, 255, 255))
        loading_rect = loading_surface.get_rect(center=(640, 350))
        self.screen.blit(loading_surface, loading_rect)
        
        # Current stage
        if self.current_stage < len(self.loading_stages):
            stage_text = self.loading_stages[self.current_stage]
            stage_surface = font_small.render(stage_text, True, (200, 200, 200))
            stage_rect = stage_surface.get_rect(center=(640, 400))
            self.screen.blit(stage_surface, stage_rect)
        
        # Progress bar
        bar_width = 400
        bar_height = 20
        bar_x = 640 - bar_width // 2
        bar_y = 450
        
        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Progress fill
        fill_width = int(bar_width * self.progress)
        if fill_width > 0:
            # Animated gradient
            for i in range(fill_width):
                ratio = i / bar_width
                color_intensity = int(100 + 155 * ratio + 50 * math.sin(self.animation_time * 3 + ratio * 10))
                # Clamp color values to valid range 0-255
                r = max(0, min(255, color_intensity))
                g = max(0, min(255, color_intensity // 2))
                b = max(0, min(255, 255 - color_intensity // 2))
                color = (r, g, b)
                pygame.draw.line(self.screen, color, 
                               (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height))
        
        # Progress percentage
        percent_text = f"{int(self.progress * 100)}%"
        percent_surface = font_small.render(percent_text, True, (255, 255, 255))
        percent_rect = percent_surface.get_rect(center=(640, 500))
        self.screen.blit(percent_surface, percent_rect)

class MainMenu:
    """Main menu with animated background and buttons"""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        self.screen = screen
        self.asset_manager = asset_manager
        self.buttons = []
        self.animation_time = 0
        self.create_buttons()
    
    def create_buttons(self):
        """Create main menu buttons"""
        button_width, button_height = 250, 60
        start_y = 350
        spacing = 80
        
        self.buttons = [
            MenuButton("START GAME", 640 - button_width//2, start_y, 
                      button_width, button_height, self.start_game),
            MenuButton("SETTINGS", 640 - button_width//2, start_y + spacing, 
                      button_width, button_height, self.open_settings),
            MenuButton("EXIT", 640 - button_width//2, start_y + spacing * 2, 
                      button_width, button_height, self.exit_game)
        ]
    
    def update(self, dt: float):
        """Update main menu animations"""
        self.animation_time += dt
    
    def handle_event(self, event) -> Optional[str]:
        """Handle menu events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for button in self.buttons:
                button.hover = button.get_rect().collidepoint(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                for button in self.buttons:
                    if button.is_clicked(mouse_pos):
                        return button.action()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Default to start game
                return self.start_game()
            elif event.key == pygame.K_ESCAPE:
                return self.exit_game()
        
        return None
    
    def draw(self):
        """Draw main menu"""
        # Background
        bg = self.asset_manager.get_ui_element('main_menu_bg')
        if bg:
            self.screen.blit(bg, (0, 0))
        
        # Cave background if available
        cave_bg = self.asset_manager.get_environment('cave_bg_1')
        if cave_bg:
            # Parallax scrolling background
            scroll_x = int(self.animation_time * 10) % cave_bg.get_width()
            self.screen.blit(cave_bg, (-scroll_x, 0))
            if scroll_x > 0:
                self.screen.blit(cave_bg, (-scroll_x + cave_bg.get_width(), 0))
            
            # Dark overlay for readability
            overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
        
        # Animated GIF logo if available (passed from menu system)
        if hasattr(self, 'gif_manager') and self.gif_manager:
            animated_logo = self.gif_manager.get_current_frame('logo', (400, 300))
            if animated_logo:
                bounce = math.sin(self.animation_time * 0.002) * 10
                logo_rect = animated_logo.get_rect(center=(640, 150 + bounce))
                self.screen.blit(animated_logo, logo_rect)
            else:
                # Fallback to static logo
                logo = self.asset_manager.get_ui_element('reserka_logo')
                if logo:
                    bounce = math.sin(self.animation_time * 0.002) * 10
                    logo_rect = logo.get_rect(center=(640, 150 + bounce))
                    self.screen.blit(logo, logo_rect)
        else:
            # Fallback to static logo
            logo = self.asset_manager.get_ui_element('reserka_logo')
            if logo:
                bounce = math.sin(self.animation_time * 0.002) * 10
                logo_rect = logo.get_rect(center=(640, 150 + bounce))
                self.screen.blit(logo, logo_rect)
        
        # Subtitle
        font_subtitle = pygame.font.Font(None, 36)
        subtitle = font_subtitle.render("Gothic Adventure Awaits", True, (200, 180, 120))
        subtitle_rect = subtitle.get_rect(center=(640, 250))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw buttons
        font_button = pygame.font.Font(None, 48)
        for button in self.buttons:
            # Button background
            if button.hover:
                color = (80, 60, 100)
                glow = pygame.Surface((button.width + 20, button.height + 20), pygame.SRCALPHA)
                glow.fill((120, 100, 150, 100))
                glow_rect = glow.get_rect(center=button.get_rect().center)
                self.screen.blit(glow, glow_rect)
            else:
                color = (60, 40, 80)
            
            pygame.draw.rect(self.screen, color, button.get_rect())
            pygame.draw.rect(self.screen, (100, 80, 120), button.get_rect(), 3)
            
            # Button text
            text_color = (255, 255, 255) if button.hover else (200, 200, 200)
            text_surface = font_button.render(button.text, True, text_color)
            text_rect = text_surface.get_rect(center=button.get_rect().center)
            self.screen.blit(text_surface, text_rect)
    
    def start_game(self) -> str:
        return "character_select"
    
    def open_settings(self) -> str:
        return "settings"
    
    def exit_game(self) -> str:
        return "exit_confirm"

class SettingsMenu:
    """Settings menu with volume, resolution, and other options"""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        self.screen = screen
        self.asset_manager = asset_manager
        self.buttons = []
        self.sliders = []
        self.settings = self.load_settings()
        self.create_ui_elements()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create defaults"""
        settings_file = Path("settings.json")
        default_settings = {
            'master_volume': 0.7,
            'music_volume': 0.5,
            'sfx_volume': 0.8,
            'fullscreen': False,
            'vsync': True,
            'show_fps': False
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_settings.update(loaded_settings)
            except:
                pass
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open("settings.json", 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
    
    def create_ui_elements(self):
        """Create settings UI elements"""
        # Volume sliders
        self.sliders = [
            MenuSlider("Master Volume", 400, 200, 300, 0.0, 1.0, 
                      self.settings['master_volume'], self.set_master_volume),
            MenuSlider("Music Volume", 400, 250, 300, 0.0, 1.0, 
                      self.settings['music_volume'], self.set_music_volume),
            MenuSlider("SFX Volume", 400, 300, 300, 0.0, 1.0, 
                      self.settings['sfx_volume'], self.set_sfx_volume)
        ]
        
        # Buttons
        self.buttons = [
            MenuButton("Toggle Fullscreen", 400, 400, 200, 50, self.toggle_fullscreen),
            MenuButton("Toggle VSync", 650, 400, 200, 50, self.toggle_vsync),
            MenuButton("Show FPS", 400, 470, 200, 50, self.toggle_fps),
            MenuButton("Reset to Defaults", 650, 470, 200, 50, self.reset_defaults),
            MenuButton("BACK", 550, 580, 180, 50, self.go_back)
        ]
    
    def update(self, dt: float):
        """Update settings menu"""
        pass
    
    def handle_event(self, event) -> Optional[str]:
        """Handle settings menu events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for button in self.buttons:
                button.hover = button.get_rect().collidepoint(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check button clicks
                for button in self.buttons:
                    if button.is_clicked(mouse_pos):
                        result = button.action()
                        if result:
                            return result
                
                # Check slider interactions
                for slider in self.sliders:
                    if slider.get_rect().collidepoint(mouse_pos):
                        rel_x = mouse_pos[0] - slider.x
                        ratio = max(0, min(1, rel_x / slider.width))
                        new_value = slider.min_value + ratio * (slider.max_value - slider.min_value)
                        slider.value = new_value
                        slider.callback(new_value)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return self.go_back()
        
        return None
    
    def draw(self):
        """Draw settings menu"""
        # Background
        bg = self.asset_manager.get_ui_element('settings_menu_bg')
        if bg:
            self.screen.blit(bg, (0, 0))
        
        # Title
        font_title = pygame.font.Font(None, 72)
        title = font_title.render("SETTINGS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(640, 100))
        self.screen.blit(title, title_rect)
        
        # Draw sliders
        font_label = pygame.font.Font(None, 36)
        for slider in self.sliders:
            # Label
            label = font_label.render(slider.label, True, (200, 200, 200))
            self.screen.blit(label, (slider.x, slider.y - 35))
            
            # Slider track
            track_rect = pygame.Rect(slider.x, slider.y + 10, slider.width, 10)
            pygame.draw.rect(self.screen, (60, 60, 60), track_rect)
            pygame.draw.rect(self.screen, (120, 120, 120), track_rect, 2)
            
            # Slider handle
            handle_x = slider.get_handle_pos()
            handle_rect = pygame.Rect(handle_x - 8, slider.y + 5, 16, 20)
            pygame.draw.rect(self.screen, (150, 150, 150), handle_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), handle_rect, 2)
            
            # Value display
            value_text = f"{slider.value:.1f}"
            value_surface = font_label.render(value_text, True, (255, 255, 255))
            self.screen.blit(value_surface, (slider.x + slider.width + 20, slider.y))
        
        # Draw buttons
        font_button = pygame.font.Font(None, 36)
        for button in self.buttons:
            # Button background
            color = (80, 60, 100) if button.hover else (60, 40, 80)
            pygame.draw.rect(self.screen, color, button.get_rect())
            pygame.draw.rect(self.screen, (100, 80, 120), button.get_rect(), 2)
            
            # Button text
            text_color = (255, 255, 255) if button.hover else (200, 200, 200)
            text_surface = font_button.render(button.text, True, text_color)
            text_rect = text_surface.get_rect(center=button.get_rect().center)
            self.screen.blit(text_surface, text_rect)
        
        # Current settings display
        font_small = pygame.font.Font(None, 24)
        settings_text = [
            f"Fullscreen: {'ON' if self.settings['fullscreen'] else 'OFF'}",
            f"VSync: {'ON' if self.settings['vsync'] else 'OFF'}",
            f"Show FPS: {'ON' if self.settings['show_fps'] else 'OFF'}"
        ]
        
        for i, text in enumerate(settings_text):
            surface = font_small.render(text, True, (150, 150, 150))
            self.screen.blit(surface, (50, 200 + i * 25))
    
    # Callback functions
    def set_master_volume(self, value: float):
        self.settings['master_volume'] = value
        # Set volume for all sound channels
        for i in range(pygame.mixer.get_num_channels()):
            channel = pygame.mixer.Channel(i)
            channel.set_volume(value)
        self.save_settings()
    
    def set_music_volume(self, value: float):
        self.settings['music_volume'] = value
        # Apply to background music when implemented
        self.save_settings()
    
    def set_sfx_volume(self, value: float):
        self.settings['sfx_volume'] = value
        # Apply to sound effects
        self.save_settings()
    
    def toggle_fullscreen(self):
        self.settings['fullscreen'] = not self.settings['fullscreen']
        # Toggle fullscreen mode
        self.save_settings()
    
    def toggle_vsync(self):
        self.settings['vsync'] = not self.settings['vsync']
        self.save_settings()
    
    def toggle_fps(self):
        self.settings['show_fps'] = not self.settings['show_fps']
        self.save_settings()
    
    def reset_defaults(self):
        self.settings = {
            'master_volume': 0.7,
            'music_volume': 0.5,
            'sfx_volume': 0.8,
            'fullscreen': False,
            'vsync': True,
            'show_fps': False
        }
        self.create_ui_elements()  # Recreate sliders with new values
        self.save_settings()
    
    def go_back(self) -> str:
        return "main_menu"

class PauseMenu:
    """In-game pause menu"""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        self.screen = screen
        self.asset_manager = asset_manager
        self.buttons = []
        self.create_buttons()
    
    def create_buttons(self):
        """Create pause menu buttons"""
        button_width, button_height = 200, 50
        start_y = 250
        spacing = 60
        
        self.buttons = [
            MenuButton("RESUME", 640 - button_width//2, start_y, 
                      button_width, button_height, self.resume_game),
            MenuButton("SETTINGS", 640 - button_width//2, start_y + spacing, 
                      button_width, button_height, self.open_settings),
            MenuButton("MAIN MENU", 640 - button_width//2, start_y + spacing * 2, 
                      button_width, button_height, self.main_menu),
            MenuButton("EXIT GAME", 640 - button_width//2, start_y + spacing * 3, 
                      button_width, button_height, self.exit_game)
        ]
    
    def update(self, dt: float):
        """Update pause menu state"""
        pass
    
    def handle_event(self, event) -> Optional[str]:
        """Handle pause menu events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for button in self.buttons:
                button.hover = button.get_rect().collidepoint(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for button in self.buttons:
                    if button.is_clicked(mouse_pos):
                        return button.action()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return self.resume_game()
        
        return None
    
    def draw(self):
        """Draw pause menu overlay"""
        # Semi-transparent overlay with gradient
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Pause title with glow effect
        font_title = pygame.font.Font(None, 72)
        title_text = "GAME PAUSED"
        
        # Title glow
        title_glow = font_title.render(title_text, True, (100, 100, 200))
        title_glow_rect = title_glow.get_rect(center=(642, 152))
        self.screen.blit(title_glow, title_glow_rect)
        
        # Main title
        title = font_title.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(640, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions
        font_small = pygame.font.Font(None, 28)
        instruction_text = "Press ESC to resume game"
        instruction_surface = font_small.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(640, 190))
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Draw buttons with enhanced styling
        font_button = pygame.font.Font(None, 42)
        for button in self.buttons:
            # Button glow for hover effect
            if button.hover:
                color = (90, 70, 120)
                # Add glow effect
                glow_surface = pygame.Surface((button.width + 10, button.height + 10), pygame.SRCALPHA)
                glow_surface.fill((120, 100, 150, 100))
                glow_rect = glow_surface.get_rect(center=button.get_rect().center)
                self.screen.blit(glow_surface, glow_rect)
            else:
                color = (60, 40, 80)
            
            # Main button
            pygame.draw.rect(self.screen, color, button.get_rect())
            pygame.draw.rect(self.screen, (140, 120, 160), button.get_rect(), 3)
            
            # Button text with enhanced styling
            text_color = (255, 255, 255) if button.hover else (200, 200, 200)
            text_surface = font_button.render(button.text, True, text_color)
            text_rect = text_surface.get_rect(center=button.get_rect().center)
            self.screen.blit(text_surface, text_rect)
        
        # Additional game info at bottom
        font_info = pygame.font.Font(None, 24)
        info_text = "Your progress is automatically saved"
        info_surface = font_info.render(info_text, True, (150, 150, 150))
        info_rect = info_surface.get_rect(center=(640, 600))
        self.screen.blit(info_surface, info_rect)
    
    def resume_game(self) -> str:
        return "resume"
    
    def open_settings(self) -> str:
        return "settings"
    
    def main_menu(self) -> str:
        return "main_menu"
    
    def exit_game(self) -> str:
        return "exit_confirm"

class MenuSystem:
    """Complete menu system coordinator"""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        self.screen = screen
        self.asset_manager = asset_manager
        self.current_state = MenuState.LOADING
        self.previous_state = None
        
        # Initialize GIF manager for animated logo
        self.gif_manager = GIFManager()
        
        # Load animated logo if available
        logo_path = asset_manager.get_animated_logo()
        if logo_path:
            success = self.gif_manager.load_gif('logo', Path(logo_path))
            if success:
                print("✅ Animated logo loaded successfully!")
            else:
                print("⚠️ Failed to load animated logo")
        
        # Initialize menu components
        self.loading_screen = LoadingScreen(screen, asset_manager)
        self.main_menu = MainMenu(screen, asset_manager)
        self.main_menu.gif_manager = self.gif_manager  # Pass GIF manager to main menu
        self.settings_menu = SettingsMenu(screen, asset_manager)
        self.pause_menu = PauseMenu(screen, asset_manager)
        
        # Loading progress
        self.loading_progress = 0.0
        self.loading_complete = False
    
    def update(self, dt: float):
        """Update current menu state"""
        # Update animated GIF
        self.gif_manager.update_all()
        
        if self.current_state == MenuState.LOADING:
            if not self.loading_complete:
                # Simulate loading progress
                self.loading_progress += dt * 0.001  # Adjust speed as needed
                if self.loading_progress >= 1.0:
                    self.loading_progress = 1.0
                    self.loading_complete = True
            
            self.loading_screen.update(dt, self.loading_progress)
            
        elif self.current_state == MenuState.MAIN_MENU:
            self.main_menu.update(dt)
        
        elif self.current_state == MenuState.SETTINGS:
            self.settings_menu.update(dt)
        
        elif self.current_state == MenuState.PAUSE_MENU:
            self.pause_menu.update(dt)
    
    def handle_event(self, event) -> Optional[str]:
        """Handle menu events and return game actions"""
        result = None
        
        if self.current_state == MenuState.LOADING:
            if self.loading_complete:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.current_state = MenuState.MAIN_MENU
        
        elif self.current_state == MenuState.MAIN_MENU:
            action = self.main_menu.handle_event(event)
            if action == "character_select":
                return "start_game"  # Signal to start game
            elif action == "settings":
                self.previous_state = self.current_state
                self.current_state = MenuState.SETTINGS
            elif action == "exit_confirm":
                return "exit_game"
        
        elif self.current_state == MenuState.SETTINGS:
            action = self.settings_menu.handle_event(event)
            if action == "main_menu":
                # Return to the appropriate previous state
                if self.previous_state == MenuState.PAUSE_MENU:
                    self.current_state = MenuState.PAUSE_MENU
                    return None  # Stay in pause menu
                else:
                    self.current_state = MenuState.MAIN_MENU
                    return None
        
        elif self.current_state == MenuState.PAUSE_MENU:
            action = self.pause_menu.handle_event(event)
            if action == "resume":
                return "resume_game"
            elif action == "settings":
                self.previous_state = self.current_state
                self.current_state = MenuState.SETTINGS
            elif action == "main_menu":
                return "main_menu"
            elif action == "exit_confirm":
                return "exit_game"
        
        return None
    
    def draw(self):
        """Draw current menu state"""
        if self.current_state == MenuState.LOADING:
            self.loading_screen.draw()
        
        elif self.current_state == MenuState.MAIN_MENU:
            self.main_menu.draw()
        
        elif self.current_state == MenuState.SETTINGS:
            self.settings_menu.draw()
        
        elif self.current_state == MenuState.PAUSE_MENU:
            self.pause_menu.draw()
    
    def show_pause_menu(self):
        """Show pause menu"""
        self.previous_state = self.current_state
        self.current_state = MenuState.PAUSE_MENU
    
    def is_loading_complete(self) -> bool:
        """Check if loading is complete"""
        return self.loading_complete
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.settings_menu.settings

def main():
    """Test the menu system"""
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Reserka Gothic - Menu System Test")
    clock = pygame.time.Clock()
    
    # Mock asset manager for testing
    class MockAssetManager:
        def get_ui_element(self, element_id):
            return None
        def get_environment(self, env_id):
            return None
    
    asset_manager = MockAssetManager()
    menu_system = MenuSystem(screen, asset_manager)
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            result = menu_system.handle_event(event)
            if result == "exit_game":
                running = False
            elif result == "start_game":
                print("Starting game...")
        
        menu_system.update(dt)
        menu_system.draw()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
