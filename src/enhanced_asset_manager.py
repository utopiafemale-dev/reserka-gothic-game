#!/usr/bin/env python3
"""
Enhanced Asset Manager for Reserka Gothic
Handles textures, environments, legacy characters, audio, and UI assets
"""

import pygame
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math

class EnhancedAssetManager:
    """Manages all game assets with caching and optimization"""
    
    def __init__(self, assets_path: Path):
        self.assets_path = Path(assets_path)
        self.textures = {}
        self.environments = {}
        self.characters = {}
        self.audio = {}
        self.ui_elements = {}
        self.fonts = {}
        self.cached_surfaces = {}
        
        # Initialize pygame mixer for audio
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        print("🎨 Enhanced Asset Manager initializing...")
        self.load_all_assets()
    
    def load_all_assets(self):
        """Load all game assets with optimization"""
        self.load_textures()
        self.load_environments() 
        self.load_legacy_characters()
        self.load_ui_assets()
        self.load_audio()
        self.create_procedural_assets()
        print("✅ All enhanced assets loaded!")
    
    def load_textures(self):
        """Load texture atlas and create individual textures"""
        texture_file = self.assets_path / "textures" / "Textures-16.png"
        if texture_file.exists():
            print("🖼️  Loading texture atlas...")
            atlas = pygame.image.load(str(texture_file)).convert_alpha()
            
            # Assuming 16x16 pixel textures in a grid
            tile_size = 16
            atlas_width = atlas.get_width()
            atlas_height = atlas.get_height()
            
            tiles_x = atlas_width // tile_size
            tiles_y = atlas_height // tile_size
            
            # Extract individual textures
            for y in range(tiles_y):
                for x in range(tiles_x):
                    rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    tile = atlas.subsurface(rect).copy()
                    # Scale up for better visibility (16x16 -> 32x32)
                    scaled_tile = pygame.transform.scale(tile, (32, 32))
                    texture_id = f"tile_{x}_{y}"
                    self.textures[texture_id] = scaled_tile
            
            print(f"  ✓ Extracted {tiles_x * tiles_y} textures from atlas")
    
    def load_environments(self):
        """Load cave and environment backgrounds"""
        env_path = self.assets_path / "environments"
        if env_path.exists():
            print("🏞️  Loading environments...")
            
            env_files = {
                'background1.png': 'cave_bg_1',
                'background2.png': 'cave_bg_2', 
                'background3.png': 'cave_bg_3',
                'background4a.png': 'cave_bg_4a',
                'background4b.png': 'cave_bg_4b',
                'mainlev_build.png': 'cave_tileset',
                'props1.png': 'cave_props_1',
                'props2.png': 'cave_props_2'
            }
            
            for filename, asset_id in env_files.items():
                file_path = env_path / filename
                if file_path.exists():
                    try:
                        surface = pygame.image.load(str(file_path)).convert_alpha()
                        self.environments[asset_id] = surface
                        print(f"  ✓ Loaded {asset_id}: {surface.get_width()}x{surface.get_height()}")
                    except pygame.error as e:
                        print(f"  ⚠️  Failed to load {filename}: {e}")
    
    def load_legacy_characters(self):
        """Load legacy character collections"""
        char_path = self.assets_path / "characters_legacy" / "Characters"
        if char_path.exists():
            print("👥 Loading legacy characters...")
            
            # Scan for character folders
            for char_dir in char_path.iterdir():
                if char_dir.is_dir() and not char_dir.name.startswith('.'):
                    char_name = char_dir.name.lower().replace(' ', '_')
                    self.characters[char_name] = {}
                    
                    # Load all images in character folder
                    for img_file in char_dir.glob("*.png"):
                        try:
                            surface = pygame.image.load(str(img_file)).convert_alpha()
                            img_name = img_file.stem.lower()
                            self.characters[char_name][img_name] = surface
                            print(f"  ✓ {char_name}: {img_name}")
                        except pygame.error as e:
                            print(f"  ⚠️  Failed to load {img_file}: {e}")
    
    def load_ui_assets(self):
        """Load and create UI assets"""
        print("🎮 Creating UI assets...")
        
        # Create Reserka logo
        self.create_reserka_logo()
        
        # Create menu backgrounds
        self.create_menu_backgrounds()
        
        # Create UI elements
        self.create_ui_elements()
    
    def create_reserka_logo(self):
        """Create the Reserka game logo"""
        # Create a stylized logo surface
        logo_width, logo_height = 400, 120
        logo_surface = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
        
        # Gothic-style font rendering simulation
        font_large = pygame.font.Font(None, 72)
        font_shadow = pygame.font.Font(None, 76)
        
        # Create shadow text
        shadow_text = font_shadow.render("RESERKA", True, (20, 20, 20))
        shadow_rect = shadow_text.get_rect(center=(logo_width//2 + 3, logo_height//2 + 3))
        logo_surface.blit(shadow_text, shadow_rect)
        
        # Create main text with gradient effect
        main_text = font_large.render("RESERKA", True, (220, 180, 80))
        main_rect = main_text.get_rect(center=(logo_width//2, logo_height//2))
        logo_surface.blit(main_text, main_rect)
        
        # Add decorative elements
        gothic_color = (150, 100, 50)
        # Left decoration
        pygame.draw.polygon(logo_surface, gothic_color, [
            (10, logo_height//2 - 20), (30, logo_height//2 - 10), 
            (30, logo_height//2 + 10), (10, logo_height//2 + 20)
        ])
        # Right decoration
        pygame.draw.polygon(logo_surface, gothic_color, [
            (logo_width - 10, logo_height//2 - 20), (logo_width - 30, logo_height//2 - 10),
            (logo_width - 30, logo_height//2 + 10), (logo_width - 10, logo_height//2 + 20)
        ])
        
        self.ui_elements['reserka_logo'] = logo_surface
        print("  ✓ Created Reserka logo")
    
    def create_menu_backgrounds(self):
        """Create menu background variations"""
        screen_size = (1280, 720)
        
        # Main menu background
        main_bg = pygame.Surface(screen_size)
        main_bg.fill((15, 15, 25))
        
        # Add gradient effect
        for y in range(screen_size[1]):
            alpha = int(255 * (1 - y / screen_size[1]) * 0.3)
            color = (25 + alpha//4, 15 + alpha//6, 35 + alpha//3)
            pygame.draw.line(main_bg, color, (0, y), (screen_size[0], y))
        
        # Add some decorative elements
        for i in range(20):
            x = (i * 67) % screen_size[0]
            y = (i * 89) % screen_size[1]
            size = 2 + (i % 3)
            pygame.draw.circle(main_bg, (40, 30, 50), (x, y), size)
        
        self.ui_elements['main_menu_bg'] = main_bg
        
        # Settings menu background (darker)
        settings_bg = main_bg.copy()
        dark_overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 128))
        settings_bg.blit(dark_overlay, (0, 0))
        self.ui_elements['settings_menu_bg'] = settings_bg
        
        print("  ✓ Created menu backgrounds")
    
    def create_ui_elements(self):
        """Create various UI elements"""
        # Button templates
        button_sizes = [(200, 50), (150, 40), (100, 30)]
        button_colors = {
            'normal': (60, 40, 80),
            'hover': (80, 60, 100),
            'pressed': (100, 80, 120)
        }
        
        for i, size in enumerate(button_sizes):
            button_name = f'button_{size[0]}x{size[1]}'
            for state, color in button_colors.items():
                button = pygame.Surface(size)
                button.fill(color)
                pygame.draw.rect(button, (color[0] + 20, color[1] + 20, color[2] + 20), 
                               button.get_rect(), 2)
                self.ui_elements[f'{button_name}_{state}'] = button
        
        # Progress bar template
        progress_bg = pygame.Surface((300, 20))
        progress_bg.fill((40, 40, 40))
        pygame.draw.rect(progress_bg, (80, 80, 80), progress_bg.get_rect(), 2)
        self.ui_elements['progress_bar_bg'] = progress_bg
        
        # Loading bar segments
        for i in range(10):
            segment = pygame.Surface((28, 16))
            segment.fill((100 + i * 10, 200 - i * 5, 100))
            self.ui_elements[f'loading_segment_{i}'] = segment
        
        print("  ✓ Created UI elements")
    
    def load_audio(self):
        """Load or create audio assets"""
        print("🔊 Setting up audio...")
        
        # Create placeholder sound effects using pygame's sound generation
        self.create_sound_effects()
        
        # Try to load any existing audio files
        audio_path = self.assets_path / "audio"
        if audio_path.exists():
            for audio_file in audio_path.glob("*.wav"):
                try:
                    sound = pygame.mixer.Sound(str(audio_file))
                    sound_name = audio_file.stem
                    self.audio[sound_name] = sound
                    print(f"  ✓ Loaded {sound_name}")
                except pygame.error as e:
                    print(f"  ⚠️  Failed to load {audio_file}: {e}")
    
    def create_sound_effects(self):
        """Create procedural sound effects"""
        # Create basic sound arrays and convert to pygame sounds
        sample_rate = 22050
        
        # Jump sound (ascending tone)
        jump_duration = 0.2
        jump_samples = int(sample_rate * jump_duration)
        jump_array = []
        for i in range(jump_samples):
            freq = 200 + (i / jump_samples) * 300
            t = i / sample_rate
            sample = int(16384 * math.sin(2 * math.pi * freq * t) * (1 - t / jump_duration))
            jump_array.append([sample, sample])
        
        try:
            jump_sound = pygame.sndarray.make_sound(pygame.array.array('h', 
                [item for sublist in jump_array for item in sublist]))
            self.audio['jump'] = jump_sound
        except:
            pass  # Skip if sndarray not available
        
        # Attack sound (quick burst)
        attack_duration = 0.1
        attack_samples = int(sample_rate * attack_duration)
        attack_array = []
        for i in range(attack_samples):
            t = i / sample_rate
            freq = 150 + (i % 100) * 2
            sample = int(8192 * math.sin(2 * math.pi * freq * t) * 
                        (1 - t / attack_duration) * math.sin(t * 200))
            attack_array.append([sample, sample])
        
        try:
            attack_sound = pygame.sndarray.make_sound(pygame.array.array('h',
                [item for sublist in attack_array for item in sublist]))
            self.audio['attack'] = attack_sound
        except:
            pass
        
        print("  ✓ Created procedural sound effects")
    
    def create_procedural_assets(self):
        """Create additional procedural assets"""
        # Particle effects
        particle_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), 
                          (255, 255, 100), (255, 100, 255)]
        
        for i, color in enumerate(particle_colors):
            particle = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(particle, color, (4, 4), 4)
            pygame.draw.circle(particle, (color[0]//2, color[1]//2, color[2]//2), (4, 4), 4, 1)
            self.ui_elements[f'particle_{i}'] = particle
        
        # Cursor/pointer
        cursor = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.polygon(cursor, (255, 255, 255), 
                           [(0, 0), (16, 6), (10, 10), (6, 16)])
        pygame.draw.polygon(cursor, (0, 0, 0), 
                           [(0, 0), (16, 6), (10, 10), (6, 16)], 2)
        self.ui_elements['cursor'] = cursor
        
        print("  ✓ Created procedural assets")
    
    def get_texture(self, texture_id: str) -> Optional[pygame.Surface]:
        """Get texture by ID"""
        return self.textures.get(texture_id)
    
    def get_environment(self, env_id: str) -> Optional[pygame.Surface]:
        """Get environment asset by ID"""
        return self.environments.get(env_id)
    
    def get_character(self, char_id: str, asset_name: str = None) -> Optional[pygame.Surface]:
        """Get character asset"""
        if char_id in self.characters:
            if asset_name:
                return self.characters[char_id].get(asset_name)
            return self.characters[char_id]
        return None
    
    def get_ui_element(self, element_id: str) -> Optional[pygame.Surface]:
        """Get a UI element by ID"""
        if element_id in self.ui_elements:
            return self.ui_elements[element_id]
        return None
        
    def get_animated_logo(self) -> Optional[str]:
        """Special method to get the animated logo path if available"""
        # Check for optimized version first
        optimized_logo = self.assets_path / "logo_optimized.gif"
        if optimized_logo.exists():
            return str(optimized_logo)
        
        # Check for transparent version
        transparent_logo = self.assets_path / "logo_transparent.gif"
        if transparent_logo.exists():
            return str(transparent_logo)
        
        # Fallback to original
        logo_path = self.assets_path / "logo.gif"
        if logo_path.exists():
            return str(logo_path)
        
        return None
    
    def play_sound(self, sound_id: str, volume: float = 1.0):
        """Play sound effect"""
        if sound_id in self.audio:
            sound = self.audio[sound_id]
            sound.set_volume(volume)
            sound.play()
    
    def get_random_texture(self, pattern: str = "tile_") -> pygame.Surface:
        """Get random texture matching pattern"""
        matching_textures = [tex for tex_id, tex in self.textures.items() 
                           if tex_id.startswith(pattern)]
        if matching_textures:
            import random
            return random.choice(matching_textures)
        return self.create_fallback_texture()
    
    def create_fallback_texture(self, size: Tuple[int, int] = (32, 32)) -> pygame.Surface:
        """Create fallback texture when asset is missing"""
        surface = pygame.Surface(size)
        surface.fill((100, 50, 150))
        pygame.draw.rect(surface, (150, 100, 200), surface.get_rect(), 2)
        return surface
    
    def optimize_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Optimize surface for better performance"""
        if surface.get_alpha() is not None or surface.get_colorkey() is not None:
            return surface.convert_alpha()
        return surface.convert()

def main():
    """Test the enhanced asset manager"""
    pygame.init()
    pygame.display.set_mode((800, 600))  # Required for convert_alpha()
    
    assets_path = Path(__file__).parent.parent / "assets"
    manager = EnhancedAssetManager(assets_path)
    
    # Display some loaded assets info
    print(f"\n📊 Asset Summary:")
    print(f"  Textures: {len(manager.textures)}")
    print(f"  Environments: {len(manager.environments)}")
    print(f"  Characters: {len(manager.characters)}")
    print(f"  UI Elements: {len(manager.ui_elements)}")
    print(f"  Audio: {len(manager.audio)}")
    
    # Test loading a texture
    test_texture = manager.get_texture("tile_0_0")
    if test_texture:
        print(f"  ✓ Test texture loaded: {test_texture.get_size()}")
    
    # Test environment
    test_env = manager.get_environment("cave_bg_1")
    if test_env:
        print(f"  ✓ Test environment loaded: {test_env.get_size()}")

if __name__ == "__main__":
    main()
