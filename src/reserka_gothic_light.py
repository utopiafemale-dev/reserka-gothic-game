#!/usr/bin/env python3
"""
Reserka Gothic - Lightweight Edition
Optimized version without heavy graphics processing
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

# Import only essential systems (no heavy graphics)
from enhanced_asset_manager import EnhancedAssetManager
from menu_system import MenuSystem, MenuState
from enhanced_level_system import EnhancedLevelManager
from character_selection import CharacterSelection
from character_asset_manager import CharacterAssetManager
from metroidvania_camera import MetroidvaniaCamera, CameraConstraints, CameraMode
from metroidvania_progression import MetroidvaniaProgression, AbilityType

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

class LightweightAssetManager:
    """Lightweight asset manager without heavy processing"""
    
    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.enhanced_manager = EnhancedAssetManager(assets_path)
        self.character_manager = CharacterAssetManager(assets_path)
        self.animations = {}
        self.current_theme = "cave"
        
        print("🎮 Lightweight Asset Manager initialized!")
    
    def load_character_animations(self, character_id: str):
        """Load character animations without heavy optimization"""
        print(f"🎭 Loading lightweight animations for {character_id}")
        self.animations.clear()
        
        # Get character animations from character manager
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
        
        # Convert to Animation objects (no heavy optimization)
        for anim_name, frames in character_animations.items():
            if frames:
                duration = frame_durations.get(anim_name, 200)
                is_looping = anim_name not in ['jump', 'attack', 'death', 'dash']
                
                # Create animation frames without heavy processing
                anim_frames = []
                for frame in frames:
                    anim_frames.append(AnimationFrame(frame, duration))
                
                self.animations[f'{character_id}_{anim_name}'] = Animation(anim_frames, loop=is_looping)
        
        # Load lightweight enemy animations
        self.load_lightweight_enemies()
    
    def load_lightweight_enemies(self):
        """Load enemy animations without heavy processing"""
        enemy_types = ['fire_skull', 'demon_idle', 'demon_attack', 'hell_hound_idle', 'hell_hound_run']
        
        for enemy_type in enemy_types:
            frames = self.character_manager.get_sprite_frames(enemy_type)
            if frames:
                is_attack = 'attack' in enemy_type
                duration = 150 if is_attack else 300
                
                anim_frames = []
                for frame in frames:
                    anim_frames.append(AnimationFrame(frame, duration))
                
                self.animations[enemy_type] = Animation(anim_frames, loop=not is_attack)
    
    def get_environment_background(self, level_name: str) -> pygame.Surface:
        """Get simple background without heavy processing"""
        theme_map = {
            'level_1': 'cave_bg_1',
            'level_2': 'cave_bg_2', 
            'level_3': 'cave_bg_3',
        }
        
        bg_id = theme_map.get(level_name, 'cave_bg_1')
        bg = self.enhanced_manager.get_environment(bg_id)
        
        if bg:
            # Simple scaling without optimization
            if bg.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
                bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            return bg
        
        # Simple fallback background
        return self.create_simple_background()
    
    def create_simple_background(self) -> pygame.Surface:
        """Create simple procedural background"""
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Simple gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(20 + ratio * 40)
            g = int(15 + ratio * 30)  
            b = int(35 + ratio * 60)
            pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        return bg
    
    def play_sound(self, sound_id: str, volume: float = 1.0):
        """Play sound effect"""
        self.enhanced_manager.play_sound(sound_id, volume)

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

class LightweightPlayer(Entity):
    """Lightweight player without heavy particle effects"""
    
    def __init__(self, x: int, y: int, character_id: str, asset_manager: LightweightAssetManager):
        super().__init__(x, y, 64, 80)
        self.character_id = character_id
        self.asset_manager = asset_manager
        self.current_animation = f'{character_id}_idle'
        
        # Basic abilities
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
        
        # Camera following
        self.camera_target_x = x
        
        # Input tracking
        self.was_jumping = False
        
        print(f"✨ Lightweight player created: {character_id}")
    
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
        """Simple input handling"""
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
        
        # Jumping system
        if keys.get(pygame.K_SPACE) and not self.was_jumping:
            if self.jump_count < self.abilities['max_jumps']:
                self.vel_y = JUMP_STRENGTH
                self.on_ground = False
                self.jump_count += 1
                self.current_animation = f'{self.character_id}_jump'
                self.asset_manager.play_sound('jump', 0.7)
        
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
        """Start attack without heavy effects"""
        self.attacking = True
        self.attack_timer = 300
        self.current_animation = f'{self.character_id}_attack'
        self.asset_manager.play_sound('attack', 0.8)
    
    def start_dash(self):
        """Start dash ability without heavy effects"""
        dash_speed = 15 * self.abilities['speed_multiplier']
        self.vel_x = dash_speed if self.facing == Direction.RIGHT else -dash_speed
        self.dash_cooldown = 1000
        self.current_animation = f'{self.character_id}_dash'
        self.invulnerable_timer = 200  # Brief invulnerability during dash
    
    def update(self, dt: int, platforms: List[pygame.Rect]):
        """Simple update without heavy processing"""
        # Update position
        self.apply_gravity()
        self.update_position()
        
        # Platform collision
        self.handle_platform_collision(platforms)
        
        # Update camera target
        self.camera_target_x = self.x - SCREEN_WIDTH // 2
        
        # Update animation
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
        
        # Reset attack state
        if self.attack_timer <= 0:
            self.attacking = False
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Simple collision detection"""
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
        """Get attack hitbox"""
        attack_width = 80
        attack_height = 60
        
        if self.facing == Direction.RIGHT:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - attack_width
        
        attack_y = self.y + (self.height - attack_height) // 2
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0):
        """Simple drawing without heavy effects"""
        draw_x = self.x - camera_x
        draw_y = self.y
        
        # Draw player
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            # Check if frame is valid
            if frame and frame.get_size() != (0, 0):
                # Flip for direction
                if self.facing == Direction.LEFT:
                    frame = pygame.transform.flip(frame, True, False)
                
                # Simple invulnerability flashing
                if self.invulnerable_timer > 0 and (self.invulnerable_timer // 100) % 2:
                    # Make player flash during invulnerability
                    flash_surface = frame.copy()
                    flash_surface.fill((255, 255, 255, 100), special_flags=pygame.BLEND_ADD)
                    screen.blit(flash_surface, (draw_x, draw_y))
                else:
                    screen.blit(frame, (draw_x, draw_y))
            else:
                # Fallback: Draw colored rectangle
                fallback_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
                pygame.draw.rect(screen, (100, 200, 255), fallback_rect)
                pygame.draw.rect(screen, (255, 255, 255), fallback_rect, 2)

class LightweightEnemy(Entity):
    """Lightweight enemy without heavy effects"""
    
    def __init__(self, x: int, y: int, width: int, height: int, enemy_type: str, asset_manager: LightweightAssetManager):
        super().__init__(x, y, width, height)
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager
        self.current_animation = enemy_type
        
        # Basic AI properties
        self.aggro_range = 200
        self.attack_range = 80
        self.speed = 2
        self.attack_cooldown = 0
        self.damage = 20
        self.souls_value = 10
        
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
    
    def update(self, dt: int, player: LightweightPlayer, platforms: List[pygame.Rect]):
        """Simple AI without heavy processing"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Calculate distance to player
        player_distance = abs(self.x - player.x)
        
        # Simple AI behavior
        if player_distance < self.aggro_range:
            # Move towards player
            if player.x < self.x:
                self.vel_x = -self.speed
                self.facing = Direction.LEFT
            elif player.x > self.x:
                self.vel_x = self.speed
                self.facing = Direction.RIGHT
            
            # Simple attack
            if player_distance < self.attack_range and self.attack_cooldown <= 0:
                self.attack_cooldown = 2000  # 2 second cooldown
        else:
            self.vel_x = 0
        
        # Apply physics
        if self.special_ability != 'floating':
            self.apply_gravity()
        
        self.update_position()
        
        # Simple collision
        if self.special_ability != 'floating':
            self.handle_platform_collision(platforms)
        
        # Update animation
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Simple enemy collision"""
        enemy_rect = self.get_rect()
        self.on_ground = False
        
        for platform in platforms:
            if enemy_rect.colliderect(platform):
                if self.vel_y > 0 and enemy_rect.bottom <= platform.top + 10:
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0):
        """Simple enemy drawing"""
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            if self.facing == Direction.LEFT:
                frame = pygame.transform.flip(frame, True, False)
            
            draw_x = self.x - camera_x
            screen.blit(frame, (draw_x, self.y))

class SimpleUI:
    """Simple UI without heavy animations"""
    
    def __init__(self, screen_width: int, screen_height: int, asset_manager: LightweightAssetManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.asset_manager = asset_manager
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)
    
    def update(self, dt: float):
        """Simple update"""
        pass
    
    def draw_simple_hud(self, screen: pygame.Surface, player: LightweightPlayer, fps: float, level_name: str):
        """Draw simple HUD"""
        
        # Simple health bar
        health_ratio = player.health / player.max_health
        bar_width = 200
        bar_height = 20
        bar_x = 30
        bar_y = 30
        
        # Background
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        fill_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text
        health_text = self.small_font.render("Health", True, (255, 255, 255))
        screen.blit(health_text, (bar_x + bar_width + 10, bar_y))
        
        # Character info
        char_name = player.character_id.replace('_', ' ').title()
        info_texts = [
            f"Character: {char_name}",
            f"Level: {player.level}",
            f"Souls: {player.souls}"
        ]
        
        for i, text in enumerate(info_texts):
            text_surface = self.small_font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (30, 70 + i * 25))
        
        # Level indicator
        level_text = self.font.render(f"Level: {level_name}", True, (255, 255, 255))
        screen.blit(level_text, (30, 200))
        
        # FPS counter
        fps_color = (0, 255, 0) if fps >= 55 else (255, 255, 0) if fps >= 45 else (255, 0, 0)
        fps_text = self.small_font.render(f"FPS: {fps:.1f}", True, fps_color)
        screen.blit(fps_text, (self.screen_width - 150, 30))

class LightweightReserkaGothic:
    """Lightweight version without heavy graphics processing"""
    
    def __init__(self):
        # Initialize Pygame with basic settings
        pygame.init()
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)  # Lower quality for performance
        
        # Create display with basic flags
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Reserka Gothic - Lightweight Edition")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Initialize lightweight systems
        assets_path = Path(__file__).parent.parent / "assets"
        self.asset_manager = LightweightAssetManager(assets_path)
        
        self.menu_system = MenuSystem(self.screen, self.asset_manager.enhanced_manager)
        self.level_manager = EnhancedLevelManager(SCREEN_WIDTH, SCREEN_HEIGHT, self.asset_manager.enhanced_manager)
        
        # Character selection
        self.character_selection = CharacterSelection(self.screen, assets_path)
        self.selected_character = None
        
        # Game objects
        self.player = None
        self.enemies = []
        self.ui = SimpleUI(SCREEN_WIDTH, SCREEN_HEIGHT, self.asset_manager)
        
        # Metroidvania camera system
        self.camera = MetroidvaniaCamera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Metroidvania progression system
        self.progression = MetroidvaniaProgression()
        
        # Game state
        self.keys = {}
        self.transition_timer = 0
        self.transition_target = None
        
        # Performance monitoring
        self.frame_times = []
        
        # Settings
        self.settings = self.menu_system.get_settings()
        
        print("🎮✨ Lightweight Reserka Gothic initialized!")
        print("🚀 Optimized for performance - no heavy graphics processing!")
    
    def create_simple_enemies_for_level(self):
        """Create simple enemies"""
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
                enemy = LightweightEnemy(x, y, width, height, enemy_type, self.asset_manager)
                self.enemies.append(enemy)
    
    def handle_events(self):
        """Simple event handling"""
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
                        self.start_lightweight_game(self.selected_character)
                    elif result['action'] == 'back':
                        self.state = GameState.MENU
    
    def start_lightweight_game(self, character_id: str):
        """Start the lightweight game experience"""
        print(f"🚀 Starting lightweight game with {character_id}")
        
        # Load character animations
        self.asset_manager.load_character_animations(character_id)
        
        # Create lightweight player
        self.player = LightweightPlayer(100, 600, character_id, self.asset_manager)
        
        # Create simple enemies
        self.create_simple_enemies_for_level()
        
        # Switch to playing state
        self.state = GameState.PLAYING
    
    def transition_to_level(self, door):
        """Simple level transition"""
        print(f"🌟 Transition to {door.target_level}")
        
        if self.level_manager.switch_level(door.target_level):
            # Simple player positioning
            self.player.x = door.target_x
            self.player.y = door.target_y
            self.player.vel_x = 0
            self.player.vel_y = 0
            
            # Simple enemies for new level
            self.create_simple_enemies_for_level()
            
            # Simple transition effect
            self.state = GameState.LEVEL_TRANSITION
            self.transition_timer = 500  # Shorter transition
            self.transition_target = door.target_level
    
    def get_level_constraints(self) -> CameraConstraints:
        """Get camera constraints based on current level"""
        current_level = self.level_manager.current_level
        
        # Define constraints for each level
        level_constraints = {
            "level_1": CameraConstraints(0, 2560, 0, 720),  # 2x screen width
            "level_2": CameraConstraints(0, 3840, 0, 720),  # 3x screen width
            "level_3": CameraConstraints(0, 2560, 0, 1440), # 2x screen width, 2x height
            "gothic_castle": CameraConstraints(0, 3840, 0, 1440),
            "gothic_town": CameraConstraints(0, 2560, 0, 720),
            "night_town": CameraConstraints(0, 1920, 0, 720)
        }
        
        return level_constraints.get(current_level, CameraConstraints())
    
    def update(self):
        """Simple game update"""
        dt = self.clock.get_time()
        
        # Update frame timing
        self.frame_times.append(dt)
        if len(self.frame_times) > 30:  # Smaller buffer
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
            # Simple player update
            self.player.handle_input(self.keys, dt)
            platforms = self.level_manager.get_collision_rects()
            self.player.update(dt, platforms)
            
            # Update Metroidvania camera
            player_pos = (self.player.x + self.player.width // 2, self.player.y + self.player.height // 2)
            player_vel = (self.player.vel_x, self.player.vel_y)
            self.camera.update(dt, player_pos, player_vel)
            
            # Set camera constraints based on level
            level_constraints = self.get_level_constraints()
            self.camera.set_constraints(level_constraints)
            
            # Simple enemy updates
            for enemy in self.enemies[:]:
                # Cull distant enemies for performance
                if abs(enemy.x - self.player.x) < 800:
                    enemy.update(dt, self.player, platforms)
                
                # Simple combat
                if self.player.attacking:
                    attack_rect = self.player.get_attack_rect()
                    if attack_rect.colliderect(enemy.get_rect()):
                        damage = self.player.abilities['attack_damage']
                        if enemy.take_damage(damage):
                            # Enemy defeated
                            self.player.souls += enemy.souls_value
                            self.player.experience += 10
                            self.enemies.remove(enemy)
                            self.asset_manager.play_sound('attack', 0.5)
                
                # Simple enemy damage
                if (enemy.get_rect().colliderect(self.player.get_rect()) 
                    and self.player.invulnerable_timer <= 0):
                    self.player.take_damage(enemy.damage)
                    self.player.invulnerable_timer = 1500
                    
                    if self.player.health <= 0:
                        self.state = GameState.GAME_OVER
            
            # Simple level up system
            if self.player.experience >= self.player.level * 100:
                self.player.level += 1
                self.player.experience = 0
                self.player.max_health += 10
                self.player.health = self.player.max_health
        
        elif self.state == GameState.PAUSED:
            self.menu_system.update(dt)
    
    def draw(self):
        """Simple rendering without heavy effects"""
        # Clear screen
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.menu_system.draw()
            
        elif self.state == GameState.CHARACTER_SELECT:
            self.character_selection.draw()
            
        elif self.state in [GameState.PLAYING, GameState.LEVEL_TRANSITION] and self.player:
            # Get camera position
            camera_x, camera_y = self.camera.get_render_position()
            
            # Simple background
            bg = self.asset_manager.get_environment_background(self.level_manager.current_level)
            if bg:
                # Parallax scrolling with camera
                bg_x = -(camera_x * 0.3) % bg.get_width()
                self.screen.blit(bg, (bg_x, 0))
                if bg_x > 0:
                    self.screen.blit(bg, (bg_x - bg.get_width(), 0))
            
            # Level rendering with camera
            self.level_manager.draw_level(self.screen, camera_x, camera_y)
            
            # Enemy rendering with camera
            for enemy in self.enemies:
                if self.camera.is_on_screen((enemy.x, enemy.y), (enemy.width, enemy.height)):
                    enemy.draw(self.screen, camera_x)
            
            # Player rendering with camera
            self.player.draw(self.screen, camera_x)
            
            # Simple UI
            fps = 1000.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0
            self.ui.draw_simple_hud(self.screen, self.player, fps, self.level_manager.current_level)
            
            # Simple transition effects
            if self.state == GameState.LEVEL_TRANSITION:
                alpha = int(255 * (1 - self.transition_timer / 500.0))
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, alpha//3))
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
            # Simple game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((139, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.ui.large_font.render("GAME OVER", True, (255, 255, 255))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
            
            # Continue prompt
            continue_text = self.ui.font.render("Press ESCAPE to return to menu", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(continue_text, continue_rect)
        
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
        """Simple game loop optimized for performance"""
        print("🚀✨ Starting Lightweight Reserka Gothic Experience!")
        print("🎮 Optimized for performance - reduced graphics processing!")
        print("🎮 Press keys to interact: WASD/Arrows=Move, SPACE=Jump, X=Attack, Z=Dash, E=Door, ESC=Pause")
        
        while self.running:
            # Target 60 FPS
            self.clock.tick(TARGET_FPS)
            
            try:
                self.handle_events()
                self.update()
                self.draw()
            except Exception as e:
                print(f"❌ Game error: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
        
        print("👋 Thanks for playing Lightweight Reserka Gothic!")
        pygame.quit()
        sys.exit()

def main():
    """Launch the lightweight Reserka Gothic experience"""
    try:
        game = LightweightReserkaGothic()
        game.run()
    except Exception as e:
        print(f"❌ Error starting Lightweight Reserka Gothic: {e}")
        print("🔧 Please check that all assets are properly installed")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
