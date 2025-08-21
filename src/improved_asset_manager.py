#!/usr/bin/env python3
"""
Improved Asset Manager for Reserka Gothic
Handles proper sprite extraction, cropping, and scaling for consistent gameplay
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
    scale_factor: float = 1.0
    crop_rect: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    offset_x: int = 0
    offset_y: int = 0

class ImprovedAssetManager:
    """Enhanced asset manager with proper sprite handling"""
    
    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.images = {}
        self.sprite_configs = {}
        self.processed_sprites = {}
        
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
        """Define sprite extraction configurations"""
        self.sprite_configs = {
            # Hero sprites
            'hero_idle': SpriteConfig(
                frame_width=38,  # Estimated from 152/4 frames
                frame_height=48,
                frame_count=4,
                scale_factor=1.3
            ),
            'hero_run': SpriteConfig(
                frame_width=66,  # Estimated from 792/12 frames (but we'll use 6)
                frame_height=48,
                frame_count=6,
                scale_factor=1.3
            ),
            'hero_attack': SpriteConfig(
                frame_width=96,  # Estimated from 576/6 frames (but we'll use 4)
                frame_height=48,
                frame_count=4,
                scale_factor=1.3
            ),
            'hero_jump': SpriteConfig(
                frame_width=61,  # Estimated from 305/5 frames
                frame_height=77,
                frame_count=5,
                scale_factor=0.8  # Jump sprite is taller, scale down
            ),
            
            # Fire Skull sprites
            'fire_skull': SpriteConfig(
                frame_width=96,  # Estimated from 768/8 frames
                frame_height=112,
                frame_count=8,
                scale_factor=0.5  # Scale down large sprite
            ),
            
            # Demon sprites
            'demon_idle': SpriteConfig(
                frame_width=80,  # Estimated from 960/12 frames
                frame_height=144,
                frame_count=12,
                scale_factor=0.6  # Scale down large sprite
            ),
            'demon_attack': SpriteConfig(
                frame_width=120,  # Estimated from large spritesheet
                frame_height=192,
                frame_count=12,  # Use subset of frames
                scale_factor=0.5
            ),
            
            # Hell Hound sprites
            'hell_hound_idle': SpriteConfig(
                frame_width=48,  # Estimated from 384/8 frames
                frame_height=32,
                frame_count=8,
                scale_factor=1.5  # Scale up small sprite
            ),
            'hell_hound_run': SpriteConfig(
                frame_width=67,  # Estimated from 335/5 frames
                frame_height=32,
                frame_count=5,
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
            
            # Calculate actual frame dimensions if auto-detecting
            if config.frame_width == -1:  # Auto-detect
                config.frame_width = pil_image.width // config.frame_count
            
            for i in range(config.frame_count):
                # Extract frame from spritesheet
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
                
                # Remove excess transparency (auto-crop)
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
        print("🎨 Loading and processing Gothic assets...")
        
        # Process hero sprites
        self.load_hero_sprites()
        
        # Process enemy sprites
        self.load_enemy_sprites()
        
        # Process background assets
        self.load_environment_assets()
        
        print("✅ Asset processing complete!")
    
    def load_hero_sprites(self):
        """Load and process hero sprite animations"""
        hero_path = self.assets_path / "Gothic-hero-Files" / "PNG"
        
        sprite_mappings = {
            'hero_idle': 'gothic-hero-idle.png',
            'hero_run': 'gothic-hero-run.png',
            'hero_attack': 'gothic-hero-attack.png',
            'hero_jump': 'gothic-hero-jump.png'
        }
        
        for sprite_key, filename in sprite_mappings.items():
            if sprite_key in self.sprite_configs:
                image_path = hero_path / filename
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
        
        # Hell Hound sprites
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
    
    def get_sprite_frames(self, sprite_key: str) -> List[pygame.Surface]:
        """Get processed sprite frames"""
        return self.processed_sprites.get(sprite_key, [])
    
    def get_image(self, image_key: str) -> Optional[pygame.Surface]:
        """Get processed image"""
        return self.images.get(image_key)
    
    def create_test_image(self):
        """Create a test image showing all processed sprites"""
        test_surface = pygame.Surface((1280, 720))
        test_surface.fill((50, 50, 50))
        
        y_offset = 50
        x_offset = 50
        
        font = pygame.font.Font(None, 24)
        
        for sprite_key, frames in self.processed_sprites.items():
            if frames:
                # Draw sprite name
                text = font.render(sprite_key, True, (255, 255, 255))
                test_surface.blit(text, (x_offset, y_offset))
                y_offset += 30
                
                # Draw first few frames
                frame_x = x_offset
                for i, frame in enumerate(frames[:5]):  # Show first 5 frames
                    test_surface.blit(frame, (frame_x, y_offset))
                    frame_x += frame.get_width() + 10
                
                y_offset += max(frame.get_height() for frame in frames[:5]) + 20
                
                # Reset position if getting too low
                if y_offset > 600:
                    y_offset = 50
                    x_offset += 400
        
        return test_surface
    
    def save_test_image(self, filename: str = "sprite_test.png"):
        """Save a test image showing all processed sprites"""
        test_surface = self.create_test_image()
        pygame.image.save(test_surface, filename)
        print(f"💾 Test image saved as {filename}")

def main():
    """Test the improved asset manager"""
    pygame.init()
    
    assets_path = Path(__file__).parent.parent / "assets"
    manager = ImprovedAssetManager(assets_path)
    
    # Save test image
    manager.save_test_image("/Users/vamplugmusic/reserka-gothic-game/sprite_test.png")
    
    # Print summary
    print("\n📊 PROCESSING SUMMARY:")
    print("=" * 50)
    
    for sprite_key, frames in manager.processed_sprites.items():
        if frames:
            frame_size = f"{frames[0].get_width()}x{frames[0].get_height()}"
            print(f"  {sprite_key}: {len(frames)} frames @ {frame_size}")
    
    print(f"\nBackground assets loaded: {len(manager.images)}")
    for img_key in manager.images.keys():
        img = manager.images[img_key]
        print(f"  {img_key}: {img.get_width()}x{img.get_height()}")
    
    pygame.quit()

if __name__ == "__main__":
    main()
