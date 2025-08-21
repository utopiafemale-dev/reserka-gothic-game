
#!/usr/bin/env python3
"""
Reserka Gothic - Ultimate Enhanced Edition
Complete game with new assets, menu system, audio, and professional 64-bit feel
"""

import pygame
import sys
import math
import random
import json
import time
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Import our enhanced systems
from enhanced_asset_manager import EnhancedAssetManager
from menu_system import MenuSystem, MenuState
from enhanced_level_system import EnhancedLevelManager
from character_selection import CharacterSelection
from character_asset_manager import CharacterAssetManager
from pixel_texture_manager import PixelTextureManager
from graphics_enhancer import GraphicsEnhancer

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TARGET_FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (25, 25, 112)
GOLD = (255, 215, 0)

class GameState(Enum):
    MENU = "menu"
    CHARACTER_SELECT = "character_select"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_TRANSITION = "level_transition"
    VICTORY = "victory"

class Direction(Enum):
    LEFT = -1
    RIGHT = 1

@dataclass
class AnimationFrame:
    surface: pygame.Surface
    duration: int

class Animation:
    def __init__(self, frames: List[AnimationFrame], loop: bool = True):
        self.frames = frames
        self.loop = loop
        self.current_frame = 0
        self.frame_timer = 0
        self.finished = False
    
    def update(self, dt: int):
        if self.finished and not self.loop:
            return
        
        if len(self.frames) == 0:
            return
            
        self.frame_timer += dt
        current_duration = self.frames[self.current_frame].duration
        
        if self.frame_timer >= current_duration:
            self.frame_timer = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self) -> pygame.Surface:
        if self.frames:
            return self.frames[self.current_frame].surface
        return pygame.Surface((64, 64))
    
    def reset(self):
        self.current_frame = 0
        self.frame_timer = 0
        self.finished = False

class UltimateAssetManager:
    """Enhanced asset manager combining all asset systems"""
    
    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.enhanced_manager = EnhancedAssetManager(assets_path)
        self.character_manager = CharacterAssetManager(assets_path)
        self.animations = {}
        self.current_theme = "cave"
        self.music_channel = None
        
        print("🎮 Ultimate Asset Manager initialized with enhanced features!")
    
    def load_character_animations(self, character_id: str):
        """Load character animations with enhanced optimization"""
        print(f"🎭 Loading ultimate animations for {character_id}")
        self.animations.clear()
        
        # Get character animations from legacy character manager
        character_animations = self.character_manager.get_character_animations(character_id)
        
        # Frame durations for different animation types
        frame_durations = {
            'idle': 250,
            'walk': 150,
            'run': 150,
            'dash': 100,
            'jump': 100,
            'attack': 100,
            'death': 200
        }
        
        # Convert to optimized Animation objects
        for anim_name, frames in character_animations.items():
            if frames:
                duration = frame_durations.get(anim_name, 200)
                is_looping = anim_name not in ['jump', 'attack', 'death', 'dash']
                
                # Create optimized animation frames
                anim_frames = []
                for frame in frames:
                    optimized_frame = self.enhanced_manager.optimize_surface(frame)
                    anim_frames.append(AnimationFrame(optimized_frame, duration))
                
                self.animations[f'{character_id}_{anim_name}'] = Animation(anim_frames, loop=is_looping)
        
        # Load enhanced enemy animations
        self.load_enhanced_enemies()
    
    def load_enhanced_enemies(self):
        """Load enhanced enemy animations"""
        enemy_types = ['fire_skull', 'demon_idle', 'demon_attack', 'hell_hound_idle', 'hell_hound_run']
        
        for enemy_type in enemy_types:
            frames = self.character_manager.get_sprite_frames(enemy_type)
            if frames:
                is_attack = 'attack' in enemy_type
                duration = 150 if is_attack else 300
                
                anim_frames = []
                for frame in frames:
                    optimized_frame = self.enhanced_manager.optimize_surface(frame)
                    anim_frames.append(AnimationFrame(optimized_frame, duration))
                
                self.animations[enemy_type] = Animation(anim_frames, loop=not is_attack)
    
    def get_environment_background(self, level_name: str) -> pygame.Surface:
        """Get appropriate background for level with comprehensive environment mapping"""
        theme_map = {
            # Original levels (now redirected)
            'level_1': 'cave_bg_1',
            'level_2': 'cave_bg_2', 
            'level_3': 'cave_bg_3',
            
            # Cave environments
            'cave_depths': 'cave_bg_1',
            'cave_passages': 'cave_bg_2',
            'cave_chamber': 'cave_bg_3',
            
            # Gothic environments (use cave backgrounds for now, could add gothic-specific later)
            'gothic_castle': 'cave_bg_4a',
            'castle_interior': 'cave_bg_4b',
            'gothic_town': 'cave_bg_1',
            
            # Night environments
            'night_town': 'cave_bg_2',
            'haunted_forest': 'cave_bg_3',
            
            # Mountain environments
            'mountain_pass': 'cave_bg_4a',
            'rocky_cliffs': 'cave_bg_4b',
            
            # Underground dangerous areas
            'lava_caverns': 'cave_bg_1',
            'treasure_chamber': 'cave_bg_2',
            
            # Pixel platformer levels
            'pixel_dungeon': 'cave_bg_3',
            'pixel_forest': 'cave_bg_4a',
            
            # Ocean and water levels
            'underwater_ruins': 'cave_bg_4b',
            'ocean_depths': 'cave_bg_1',
            
            # Sci-fi environments
            'scifi_lab': 'cave_bg_2',
            'alien_world': 'cave_bg_3',
            
            # Final boss areas
            'demon_throne': 'cave_bg_4a',
            'final_sanctum': 'cave_bg_4b'
        }
        
        bg_id = theme_map.get(level_name, 'cave_bg_1')
        bg = self.enhanced_manager.get_environment(bg_id)
        
        if bg:
            # Scale to screen size if needed
            if bg.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
                bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            return self.enhanced_manager.optimize_surface(bg)
        
        # Fallback to procedural background
        return self.create_fallback_background()
    
    def create_fallback_background(self) -> pygame.Surface:
        """Create beautiful procedural background if assets are missing"""
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(20 + ratio * 40)
            g = int(15 + ratio * 30)  
            b = int(35 + ratio * 60)
            pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Add atmospheric elements
        for i in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 4)
            brightness = random.randint(50, 150)
            color = (brightness, brightness//2, brightness//3)
            pygame.draw.circle(bg, color, (x, y), size)
        
        return bg
    
    def play_sound(self, sound_id: str, volume: float = 1.0):
        """Play enhanced sound effect"""
        self.enhanced_manager.play_sound(sound_id, volume)
    
    def start_background_music(self, theme: str = "cave"):
        """Start themed background music"""
        # For now, we'll use silence or procedural music
        # In a full implementation, you'd load and play actual music files
        pass
    
    def get_texture(self, texture_id: str) -> pygame.Surface:
        """Get enhanced texture"""
        return self.enhanced_manager.get_texture(texture_id)
    
    def get_ui_element(self, element_id: str) -> pygame.Surface:
        """Get UI element"""
        return self.enhanced_manager.get_ui_element(element_id)

class Entity:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.facing = Direction.RIGHT
        
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def apply_gravity(self):
        if not self.on_ground:
            self.vel_y += GRAVITY
    
    def update_position(self):
        self.x += self.vel_x
        self.y += self.vel_y
    
    def take_damage(self, amount: int):
        self.health = max(0, self.health - amount)
        return self.health <= 0

class UltimatePlayer(Entity):
    """Enhanced player with all new features"""
    
    def __init__(self, x: int, y: int, character_id: str, asset_manager: UltimateAssetManager):
        super().__init__(x, y, 64, 80)
        self.character_id = character_id
        self.asset_manager = asset_manager
        self.current_animation = f'{character_id}_idle'
        
        # Enhanced abilities
        self.souls = 0
        self.level = 1
        self.experience = 0
        self.attacking = False
        self.attack_timer = 0
        self.invulnerable_timer = 0
        self.dash_cooldown = 0
        self.jump_count = 0
        self.max_jumps = 2
        
        # Character-specific abilities
        self.abilities = self.get_character_abilities(character_id)
        
        # Visual effects
        self.particles = []
        self.screen_shake = 0
        
        # Camera following
        self.camera_target_x = x
        
        # Input tracking
        self.was_jumping = False
        
        print(f"✨ Ultimate player created: {character_id} with {len(self.abilities)} abilities")
    
    def get_character_abilities(self, character_id: str) -> Dict[str, Any]:
        """Get character-specific abilities and stats"""
        abilities = {
            'gothicvania_hero': {
                'max_jumps': 2,
                'dash_available': False,
                'attack_damage': 50,
                'speed_multiplier': 1.0,
                'special_ability': 'heavy_attack'
            },
            'female_adventurer': {
                'max_jumps': 3,  # Triple jump
                'dash_available': True,
                'attack_damage': 40,
                'speed_multiplier': 1.2,
                'special_ability': 'quick_dash'
            }
        }
        
        return abilities.get(character_id, abilities['gothicvania_hero'])
    
    def handle_input(self, keys: Dict[int, bool], dt: int):
        """Enhanced input handling with new abilities"""
        # Movement
        self.vel_x = 0
        
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            self.vel_x = -PLAYER_SPEED * self.abilities['speed_multiplier']
            self.facing = Direction.LEFT
            if self.on_ground:
                self.current_animation = f'{self.character_id}_run'
        
        elif keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            self.vel_x = PLAYER_SPEED * self.abilities['speed_multiplier']
            self.facing = Direction.RIGHT
            if self.on_ground:
                self.current_animation = f'{self.character_id}_run'
        else:
            if self.on_ground and not self.attacking:
                self.current_animation = f'{self.character_id}_idle'
        
        # Enhanced jumping system
        if keys.get(pygame.K_SPACE) and not self.was_jumping:
            if self.jump_count < self.abilities['max_jumps']:
                self.vel_y = JUMP_STRENGTH
                self.on_ground = False
                self.jump_count += 1
                self.current_animation = f'{self.character_id}_jump'
                self.asset_manager.play_sound('jump', 0.7)
                self.create_jump_particles()
        
        self.was_jumping = keys.get(pygame.K_SPACE, False)
        
        # Attack
        if keys.get(pygame.K_x) and not self.attacking and self.attack_timer <= 0:
            self.start_attack()
        
        # Dash (if available)
        if (keys.get(pygame.K_z) and self.abilities['dash_available'] 
            and self.dash_cooldown <= 0):
            self.start_dash()
        
        # Update timers
        if self.attack_timer > 0:
            self.attack_timer -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
    
    def start_attack(self):
        """Start attack with enhanced effects"""
        self.attacking = True
        self.attack_timer = 300
        self.current_animation = f'{self.character_id}_attack'
        self.asset_manager.play_sound('attack', 0.8)
        self.create_attack_particles()
        self.screen_shake = 5
    
    def start_dash(self):
        """Start dash ability with visual effects"""
        dash_speed = 15 * self.abilities['speed_multiplier']
        self.vel_x = dash_speed if self.facing == Direction.RIGHT else -dash_speed
        self.dash_cooldown = 1000
        self.current_animation = f'{self.character_id}_dash'
        self.invulnerable_timer = 200  # Brief invulnerability during dash
        self.create_dash_particles()
        self.screen_shake = 3
    
    def create_jump_particles(self):
        """Create particle effects for jumping"""
        for i in range(8):
            particle = {
                'x': self.x + self.width // 2 + random.randint(-10, 10),
                'y': self.y + self.height,
                'dx': random.uniform(-2, 2),
                'dy': random.uniform(-1, 1),
                'life': 500,
                'color': (150, 200, 255)
            }
            self.particles.append(particle)
    
    def create_attack_particles(self):
        """Create particle effects for attacks"""
        direction = 1 if self.facing == Direction.RIGHT else -1
        for i in range(12):
            particle = {
                'x': self.x + self.width // 2 + direction * 20,
                'y': self.y + self.height // 2 + random.randint(-15, 15),
                'dx': direction * random.uniform(3, 8),
                'dy': random.uniform(-3, 3),
                'life': 300,
                'color': (255, 200, 100)
            }
            self.particles.append(particle)
    
    def create_dash_particles(self):
        """Create particle effects for dashing"""
        for i in range(15):
            particle = {
                'x': self.x + random.randint(0, self.width),
                'y': self.y + random.randint(0, self.height),
                'dx': random.uniform(-4, 4),
                'dy': random.uniform(-2, 2),
                'life': 600,
                'color': (200, 150, 255)
            }
            self.particles.append(particle)
    
    def update(self, dt: int, platforms: List[pygame.Rect]):
        """Enhanced update with particle effects"""
        # Update position
        self.apply_gravity()
        self.update_position()
        
        # Platform collision
        self.handle_platform_collision(platforms)
        
        # Update camera target
        self.camera_target_x = self.x - SCREEN_WIDTH // 2
        
        # Update particles
        self.update_particles(dt)
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 0.01)
        
        # Update animation
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
        
        # Reset attack state
        if self.attack_timer <= 0:
            self.attacking = False
    
    def update_particles(self, dt: int):
        """Update particle system"""
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= dt
            
            # Add gravity to some particles
            particle['dy'] += 0.1
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Enhanced collision with better ground detection"""
        player_rect = self.get_rect()
        self.on_ground = False
        
        for platform in platforms:
            if player_rect.colliderect(platform):
                # Vertical collision
                if self.vel_y > 0 and player_rect.bottom <= platform.top + 15:
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0  # Reset jump count on landing
                
                # Horizontal collision
                elif self.vel_x > 0 and player_rect.right <= platform.left + 10:
                    self.x = platform.left - self.width
                    self.vel_x = 0
                elif self.vel_x < 0 and player_rect.left >= platform.right - 10:
                    self.x = platform.right
                    self.vel_x = 0
    
    def get_attack_rect(self) -> pygame.Rect:
        """Get enhanced attack hitbox"""
        attack_width = 80
        attack_height = 60
        
        if self.facing == Direction.RIGHT:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - attack_width
        
        attack_y = self.y + (self.height - attack_height) // 2
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0):
        """Enhanced drawing with particles and effects"""
        # Apply screen shake
        shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
        shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
        
        draw_x = self.x - camera_x + shake_x
        draw_y = self.y + shake_y
        
        # Draw particles behind player
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = min(255, particle['life'] // 2)
                color = (*particle['color'], alpha)
                particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color[:3], (3, 3), 3)
                screen.blit(particle_surface, (particle['x'] - camera_x + shake_x, 
                                             particle['y'] + shake_y))
        
        # Draw player
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            # Check if frame is valid
            if frame and frame.get_size() != (0, 0):
                # Flip for direction
                if self.facing == Direction.LEFT:
                    frame = pygame.transform.flip(frame, True, False)
                
                # Invulnerability flashing
                if self.invulnerable_timer > 0 and (self.invulnerable_timer // 100) % 2:
                    # Make player flash during invulnerability
                    flash_surface = frame.copy()
                    flash_surface.fill((255, 255, 255, 100), special_flags=pygame.BLEND_ADD)
                    screen.blit(flash_surface, (draw_x, draw_y))
                else:
                    screen.blit(frame, (draw_x, draw_y))
            else:
                # Fallback: Draw colored rectangle if animation frame is invalid
                fallback_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
                pygame.draw.rect(screen, (100, 200, 255), fallback_rect)
                pygame.draw.rect(screen, (255, 255, 255), fallback_rect, 2)
        else:
            # Fallback: Draw colored rectangle if animation not found
            print(f"⚠️ Animation not found: {self.current_animation}")
            print(f"Available animations: {list(self.asset_manager.animations.keys())}")
            fallback_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
            pygame.draw.rect(screen, (255, 100, 100), fallback_rect)
            pygame.draw.rect(screen, (255, 255, 255), fallback_rect, 2)
            
            # Draw character ID as text
            if hasattr(self, 'character_id'):
                font = pygame.font.Font(None, 24)
                text = font.render(self.character_id[:8], True, (255, 255, 255))
                screen.blit(text, (draw_x, draw_y - 20))

class UltimateEnemy(Entity):
    """Enhanced enemy with better AI and effects"""
    
    def __init__(self, x: int, y: int, width: int, height: int, enemy_type: str, asset_manager: UltimateAssetManager):
        super().__init__(x, y, width, height)
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager
        self.current_animation = enemy_type
        
        # Enhanced AI properties
        self.aggro_range = 200
        self.attack_range = 80
        self.speed = 2
        self.attack_cooldown = 0
        self.damage = 20
        self.souls_value = 10
        self.particles = []
        
        # Enemy-specific stats
        self.setup_enemy_stats(enemy_type)
    
    def setup_enemy_stats(self, enemy_type: str):
        """Set up enemy-specific statistics"""
        stats = {
            'fire_skull': {
                'health': 75, 'speed': 3, 'damage': 30, 'souls': 15,
                'special': 'floating'
            },
            'hell_hound': {
                'health': 100, 'speed': 4, 'damage': 25, 'souls': 20,
                'special': 'charge'
            },
            'demon': {
                'health': 150, 'speed': 2, 'damage': 40, 'souls': 30,
                'special': 'magic_attack'
            }
        }
        
        if enemy_type in stats:
            stat = stats[enemy_type]
            self.health = stat['health']
            self.max_health = self.health
            self.speed = stat['speed']
            self.damage = stat['damage']
            self.souls_value = stat['souls']
            self.special_ability = stat['special']
    
    def update(self, dt: int, player: UltimatePlayer, platforms: List[pygame.Rect]):
        """Enhanced AI with special abilities"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Calculate distance to player
        player_distance = abs(self.x - player.x)
        
        # Enhanced AI behavior
        if player_distance < self.aggro_range:
            # Move towards player
            if player.x < self.x:
                self.vel_x = -self.speed
                self.facing = Direction.LEFT
            elif player.x > self.x:
                self.vel_x = self.speed
                self.facing = Direction.RIGHT
            
            # Special abilities
            if player_distance < self.attack_range and self.attack_cooldown <= 0:
                self.perform_special_attack(player)
        else:
            self.vel_x = 0
        
        # Apply physics
        if self.special_ability != 'floating':
            self.apply_gravity()
        
        self.update_position()
        
        # Enhanced collision
        if self.special_ability != 'floating':
            self.handle_platform_collision(platforms)
        
        # Update particles
        self.update_particles(dt)
        
        # Update animation
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
    
    def perform_special_attack(self, player: UltimatePlayer):
        """Perform enemy-specific special attack"""
        self.attack_cooldown = 2000  # 2 second cooldown
        
        if self.special_ability == 'floating':
            # Fire skull creates fire particles
            self.create_fire_particles()
        elif self.special_ability == 'charge':
            # Hell hound charges forward
            charge_speed = 8
            self.vel_x = charge_speed if self.facing == Direction.RIGHT else -charge_speed
        elif self.special_ability == 'magic_attack':
            # Demon creates magic effect
            self.create_magic_particles()
    
    def create_fire_particles(self):
        """Create fire particle effects"""
        for i in range(10):
            particle = {
                'x': self.x + self.width // 2,
                'y': self.y + self.height // 2,
                'dx': random.uniform(-3, 3),
                'dy': random.uniform(-4, -1),
                'life': 800,
                'color': random.choice([(255, 100, 0), (255, 200, 0), (255, 50, 0)])
            }
            self.particles.append(particle)
    
    def create_magic_particles(self):
        """Create magic particle effects"""
        for i in range(15):
            particle = {
                'x': self.x + random.randint(0, self.width),
                'y': self.y + random.randint(0, self.height),
                'dx': random.uniform(-2, 2),
                'dy': random.uniform(-3, 3),
                'life': 1000,
                'color': random.choice([(150, 0, 255), (255, 0, 150), (0, 150, 255)])
            }
            self.particles.append(particle)
    
    def update_particles(self, dt: int):
        """Update enemy particle effects"""
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= dt
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Enhanced enemy collision"""
        enemy_rect = self.get_rect()
        self.on_ground = False
        
        for platform in platforms:
            if enemy_rect.colliderect(platform):
                if self.vel_y > 0 and enemy_rect.bottom <= platform.top + 10:
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0):
        """Enhanced enemy drawing with particles"""
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = min(255, particle['life'] // 3)
                color = (*particle['color'], alpha)
                particle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color[:3], (4, 4), 4)
                screen.blit(particle_surface, (particle['x'] - camera_x, particle['y']))
        
        # Draw enemy
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            if self.facing == Direction.LEFT:
                frame = pygame.transform.flip(frame, True, False)
            
            draw_x = self.x - camera_x
            screen.blit(frame, (draw_x, self.y))
            
            # Health bar for stronger enemies
            if self.max_health > 100:
                self.draw_health_bar(screen, draw_x)
    
    def draw_health_bar(self, screen: pygame.Surface, x: int):
        """Draw enemy health bar"""
        bar_width = self.width
        bar_height = 6
        bar_y = self.y - 15
        
        # Background
        pygame.draw.rect(screen, (100, 0, 0), (x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_ratio = self.health / self.max_health
        fill_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (255, 0, 0), (x, bar_y, fill_width, bar_height))

class UltimateUI:
    """Enhanced UI with beautiful designs and animations"""
    
    def __init__(self, screen_width: int, screen_height: int, asset_manager: UltimateAssetManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.asset_manager = asset_manager
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)
        
        # UI animations
        self.ui_animation_time = 0
        self.notification_queue = []
    
    def update(self, dt: float):
        """Update UI animations"""
        self.ui_animation_time += dt
        
        # Update notifications
        for notification in self.notification_queue[:]:
            notification['life'] -= dt
            if notification['life'] <= 0:
                self.notification_queue.remove(notification)
    
    def draw_enhanced_hud(self, screen: pygame.Surface, player: UltimatePlayer, fps: float, level_name: str):
        """Draw enhanced HUD with animations and effects"""
        
        # Health bar with gradient and glow
        health_ratio = player.health / player.max_health
        self.draw_gradient_bar(screen, 30, 30, 250, 25, health_ratio, 
                              (255, 0, 0), (0, 255, 0), "Health")
        
        # Experience bar
        exp_ratio = (player.experience % 100) / 100
        self.draw_gradient_bar(screen, 30, 65, 250, 15, exp_ratio,
                              (100, 100, 255), (255, 255, 100), "EXP")
        
        # Character info panel with glow effect
        panel_surface = pygame.Surface((300, 120), pygame.SRCALPHA)
        panel_surface.fill((20, 20, 40, 200))
        
        # Add border glow
        glow_surface = pygame.Surface((310, 130), pygame.SRCALPHA)
        glow_surface.fill((100, 150, 255, 50))
        screen.blit(glow_surface, (25, 100))
        screen.blit(panel_surface, (30, 105))
        
        # Character info text
        char_name = player.character_id.replace('_', ' ').title()
        info_texts = [
            f"Character: {char_name}",
            f"Level: {player.level}",
            f"Souls: {player.souls}",
            f"Abilities: {len(player.abilities)}"
        ]
        
        for i, text in enumerate(info_texts):
            color = (255, 255, 255) if i == 0 else (200, 200, 200)
            text_surface = self.small_font.render(text, True, color)
            screen.blit(text_surface, (40, 115 + i * 20))
        
        # Ability cooldowns with circular progress
        self.draw_ability_cooldowns(screen, player)
        
        # Level indicator
        level_text = self.font.render(f"Level: {level_name}", True, (255, 255, 255))
        level_glow = self.font.render(f"Level: {level_name}", True, (100, 150, 255))
        screen.blit(level_glow, (32, 252))
        screen.blit(level_text, (30, 250))
        
        # Enhanced FPS counter with color coding
        fps_color = (0, 255, 0) if fps >= 55 else (255, 255, 0) if fps >= 45 else (255, 0, 0)
        fps_text = self.small_font.render(f"FPS: {fps:.1f}", True, fps_color)
        screen.blit(fps_text, (self.screen_width - 150, 30))
        
        # Draw notifications
        self.draw_notifications(screen)
    
    def draw_gradient_bar(self, screen: pygame.Surface, x: int, y: int, width: int, height: int, 
                         ratio: float, color1: tuple, color2: tuple, label: str):
        """Draw a beautiful gradient progress bar"""
        # Background
        bg_surface = pygame.Surface((width + 4, height + 4))
        bg_surface.fill((50, 50, 50))
        screen.blit(bg_surface, (x - 2, y - 2))
        
        # Main bar background
        bar_bg = pygame.Surface((width, height))
        bar_bg.fill((30, 30, 30))
        screen.blit(bar_bg, (x, y))
        
        # Fill bar with gradient
        fill_width = int(width * ratio)
        if fill_width > 0:
            for i in range(fill_width):
                progress = i / width
                r = int(color1[0] * (1 - progress) + color2[0] * progress)
                g = int(color1[1] * (1 - progress) + color2[1] * progress)
                b = int(color1[2] * (1 - progress) + color2[2] * progress)
                pygame.draw.line(screen, (r, g, b), (x + i, y), (x + i, y + height))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 2)
        
        # Label
        label_text = self.small_font.render(label, True, (255, 255, 255))
        screen.blit(label_text, (x + width + 10, y))
    
    def draw_ability_cooldowns(self, screen: pygame.Surface, player: UltimatePlayer):
        """Draw circular ability cooldown indicators"""
        if player.abilities['dash_available']:
            # Dash cooldown
            cooldown_ratio = 1.0 - (player.dash_cooldown / 1000.0)
            self.draw_circular_cooldown(screen, self.screen_width - 100, 100, 30, 
                                      cooldown_ratio, "DASH", (255, 100, 255))
        
        # Attack cooldown
        attack_ratio = 1.0 - (player.attack_timer / 300.0)
        self.draw_circular_cooldown(screen, self.screen_width - 180, 100, 30,
                                  attack_ratio, "ATK", (255, 200, 100))
    
    def draw_circular_cooldown(self, screen: pygame.Surface, x: int, y: int, radius: int,
                              ratio: float, label: str, color: tuple):
        """Draw circular cooldown indicator"""
        # Background circle
        pygame.draw.circle(screen, (50, 50, 50), (x, y), radius + 2)
        pygame.draw.circle(screen, (30, 30, 30), (x, y), radius)
        
        # Cooldown arc
        if ratio > 0:
            angle = int(360 * ratio)
            points = [(x, y)]
            for i in range(angle + 1):
                angle_rad = math.radians(i - 90)
                px = x + radius * math.cos(angle_rad)
                py = y + radius * math.sin(angle_rad)
                points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points)
        
        # Border
        pygame.draw.circle(screen, (100, 100, 100), (x, y), radius, 2)
        
        # Label
        label_surface = self.small_font.render(label, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=(x, y + radius + 20))
        screen.blit(label_surface, label_rect)
    
    def draw_notifications(self, screen: pygame.Surface):
        """Draw floating notifications"""
        for i, notification in enumerate(self.notification_queue):
            alpha = min(255, notification['life'])
            y_offset = i * 40
            
            # Notification background
            notif_surface = pygame.Surface((300, 35), pygame.SRCALPHA)
            notif_surface.fill((40, 40, 60, alpha // 2))
            
            # Text
            text_surface = self.font.render(notification['text'], True, notification['color'])
            
            notif_rect = notif_surface.get_rect()
            notif_rect.center = (self.screen_width // 2, 100 + y_offset)
            
            screen.blit(notif_surface, notif_rect)
            
            text_rect = text_surface.get_rect(center=notif_rect.center)
            screen.blit(text_surface, text_rect)
    
    def add_notification(self, text: str, color: tuple = (255, 255, 255), duration: int = 3000):
        """Add notification to queue"""
        notification = {
            'text': text,
            'color': color,
            'life': duration
        }
        self.notification_queue.append(notification)

class UltimateReserkaGothic:
    """The ultimate enhanced Reserka Gothic experience with pixel art integration"""
    
    def __init__(self):
        # Initialize Pygame with optimizations
        pygame.init()
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Create display with enhanced flags
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Reserka Gothic - Ultimate Enhanced Edition with Pixel Art")
        
        # Set icon if available
        try:
            icon = pygame.image.load("assets/ui/icon.png")
            pygame.display.set_icon(icon)
        except:
            pass
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Initialize enhanced systems
        assets_path = Path(__file__).parent.parent / "assets"
        self.asset_manager = UltimateAssetManager(assets_path)
        
        # Initialize pixel texture manager
        try:
            self.pixel_texture_manager = PixelTextureManager(assets_path)
            self.pixel_texture_manager.create_terrain_variations()
            self.pixel_texture_manager.optimize_textures()
            print("🎨 Pixel textures integrated successfully!")
        except Exception as e:
            print(f"⚠️ Could not initialize pixel textures: {e}")
            self.pixel_texture_manager = None
        
        # Initialize advanced graphics enhancer
        try:
            self.graphics_enhancer = GraphicsEnhancer(SCREEN_WIDTH, SCREEN_HEIGHT)
            # Add ambient lighting for gothic atmosphere
            self.graphics_enhancer.add_ambient_light()
            print("🎨 Advanced Graphics Enhancer integrated successfully!")
        except Exception as e:
            print(f"⚠️ Could not initialize graphics enhancer: {e}")
            self.graphics_enhancer = None
        
        self.menu_system = MenuSystem(self.screen, self.asset_manager.enhanced_manager)
        self.level_manager = EnhancedLevelManager(SCREEN_WIDTH, SCREEN_HEIGHT, self.asset_manager.enhanced_manager)
        
        # Character selection
        self.character_selection = CharacterSelection(self.screen, assets_path)
        self.selected_character = None
        
        # Game objects
        self.player = None
        self.enemies = []
        self.ui = UltimateUI(SCREEN_WIDTH, SCREEN_HEIGHT, self.asset_manager)
        
        # Enhanced camera system
        self.camera_x = 0
        self.camera_smooth = 0.15
        self.camera_shake = 0
        
        # Game state - Start with menu instead of jumping to gameplay
        self.state = GameState.MENU  # Ensure we start in menu state
        self.keys = {}
        self.transition_timer = 0
        self.transition_target = None
        
        # Performance monitoring
        self.frame_times = []
        self.fps_counter = 0
        
        # Settings
        self.settings = self.menu_system.get_settings()
        
        print("🎮✨ Ultimate Reserka Gothic initialized!")
        print("🔥 Enhanced with pixel art, parallax scrolling, and 64-bit feel!")
        
        # Start background music
        self.asset_manager.start_background_music()
    
    def create_enhanced_enemies_for_level(self):
        """Create enhanced enemies with new AI"""
        self.enemies.clear()
        current_level = self.level_manager.current_level
        
        enemy_configs = {
            "level_1": [
                ('fire_skull', 400, 460, 48, 48),
                ('hell_hound', 800, 260, 64, 64),
            ],
            "level_2": [
                ('fire_skull', 300, 360, 48, 48),
                ('demon', 600, 180, 80, 80),
                ('hell_hound', 1000, 220, 64, 64),
            ],
            "level_3": [
                ('fire_skull', 200, 300, 48, 48),
                ('fire_skull', 600, 200, 48, 48),
                ('demon', 900, 150, 80, 80),
                ('hell_hound', 450, 400, 64, 64),
            ]
        }
        
        if current_level in enemy_configs:
            for enemy_type, x, y, width, height in enemy_configs[current_level]:
                enemy = UltimateEnemy(x, y, width, height, enemy_type, self.asset_manager)
                self.enemies.append(enemy)
    
    def handle_events(self):
        """Enhanced event handling"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys[event.key] = True
                
                # Global shortcuts
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_F1:
                    self.settings['show_fps'] = not self.settings['show_fps']
                
                # State-specific handling
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                        self.menu_system.show_pause_menu()
                    elif event.key == pygame.K_e:
                        # Door interaction
                        door = self.level_manager.check_door_collision(self.player.get_rect())
                        if door:
                            self.transition_to_level(door)
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                        self.reset_game()
            
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False
            
            # Menu system events
            if self.state in [GameState.MENU, GameState.PAUSED]:
                result = self.menu_system.handle_event(event)
                if result == "start_game":
                    self.state = GameState.CHARACTER_SELECT
                elif result == "resume_game":
                    self.state = GameState.PLAYING
                elif result == "main_menu":
                    self.state = GameState.MENU
                    self.reset_game()
                elif result == "exit_game":
                    self.running = False
            
            elif self.state == GameState.CHARACTER_SELECT:
                result = self.character_selection.handle_event(event)
                if result:
                    if result['action'] == 'select':
                        self.selected_character = result['character_id']
                        self.start_enhanced_game(self.selected_character)
                    elif result['action'] == 'back':
                        self.state = GameState.MENU
    
    def start_enhanced_game(self, character_id: str):
        """Start the enhanced game experience"""
        print(f"🚀 Starting ultimate game with {character_id}")
        
        # Load character animations
        self.asset_manager.load_character_animations(character_id)
        
        # Create enhanced player
        self.player = UltimatePlayer(100, 600, character_id, self.asset_manager)
        
        # Create enhanced enemies
        self.create_enhanced_enemies_for_level()
        
        # Add torch lights for gothic atmosphere
        if self.graphics_enhancer:
            # Add torch lights at various positions
            self.graphics_enhancer.add_torch_light(200, 500)
            self.graphics_enhancer.add_torch_light(500, 300)
            self.graphics_enhancer.add_torch_light(800, 450)
            self.graphics_enhancer.add_torch_light(1100, 250)
            print("🔥 Torch lights added for dramatic atmosphere!")
        
        # UI notification
        self.ui.add_notification(f"Welcome, {character_id.replace('_', ' ').title()}!", 
                               (100, 255, 100), 4000)
        
        # Switch to playing state
        self.state = GameState.PLAYING
    
    def transition_to_level(self, door):
        """Enhanced level transition with effects"""
        print(f"🌟 Enhanced transition to {door.target_level}")
        
        if self.level_manager.switch_level(door.target_level):
            # Enhanced player positioning
            self.player.x = door.target_x
            self.player.y = door.target_y
            self.player.vel_x = 0
            self.player.vel_y = 0
            
            # Create transition particles
            for i in range(50):
                particle = {
                    'x': self.player.x + random.randint(-50, 50),
                    'y': self.player.y + random.randint(-50, 50),
                    'dx': random.uniform(-5, 5),
                    'dy': random.uniform(-5, 5),
                    'life': 1500,
                    'color': (100, 200, 255)
                }
                self.player.particles.append(particle)
            
            # Enhanced enemies for new level
            self.create_enhanced_enemies_for_level()
            
            # UI notification
            level_display = door.target_level.replace('_', ' ').title()
            self.ui.add_notification(f"Entered {level_display}", (255, 200, 100), 3000)
            
            # Transition effect
            self.state = GameState.LEVEL_TRANSITION
            self.transition_timer = 1000
            self.transition_target = door.target_level
            self.camera_shake = 10
    
    def update(self):
        """Ultimate game update with all enhancements"""
        dt = self.clock.get_time()
        
        # Update frame timing
        self.frame_times.append(dt)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
        
        # Update UI
        self.ui.update(dt)
        
        if self.state == GameState.MENU:
            self.menu_system.update(dt)
            
        elif self.state == GameState.CHARACTER_SELECT:
            self.character_selection.update(dt / 1000.0)
            
        elif self.state == GameState.LEVEL_TRANSITION:
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.state = GameState.PLAYING
                
        elif self.state == GameState.PLAYING and self.player:
            # Enhanced player update
            self.player.handle_input(self.keys, dt)
            platforms = self.level_manager.get_collision_rects()
            self.player.update(dt, platforms)
            
            # Update graphics enhancer effects
            if self.graphics_enhancer:
                self.graphics_enhancer.update(dt / 1000.0)  # Convert to seconds
            
            # Enhanced camera with smooth following and shake
            target_camera_x = self.player.camera_target_x
            self.camera_x += (target_camera_x - self.camera_x) * self.camera_smooth
            
            # Apply camera shake
            if self.player.screen_shake > 0 or self.camera_shake > 0:
                shake_amount = max(self.player.screen_shake, self.camera_shake)
                self.camera_x += random.uniform(-shake_amount, shake_amount)
                if self.camera_shake > 0:
                    self.camera_shake = max(0, self.camera_shake - dt * 0.01)
            
            # Clamp camera
            self.camera_x = max(0, min(self.camera_x, SCREEN_WIDTH))
            
            # Enhanced enemy updates
            for enemy in self.enemies[:]:
                # Cull distant enemies for performance
                if abs(enemy.x - self.player.x) < 1000:
                    enemy.update(dt, self.player, platforms)
                
                # Enhanced combat
                if self.player.attacking:
                    attack_rect = self.player.get_attack_rect()
                    if attack_rect.colliderect(enemy.get_rect()):
                        damage = self.player.abilities['attack_damage']
                        if enemy.take_damage(damage):
                            # Enemy defeated
                            self.player.souls += enemy.souls_value
                            self.player.experience += 10
                            self.ui.add_notification(f"+{enemy.souls_value} Souls!", 
                                                   (255, 215, 0), 2000)
                            
                            # Create death particles
                            for i in range(20):
                                particle = {
                                    'x': enemy.x + enemy.width // 2,
                                    'y': enemy.y + enemy.height // 2,
                                    'dx': random.uniform(-6, 6),
                                    'dy': random.uniform(-8, -2),
                                    'life': 1000,
                                    'color': (255, 0, 0)
                                }
                                self.player.particles.append(particle)
                            
                            self.enemies.remove(enemy)
                            self.asset_manager.play_sound('attack', 0.5)
                
                # Enhanced enemy damage
                if (enemy.get_rect().colliderect(self.player.get_rect()) 
                    and self.player.invulnerable_timer <= 0):
                    self.player.take_damage(enemy.damage)
                    self.player.invulnerable_timer = 1500
                    self.camera_shake = 8
                    self.ui.add_notification(f"-{enemy.damage} HP", (255, 0, 0), 1500)
                    
                    if self.player.health <= 0:
                        self.state = GameState.GAME_OVER
            
            # Level up system
            if self.player.experience >= self.player.level * 100:
                self.player.level += 1
                self.player.experience = 0
                self.player.max_health += 10
                self.player.health = self.player.max_health
                self.ui.add_notification(f"LEVEL UP! Level {self.player.level}", 
                                       (255, 255, 0), 4000)
        
        elif self.state == GameState.PAUSED:
            self.menu_system.update(dt)
    
    def draw(self):
        """Ultimate rendering with all visual enhancements"""
        # Clear screen
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.menu_system.draw()
            
        elif self.state == GameState.CHARACTER_SELECT:
            self.character_selection.draw()
            
        elif self.state in [GameState.PLAYING, GameState.LEVEL_TRANSITION] and self.player:
            # Enhanced pixel art parallax background rendering
            if self.pixel_texture_manager:
                # Update animated textures
                self.pixel_texture_manager.update_animations(self.clock.get_time())
                
                # Draw multi-layer parallax background with pixel art
                self.pixel_texture_manager.draw_parallax_background(self.screen, int(self.camera_x))
                
                # Add atmospheric overlay for depth
                atmosphere_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                atmosphere_overlay.fill((20, 30, 50, 30))
                self.screen.blit(atmosphere_overlay, (0, 0))
            else:
                # Fallback to original background system
                bg = self.asset_manager.get_environment_background(self.level_manager.current_level)
                if bg:
                    # Parallax scrolling
                    bg_x = -(self.camera_x * 0.3) % bg.get_width()
                    self.screen.blit(bg, (bg_x, 0))
                    if bg_x > 0:
                        self.screen.blit(bg, (bg_x - bg.get_width(), 0))
                    
                    # Additional parallax layers
                    bg_x2 = -(self.camera_x * 0.5) % bg.get_width()
                    dark_overlay = pygame.Surface(bg.get_size(), pygame.SRCALPHA)
                    dark_overlay.fill((0, 0, 50, 100))
                    bg_layer2 = bg.copy()
                    bg_layer2.blit(dark_overlay, (0, 0))
                    self.screen.blit(bg_layer2, (bg_x2, 0))
                    if bg_x2 > 0:
                        self.screen.blit(bg_layer2, (bg_x2 - bg.get_width(), 0))
            
            # Enhanced level rendering
            self.level_manager.draw_level(self.screen, int(self.camera_x), 0)
            
            # Enhanced enemy rendering with culling
            for enemy in self.enemies:
                if -200 <= enemy.x - self.camera_x <= SCREEN_WIDTH + 200:
                    enemy.draw(self.screen, int(self.camera_x))
            
            # Enhanced player rendering
            self.player.draw(self.screen, int(self.camera_x))
            
            # Enhanced UI
            fps = 1000.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0
            self.ui.draw_enhanced_hud(self.screen, self.player, fps, 
                                    self.level_manager.current_level)
            
            # Transition effects
            if self.state == GameState.LEVEL_TRANSITION:
                alpha = int(255 * (1 - self.transition_timer / 1000.0))
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                # Animated transition effect
                for i in range(0, SCREEN_WIDTH, 20):
                    wave_height = int(50 * math.sin(i * 0.02 + self.transition_timer * 0.01))
                    overlay.fill((255, 255, 255, alpha//3))
                    pygame.draw.rect(overlay, (100, 150, 255, alpha//2), 
                                   (i, SCREEN_HEIGHT//2 + wave_height - 25, 20, 50))
                
                self.screen.blit(overlay, (0, 0))
                
                if self.transition_target:
                    transition_text = self.ui.large_font.render(
                        f"Entering {self.transition_target.replace('_', ' ').title()}", 
                        True, (255, 255, 255))
                    text_rect = transition_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    self.screen.blit(transition_text, text_rect)
            
        elif self.state == GameState.PAUSED:
            # Draw game behind pause menu
            if self.player:
                bg = self.asset_manager.get_environment_background(self.level_manager.current_level)
                if bg:
                    self.screen.blit(bg, (0, 0))
                
                self.level_manager.draw_level(self.screen, int(self.camera_x), 0)
                for enemy in self.enemies:
                    if -200 <= enemy.x - self.camera_x <= SCREEN_WIDTH + 200:
                        enemy.draw(self.screen, int(self.camera_x))
                self.player.draw(self.screen, int(self.camera_x))
            
            # Draw pause menu overlay
            self.menu_system.draw()
            
        elif self.state == GameState.GAME_OVER:
            # Enhanced game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((139, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.ui.large_font.render("GAME OVER", True, (255, 255, 255))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            # Text glow effect
            glow_text = self.ui.large_font.render("GAME OVER", True, (255, 0, 0))
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH // 2 + 2, SCREEN_HEIGHT // 2 + 2))
            self.screen.blit(glow_text, glow_rect)
            self.screen.blit(game_over_text, text_rect)
            
            # Continue prompt
            continue_text = self.ui.font.render("Press ESCAPE to return to menu", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(continue_text, continue_rect)
        
        # Apply post-processing effects if graphics enhancer is available
        if (self.graphics_enhancer and 
            self.state in [GameState.PLAYING, GameState.LEVEL_TRANSITION, GameState.PAUSED]):
            self.screen = self.graphics_enhancer.apply_post_processing(self.screen)
        
        # Show FPS if enabled
        if self.settings.get('show_fps', False):
            fps = 1000.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0
            fps_text = self.ui.small_font.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, 10))
        
        pygame.display.flip()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        if self.settings['fullscreen']:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def reset_game(self):
        """Reset game to initial state"""
        self.player = None
        self.enemies = []
        self.selected_character = None
        self.level_manager.switch_level("level_1")
        self.camera_x = 0
    
    def run(self):
        """Ultimate game loop with enhanced performance"""
        print("🚀✨ Starting Ultimate Reserka Gothic Experience!")
        print("🎮 Enhanced with professional 64-bit feel and all new features!")
        print("🎮 Press keys to interact: WASD/Arrows=Move, SPACE=Jump, X=Attack, Z=Dash, E=Door, ESC=Pause")
        
        while self.running:
            # Target 60 FPS with vsync if enabled
            if self.settings.get('vsync', True):
                self.clock.tick(TARGET_FPS)
            else:
                self.clock.tick()
            
            try:
                self.handle_events()
                self.update()
                self.draw()
            except Exception as e:
                print(f"❌ Game error: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
        
        print("👋 Thanks for playing Ultimate Reserka Gothic!")
        pygame.quit()
        sys.exit()

def main():
    """Launch the ultimate Reserka Gothic experience"""
    try:
        game = UltimateReserkaGothic()
        game.run()
    except Exception as e:
        print(f"❌ Error starting Ultimate Reserka Gothic: {e}")
        print("🔧 Please check that all assets are properly installed")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
