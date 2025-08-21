#!/usr/bin/env python3
"""
Character Asset Manager for Reserka Gothic
Supports multiple playable characters including the Female Adventurer
"""

import pygame
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from PIL import Image, ImageOps
import math

@dataclass
class SpriteConfig:
    """Configuration for sprite extraction and scaling"""
    frame_width: int
    frame_height: int  
    frame_count: int
    cols: int = 1
    rows: int = 1
    scale_factor: float = 1.0
    crop_rect: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    offset_x: int = 0
    offset_y: int = 0

class CharacterAssetManager:
    """Enhanced asset manager with multiple character support"""
    
    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.images = {}
        self.sprite_configs = {}
        self.processed_sprites = {}
        
        # Character definitions
        self.characters = {
            'gothicvania_hero': {
                'name': 'Gothic Hero',
                'animations': ['idle', 'run', 'attack', 'jump']
            },
            'female_adventurer': {
                'name': 'Female Adventurer',
                'animations': ['idle', 'walk', 'run', 'dash', 'jump', 'attack', 'death']
            }
        }
        
        # Target dimensions for consistent gameplay
        self.TARGET_PLAYER_SIZE = (64, 64)
        self.TARGET_ENEMY_SIZE = {
            'fire_skull': (48, 48),
            'demon': (80, 80),
            'hell_hound': (64, 48)
        }
        
        self.load_sprite_configs()
        self.load_and_process_assets()
    
    def load_sprite_configs(self):
        """Define sprite extraction configurations for all characters"""
        self.sprite_configs = {
            # Gothic Hero sprites
            'gothicvania_hero_idle': SpriteConfig(
                frame_width=38,
                frame_height=48,
                frame_count=4,
                cols=4,
                rows=1,
                scale_factor=1.3
            ),
            'gothicvania_hero_run': SpriteConfig(
                frame_width=66,
                frame_height=48,
                frame_count=6,
                cols=6,
                rows=1,
                scale_factor=1.3
            ),
            'gothicvania_hero_attack': SpriteConfig(
                frame_width=96,
                frame_height=48,
                frame_count=4,
                cols=4,
                rows=1,
                scale_factor=1.3
            ),
            'gothicvania_hero_jump': SpriteConfig(
                frame_width=61,
                frame_height=77,
                frame_count=5,
                cols=5,
                rows=1,
                scale_factor=0.8
            ),
            
            # Female Adventurer sprites - Fixed configurations for 6x6 grid (384x384 images)
            'female_adventurer_idle': SpriteConfig(
                frame_width=64,
                frame_height=64,
                frame_count=6,  # First row: idle animation
                cols=6,
                rows=6,
                scale_factor=1.0
            ),
            'female_adventurer_walk': SpriteConfig(
                frame_width=64,
                frame_height=64,
                frame_count=6,  # First row: walk animation
                cols=6,
                rows=6,
                scale_factor=1.0
            ),
            'female_adventurer_run': SpriteConfig(
                frame_width=64,
                frame_height=64,
                frame_count=6,  # Alias for walk (running animation)
                cols=6,
                rows=6,
                scale_factor=1.0
            ),
            'female_adventurer_dash': SpriteConfig(
                frame_width=64,
                frame_height=64,
                frame_count=6,  # First row: dash animation
                cols=6,
                rows=6,
                scale_factor=1.0
            ),
            'female_adventurer_jump': SpriteConfig(
                frame_width=64,
                frame_height=64,
                frame_count=6,  # First row: jump animation
                cols=6,
                rows=6,
                scale_factor=1.0
            ),
            'female_adventurer_attack': SpriteConfig(
                frame_width=64,
                frame_height=64,
                frame_count=6,  # Use dash animation for attack if no specific attack exists
                cols=6,
                rows=6,
                scale_factor=1.0
            ),
            'female_adventurer_death': SpriteConfig(
                frame_width=64,
                frame_height=64,
                frame_count=6,  # First row: death animation
                cols=6,
                rows=6,
                scale_factor=1.0
            ),
            
            # Enemy sprites (keeping existing configs)
            'fire_skull': SpriteConfig(
                frame_width=96,
                frame_height=112,
                frame_count=8,
                cols=8,
                rows=1,
                scale_factor=0.5
            ),
            'demon_idle': SpriteConfig(
                frame_width=80,
                frame_height=144,
                frame_count=12,
                cols=12,
                rows=1,
                scale_factor=0.6
            ),
            'demon_attack': SpriteConfig(
                frame_width=120,
                frame_height=192,
                frame_count=12,
                cols=12,
                rows=1,
                scale_factor=0.5
            ),
            'hell_hound_idle': SpriteConfig(
                frame_width=48,
                frame_height=32,
                frame_count=8,
                cols=8,
                rows=1,
                scale_factor=1.5
            ),
            'hell_hound_run': SpriteConfig(
                frame_width=67,
                frame_height=32,
                frame_count=5,
                cols=5,
                rows=1,
                scale_factor=1.5
            )
        }
    
    def extract_sprite_frames(self, image_path: Path, config: SpriteConfig) -> List[pygame.Surface]:
        """Extract individual frames from a spritesheet"""
        if not image_path.exists():
            return self.create_placeholder_frames(config)
        
        try:
            # Load image with PIL for better processing
            pil_image = Image.open(image_path)
            
            # Convert to RGBA if needed
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')
            
            frames = []
            
            # Extract frames based on grid layout
            for i in range(config.frame_count):
                # For grid layouts, calculate position
                if config.cols > 1 or config.rows > 1:
                    col = i % config.cols
                    row = i // config.cols
                    
                    left = col * config.frame_width + config.offset_x
                    top = row * config.frame_height + config.offset_y
                else:
                    # Single row layout
                    left = i * config.frame_width + config.offset_x
                    top = config.offset_y
                
                right = left + config.frame_width
                bottom = top + config.frame_height
                
                # Ensure we don't go out of bounds
                if right > pil_image.width:
                    right = pil_image.width
                if bottom > pil_image.height:
                    bottom = pil_image.height
                
                # Crop the frame
                frame = pil_image.crop((left, top, right, bottom))
                
                # Apply cropping if specified
                if config.crop_rect:
                    cx, cy, cw, ch = config.crop_rect
                    frame = frame.crop((cx, cy, cx + cw, cy + ch))
                
                # Remove excess transparency (auto-crop) - Skip for Female Adventurer
                if not image_path.name.startswith(('Idle.png', 'walk.png', 'Dash.png', 'Jump.png', 'death.png')):
                    frame = self.auto_crop_transparency(frame)
                
                # Scale the frame
                if config.scale_factor != 1.0:
                    new_width = int(frame.width * config.scale_factor)
                    new_height = int(frame.height * config.scale_factor)
                    frame = frame.resize((new_width, new_height), Image.NEAREST)
                
                # Convert PIL image to Pygame surface
                frame_data = frame.tobytes()
                pygame_surface = pygame.image.fromstring(frame_data, frame.size, 'RGBA')
                frames.append(pygame_surface)
            
            return frames
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return self.create_placeholder_frames(config)
    
    def auto_crop_transparency(self, pil_image: Image.Image) -> Image.Image:
        """Remove transparent borders from sprite"""
        try:
            # Get the bounding box of non-transparent pixels
            bbox = pil_image.getbbox()
            if bbox:
                return pil_image.crop(bbox)
            else:
                return pil_image
        except:
            return pil_image
    
    def create_placeholder_frames(self, config: SpriteConfig) -> List[pygame.Surface]:
        """Create placeholder frames when sprite loading fails"""
        frames = []
        for i in range(config.frame_count):
            surface = pygame.Surface((int(config.frame_width * config.scale_factor), 
                                    int(config.frame_height * config.scale_factor)))
            # Create a distinctive placeholder pattern
            color = ((i * 50) % 255, (i * 80) % 255, (i * 120) % 255)
            surface.fill(color)
            frames.append(surface)
        return frames
    
    def load_and_process_assets(self):
        """Load and process all game assets with proper scaling"""
        print("🎨 Loading and processing character assets...")
        
        # Process character sprites
        self.load_gothicvania_hero_sprites()
        self.load_female_adventurer_sprites()
        
        # Process enemy sprites
        self.load_enemy_sprites()
        
        # Process background assets
        self.load_environment_assets()
        
        print("✅ Asset processing complete!")
    
    def load_gothicvania_hero_sprites(self):
        """Load and process Gothicvania hero sprite animations"""
        hero_path = self.assets_path / "Gothic-hero-Files" / "PNG"
        
        sprite_mappings = {
            'gothicvania_hero_idle': 'gothic-hero-idle.png',
            'gothicvania_hero_run': 'gothic-hero-run.png',
            'gothicvania_hero_attack': 'gothic-hero-attack.png',
            'gothicvania_hero_jump': 'gothic-hero-jump.png'
        }
        
        for sprite_key, filename in sprite_mappings.items():
            if sprite_key in self.sprite_configs:
                image_path = hero_path / filename
                config = self.sprite_configs[sprite_key]
                frames = self.extract_sprite_frames(image_path, config)
                self.processed_sprites[sprite_key] = frames
                print(f"  ✓ Processed {sprite_key}: {len(frames)} frames")
    
    def load_female_adventurer_sprites(self):
        """Load and process Female Adventurer sprite animations"""
        fa_path = self.assets_path / "female_adventurer"
        
        sprite_mappings = {
            'female_adventurer_idle': 'Idle/Idle.png',
            'female_adventurer_walk': 'Walk/walk.png',
            'female_adventurer_run': 'Walk/walk.png',  # Use walk for run
            'female_adventurer_dash': 'Dash/Dash.png',
            'female_adventurer_jump': 'Jump - NEW/Normal/Jump.png',
            'female_adventurer_attack': 'Dash/Dash.png',  # Use dash for attack
            'female_adventurer_death': 'Death/death.png'
        }
        
        for sprite_key, filename in sprite_mappings.items():
            if sprite_key in self.sprite_configs:
                image_path = fa_path / filename
                config = self.sprite_configs[sprite_key]
                frames = self.extract_sprite_frames(image_path, config)
                self.processed_sprites[sprite_key] = frames
                print(f"  ✓ Processed {sprite_key}: {len(frames)} frames")
    
    def load_enemy_sprites(self):
        """Load and process enemy sprite animations"""
        # Fire Skull
        fire_skull_path = self.assets_path / "Fire-Skull-Files" / "PNG" / "fire-skull.png"
        if 'fire_skull' in self.sprite_configs:
            config = self.sprite_configs['fire_skull']
            frames = self.extract_sprite_frames(fire_skull_path, config)
            self.processed_sprites['fire_skull'] = frames
            print(f"  ✓ Processed fire_skull: {len(frames)} frames")
        
        # Demon sprites
        demon_path = self.assets_path / "demon-Files" / "PNG"
        demon_mappings = {
            'demon_idle': 'demon-idle.png',
            'demon_attack': 'demon-attack.png'
        }
        
        for sprite_key, filename in demon_mappings.items():
            if sprite_key in self.sprite_configs:
                image_path = demon_path / filename
                config = self.sprite_configs[sprite_key]
                frames = self.extract_sprite_frames(image_path, config)
                self.processed_sprites[sprite_key] = frames
                print(f"  ✓ Processed {sprite_key}: {len(frames)} frames")
        
        # Hell Hound sprites - use correct paths
        hound_path = self.assets_path / "Hell-Hound-Files" / "PNG"
        hound_mappings = {
            'hell_hound_idle': 'hell-hound-idle.png',
            'hell_hound_run': 'hell-hound-run.png'
        }
        
        for sprite_key, filename in hound_mappings.items():
            if sprite_key in self.sprite_configs:
                image_path = hound_path / filename
                config = self.sprite_configs[sprite_key]
                frames = self.extract_sprite_frames(image_path, config)
                self.processed_sprites[sprite_key] = frames
                print(f"  ✓ Processed {sprite_key}: {len(frames)} frames")
    
    def load_environment_assets(self):
        """Load and process background and environment assets"""
        # Gothic Castle background
        castle_path = self.assets_path / "Gothic-Castle-Files" / "PNG" / "layers"
        
        bg_assets = {
            'castle_background': 'gothic-castle-background.png',
            'castle_tileset': 'gothic-castle-tileset.png'
        }
        
        for asset_key, filename in bg_assets.items():
            asset_path = castle_path / filename
            if asset_path.exists():
                try:
                    # Load and scale background to screen size
                    pil_image = Image.open(asset_path)
                    
                    # Scale backgrounds to fit screen while maintaining aspect ratio
                    screen_width, screen_height = 1280, 720
                    
                    # Calculate scaling to cover the screen
                    scale_x = screen_width / pil_image.width
                    scale_y = screen_height / pil_image.height
                    scale = max(scale_x, scale_y)  # Use max to cover screen
                    
                    new_width = int(pil_image.width * scale)
                    new_height = int(pil_image.height * scale)
                    
                    scaled_image = pil_image.resize((new_width, new_height), Image.NEAREST)
                    
                    # Convert to pygame surface
                    if scaled_image.mode != 'RGBA':
                        scaled_image = scaled_image.convert('RGBA')
                    
                    image_data = scaled_image.tobytes()
                    surface = pygame.image.fromstring(image_data, scaled_image.size, 'RGBA')
                    
                    self.images[asset_key] = surface
                    print(f"  ✓ Processed {asset_key}: {new_width}x{new_height}")
                    
                except Exception as e:
                    print(f"  ✗ Error processing {asset_key}: {e}")
        
        # Gothic Horror assets
        horror_path = self.assets_path / "Gothic-Horror-Files" / "PNG" / "layers"
        horror_assets = {
            'horror_town': 'town.png',
            'horror_clouds': 'clouds.png',
            'horror_tiles': 'tiles.png'
        }
        
        for asset_key, filename in horror_assets.items():
            asset_path = horror_path / filename
            if asset_path.exists():
                try:
                    surface = pygame.image.load(str(asset_path)).convert_alpha()
                    # Scale to reasonable size
                    scaled_surface = pygame.transform.scale(surface, (1280, 720))
                    self.images[asset_key] = scaled_surface
                    print(f"  ✓ Processed {asset_key}")
                except Exception as e:
                    print(f"  ✗ Error processing {asset_key}: {e}")
    
    def get_character_animations(self, character_id: str) -> Dict[str, List[pygame.Surface]]:
        """Get all animation frames for a character"""
        if character_id not in self.characters:
            return {}
        
        animations = {}
        for anim_name in self.characters[character_id]['animations']:
            sprite_key = f"{character_id}_{anim_name}"
            frames = self.processed_sprites.get(sprite_key, [])
            if frames:
                animations[anim_name] = frames
        
        return animations
    
    def get_sprite_frames(self, sprite_key: str) -> List[pygame.Surface]:
        """Get processed sprite frames"""
        return self.processed_sprites.get(sprite_key, [])
    
    def get_image(self, image_key: str) -> Optional[pygame.Surface]:
        """Get processed image"""
        return self.images.get(image_key)
    
    def get_available_characters(self) -> List[Dict[str, str]]:
        """Get list of available characters"""
        return [
            {
                'id': char_id,
                'name': char_data['name'],
                'animations': char_data['animations']
            }
            for char_id, char_data in self.characters.items()
        ]
    
    def create_character_preview(self, character_id: str) -> pygame.Surface:
        """Create a preview image for a character showing their idle animation"""
        preview_surface = pygame.Surface((200, 150))
        preview_surface.fill((30, 30, 30))
        
        # Get idle animation
        idle_frames = self.get_sprite_frames(f"{character_id}_idle")
        if not idle_frames:
            # Try walk animation for female adventurer
            idle_frames = self.get_sprite_frames(f"{character_id}_walk")
        
        if idle_frames:
            # Show first frame centered
            frame = idle_frames[0]
            frame_rect = frame.get_rect()
            frame_rect.center = preview_surface.get_rect().center
            preview_surface.blit(frame, frame_rect)
        
        # Add character name
        font = pygame.font.Font(None, 24)
        name = self.characters.get(character_id, {}).get('name', character_id)
        text = font.render(name, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.centerx = preview_surface.get_width() // 2
        text_rect.bottom = preview_surface.get_height() - 10
        preview_surface.blit(text, text_rect)
        
        return preview_surface
    
    def save_character_previews(self):
        """Save preview images for all characters"""
        for char_id in self.characters.keys():
            preview = self.create_character_preview(char_id)
            filename = f"character_preview_{char_id}.png"
            pygame.image.save(preview, filename)
            print(f"💾 Character preview saved as {filename}")

def main():
    """Test the character asset manager"""
    pygame.init()
    
    assets_path = Path(__file__).parent.parent / "assets"
    manager = CharacterAssetManager(assets_path)
    
    # Save character previews
    manager.save_character_previews()
    
    # Print summary
    print("\n📊 CHARACTER PROCESSING SUMMARY:")
    print("=" * 50)
    
    for char_id, char_data in manager.characters.items():
        print(f"\n🎭 {char_data['name']} ({char_id}):")
        animations = manager.get_character_animations(char_id)
        for anim_name, frames in animations.items():
            if frames:
                frame_size = f"{frames[0].get_width()}x{frames[0].get_height()}"
                print(f"  {anim_name}: {len(frames)} frames @ {frame_size}")
    
    print(f"\n🏞️ Background assets loaded: {len(manager.images)}")
    for img_key in manager.images.keys():
        img = manager.images[img_key]
        print(f"  {img_key}: {img.get_width()}x{img.get_height()}")
    
    pygame.quit()

if __name__ == "__main__":
    main()
