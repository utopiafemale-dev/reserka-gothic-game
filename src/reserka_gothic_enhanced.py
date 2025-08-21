#!/usr/bin/env python3
"""
Reserka - Gothic Edition Enhanced
Fixed frame rate, enhanced terrain, and door system for level progression
"""

import pygame
import sys
import os
import json
import random
import math
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

# Import enhanced systems
from character_asset_manager import CharacterAssetManager
from character_selection import CharacterSelection
from enhanced_level_system import EnhancedLevelManager, PerformanceOptimizer, Door

# Initialize Pygame with optimizations
pygame.init()
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)

# Game Configuration - Optimized for 60fps
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
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
        
        self.frame_timer += dt
        if self.frame_timer >= self.frames[self.current_frame].duration:
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

class AssetManager:
    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.character_manager = CharacterAssetManager(assets_path)
        self.animations = {}
        self.optimized_surfaces = {}
        
    def load_character_animations(self, character_id: str):
        """Load animations for a specific character with optimization"""
        print(f"🎨 Loading optimized animations for {character_id}")
        self.animations.clear()
        self.optimized_surfaces.clear()
        
        # Get character animations from asset manager
        character_animations = self.character_manager.get_character_animations(character_id)
        
        # Convert to Animation objects with optimized surfaces
        frame_durations = {
            'idle': 250,
            'walk': 150,
            'run': 150,
            'dash': 100,
            'jump': 100,
            'attack': 100,
            'death': 200
        }
        
        for anim_name, frames in character_animations.items():
            if frames:
                duration = frame_durations.get(anim_name, 200)
                is_looping = anim_name not in ['jump', 'attack', 'death', 'dash']
                
                # Optimize surfaces for better performance
                optimized_frames = []
                for frame in frames:
                    optimized_frame = frame.convert_alpha() if frame.get_alpha() else frame.convert()
                    optimized_frames.append(optimized_frame)
                
                self.animations[f'{character_id}_{anim_name}'] = Animation([
                    AnimationFrame(frame, duration) for frame in optimized_frames
                ], loop=is_looping)
                
                print(f"  ✓ Optimized {character_id}_{anim_name}: {len(frames)} frames")
        
        # Load enemy animations
        self.load_enemy_animations()
        
        # Load environment assets
        self.load_environment_assets()
    
    def load_enemy_animations(self):
        """Load enemy sprites and animations with optimization"""
        enemy_animations = {
            'fire_skull': 200,
            'demon_idle': 300,
            'demon_attack': 150,
            'hell_hound_idle': 250,
            'hell_hound_run': 200
        }
        
        for anim_key, frame_duration in enemy_animations.items():
            frames = self.character_manager.get_sprite_frames(anim_key)
            if frames:
                is_attack = 'attack' in anim_key
                
                # Optimize enemy frames
                optimized_frames = []
                for frame in frames:
                    optimized_frame = frame.convert_alpha() if frame.get_alpha() else frame.convert()
                    optimized_frames.append(optimized_frame)
                
                self.animations[anim_key] = Animation([
                    AnimationFrame(frame, frame_duration) for frame in optimized_frames
                ], loop=not is_attack)
        
        # Map hell_hound animations
        if 'hell_hound_idle' in self.animations:
            self.animations['hell_hound'] = self.animations['hell_hound_idle']
    
    def load_environment_assets(self):
        """Load background and environment assets with optimization"""
        self.images = {}
        
        bg_assets = ['castle_background', 'castle_tileset', 'horror_town', 'horror_clouds', 'horror_tiles']
        
        for asset_key in bg_assets:
            processed_bg = self.character_manager.get_image(asset_key)
            if processed_bg:
                # Optimize background images
                optimized_bg = processed_bg.convert_alpha() if processed_bg.get_alpha() else processed_bg.convert()
                self.images[asset_key] = optimized_bg
        
        # Map to expected keys
        if 'castle_background' in self.images:
            self.images['castle_bg'] = self.images['castle_background']
        else:
            # Create optimized placeholder
            placeholder = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            placeholder.fill(DARK_BLUE)
            self.images['castle_bg'] = placeholder.convert()

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

class Player(Entity):
    def __init__(self, x: int, y: int, character_id: str, asset_manager: AssetManager):
        super().__init__(x, y, 64, 80)
        self.character_id = character_id
        self.asset_manager = asset_manager
        self.current_animation = f'{character_id}_idle'
        self.attacking = False
        self.dashing = False
        self.attack_cooldown = 0
        self.dash_cooldown = 0
        self.jump_count = 0
        self.max_jumps = 2
        self.invulnerable_timer = 0
        
        # Character-specific properties
        self.setup_character_properties()
        
        # Player stats
        self.experience = 0
        self.level = 1
        self.souls = 0
        self.keys = []  # For door unlocking
        
        # Camera smoothing
        self.camera_target_x = x
        self.camera_smooth_factor = 0.1
    
    def setup_character_properties(self):
        """Setup character-specific properties"""
        if self.character_id == 'female_adventurer':
            self.max_jumps = 3  # Triple jump
            self.dash_distance = 150
            self.dash_duration = 300
        elif self.character_id == 'gothicvania_hero':
            self.max_jumps = 2
            self.dash_distance = 0
            self.dash_duration = 0
    
    def handle_input(self, keys: Dict[int, bool], dt: int):
        """Handle player input with performance optimizations"""
        # Reset horizontal velocity
        self.vel_x = 0
        
        # Movement with caching to avoid repeated animation changes
        moving = False
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            self.vel_x = -PLAYER_SPEED
            self.facing = Direction.LEFT
            moving = True
        elif keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            self.vel_x = PLAYER_SPEED
            self.facing = Direction.RIGHT
            moving = True
        
        # Only change animation if state changed
        if self.on_ground and not self.attacking and not self.dashing:
            if moving:
                target_anim = f'{self.character_id}_walk' if self.character_id == 'female_adventurer' else f'{self.character_id}_run'
                if self.current_animation != target_anim:
                    self.current_animation = target_anim
            else:
                target_anim = f'{self.character_id}_idle'
                if self.current_animation != target_anim:
                    self.current_animation = target_anim
        
        # Jumping
        if (keys.get(pygame.K_SPACE) or keys.get(pygame.K_w)) and self.jump_count < self.max_jumps:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jump_count += 1
            if not self.attacking and not self.dashing:
                self.current_animation = f'{self.character_id}_jump'
        
        # Attack
        if (keys.get(pygame.K_x) or keys.get(pygame.K_j)) and self.attack_cooldown <= 0:
            self.attacking = True
            self.current_animation = f'{self.character_id}_attack'
            self.attack_cooldown = 500
            anim_key = f'{self.character_id}_attack'
            if anim_key in self.asset_manager.animations:
                self.asset_manager.animations[anim_key].reset()
        
        # Dash (Female Adventurer only)
        if (keys.get(pygame.K_z) or keys.get(pygame.K_k)) and self.character_id == 'female_adventurer' and self.dash_cooldown <= 0:
            self.start_dash()
    
    def start_dash(self):
        """Start dash ability for Female Adventurer"""
        if self.dash_distance > 0:
            self.dashing = True
            self.dash_cooldown = 1000
            self.current_animation = f'{self.character_id}_dash'
            
            # Set dash velocity
            dash_speed = self.dash_distance / (self.dash_duration / 1000.0)
            if self.facing == Direction.LEFT:
                self.vel_x = -dash_speed
            else:
                self.vel_x = dash_speed
            
            self.dash_timer = self.dash_duration
            
            if f'{self.character_id}_dash' in self.asset_manager.animations:
                self.asset_manager.animations[f'{self.character_id}_dash'].reset()
    
    def update(self, dt: int, platforms: List[pygame.Rect]):
        """Update player state with optimizations"""
        # Update timers
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        
        # Handle dash
        if self.dashing:
            if hasattr(self, 'dash_timer'):
                self.dash_timer -= dt
                if self.dash_timer <= 0:
                    self.dashing = False
                    self.vel_x = 0
                    delattr(self, 'dash_timer')
        
        # Check animation completion
        attack_anim = f'{self.character_id}_attack'
        if self.attacking and attack_anim in self.asset_manager.animations:
            if self.asset_manager.animations[attack_anim].finished:
                self.attacking = False
                self.current_animation = f'{self.character_id}_idle'
        
        # Apply physics
        if not self.dashing:
            self.apply_gravity()
        self.update_position()
        
        # Platform collision
        self.handle_platform_collision(platforms)
        
        # Keep player on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH * 2 - self.width))  # Allow wider world
        
        # Update camera target
        self.camera_target_x = self.x - SCREEN_WIDTH // 2
        
        # Update animation only if it exists
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Handle collision with platforms"""
        player_rect = self.get_rect()
        self.on_ground = False
        
        for platform in platforms:
            if player_rect.colliderect(platform):
                # Landing on top
                if self.vel_y > 0 and player_rect.bottom <= platform.top + 10:
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                # Hitting from below
                elif self.vel_y < 0 and player_rect.top >= platform.bottom - 10:
                    self.y = platform.bottom
                    self.vel_y = 0
    
    def get_attack_rect(self) -> pygame.Rect:
        """Get attack hitbox"""
        if not self.attacking:
            return pygame.Rect(0, 0, 0, 0)
        
        if self.facing == Direction.RIGHT:
            return pygame.Rect(self.x + self.width, self.y, 40, self.height)
        else:
            return pygame.Rect(self.x - 40, self.y, 40, self.height)
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0):
        """Draw the player with camera offset"""
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            # Flip sprite based on facing direction
            if self.facing == Direction.LEFT:
                frame = pygame.transform.flip(frame, True, False)
            
            # Flash if invulnerable
            if self.invulnerable_timer > 0 and (self.invulnerable_timer // 100) % 2:
                return
            
            # Draw with camera offset
            draw_x = self.x - camera_x
            draw_y = self.y
            
            frame_rect = frame.get_rect()
            frame_rect.center = (draw_x + self.width // 2, draw_y + self.height // 2)
            screen.blit(frame, frame_rect)

class Enemy(Entity):
    def __init__(self, x: int, y: int, width: int, height: int, enemy_type: str, asset_manager: AssetManager):
        super().__init__(x, y, width, height)
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager
        self.current_animation = f'{enemy_type}_idle'
        self.attack_cooldown = 0
        self.aggro_range = 200
        self.attack_range = 80
        self.speed = 2
        self.damage = 20
        self.souls_value = 10
        
        # Enemy-specific stats
        if enemy_type == 'fire_skull':
            self.health = 50
            self.speed = 3
            self.damage = 15
        elif enemy_type == 'demon':
            self.health = 100
            self.speed = 1.5
            self.damage = 30
            self.souls_value = 25
        elif enemy_type == 'hell_hound':
            self.health = 75
            self.speed = 4
            self.damage = 25
            self.souls_value = 15
    
    def update(self, dt: int, player: Player, platforms: List[pygame.Rect]):
        """Update enemy AI with performance optimizations"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Optimize AI calculations
        player_distance = abs(self.x - player.x)
        
        if player_distance < self.aggro_range:
            if player.x < self.x:
                self.vel_x = -self.speed
                self.facing = Direction.LEFT
            elif player.x > self.x:
                self.vel_x = self.speed
                self.facing = Direction.RIGHT
        else:
            self.vel_x = 0
        
        self.apply_gravity()
        self.update_position()
        
        # Simplified platform collision
        self.handle_platform_collision(platforms)
        
        # Update animation
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Handle enemy platform collision"""
        enemy_rect = self.get_rect()
        self.on_ground = False
        
        for platform in platforms:
            if enemy_rect.colliderect(platform):
                if self.vel_y > 0 and enemy_rect.bottom <= platform.top + 10:
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0):
        """Draw enemy with camera offset"""
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            if self.facing == Direction.LEFT:
                frame = pygame.transform.flip(frame, True, False)
            
            draw_x = self.x - camera_x
            screen.blit(frame, (draw_x, self.y))

class UI:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)
    
    def draw_hud(self, screen: pygame.Surface, player: Player, performance: PerformanceOptimizer, level_name: str):
        """Draw optimized HUD"""
        # Health bar
        health_ratio = player.health / player.max_health
        health_bg = pygame.Rect(20, 20, 200, 20)
        health_fg = pygame.Rect(20, 20, int(200 * health_ratio), 20)
        
        pygame.draw.rect(screen, DARK_RED, health_bg)
        pygame.draw.rect(screen, (0, 255, 0), health_fg)
        
        # Text elements
        health_text = self.small_font.render(f"HP: {player.health}/{player.max_health}", True, WHITE)
        screen.blit(health_text, (25, 45))
        
        char_name = player.character_id.replace('_', ' ').title()
        char_text = self.small_font.render(f"Character: {char_name}", True, WHITE)
        screen.blit(char_text, (20, 70))
        
        souls_text = self.small_font.render(f"Souls: {player.souls}", True, GOLD)
        screen.blit(souls_text, (20, 95))
        
        level_text = self.small_font.render(f"Level: {level_name}", True, WHITE)
        screen.blit(level_text, (20, 120))
        
        # Performance info
        fps = performance.get_average_fps()
        fps_color = (0, 255, 0) if fps >= 55 else (255, 255, 0) if fps >= 45 else (255, 0, 0)
        fps_text = self.small_font.render(f"FPS: {fps:.1f}", True, fps_color)
        screen.blit(fps_text, (self.screen_width - 150, 20))
        
        # Ability cooldowns
        if player.character_id == 'female_adventurer':
            dash_ready = player.dash_cooldown <= 0
            dash_color = WHITE if dash_ready else (100, 100, 100)
            dash_text = self.small_font.render("Z: Dash", True, dash_color)
            screen.blit(dash_text, (20, 145))

class Game:
    def __init__(self):
        # Initialize display with optimization flags
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                             pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Reserka - Gothic Edition Enhanced")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.CHARACTER_SELECT
        
        # Enhanced systems
        assets_path = Path(__file__).parent.parent / "assets"
        self.asset_manager = AssetManager(assets_path)
        self.level_manager = EnhancedLevelManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.performance = PerformanceOptimizer()
        
        # Character selection
        self.character_selection = CharacterSelection(self.screen, assets_path)
        self.selected_character = None
        
        # Game objects
        self.player = None
        self.enemies = []
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Camera system
        self.camera_x = 0
        self.camera_smooth = 0.1
        
        # Game state
        self.keys = {}
        self.transition_timer = 0
        self.transition_target = None
        
        print("🎮 Enhanced Reserka Gothic initialized")
    
    def create_enemies_for_level(self):
        """Create enemies based on current level"""
        self.enemies.clear()
        current_level = self.level_manager.current_level
        
        if current_level == "level_1":
            self.enemies = [
                Enemy(400, 460, 48, 48, 'fire_skull', self.asset_manager),
                Enemy(800, 260, 64, 64, 'hell_hound', self.asset_manager),
            ]
        elif current_level == "level_2":
            self.enemies = [
                Enemy(300, 360, 48, 48, 'fire_skull', self.asset_manager),
                Enemy(600, 180, 80, 80, 'demon', self.asset_manager),
                Enemy(1000, 220, 64, 64, 'hell_hound', self.asset_manager),
            ]
    
    def handle_events(self):
        """Handle pygame events with optimization"""
        dt = self.clock.get_time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys[event.key] = True
                
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                
                # Door interaction
                elif event.key == pygame.K_e and self.state == GameState.PLAYING and self.player:
                    door = self.level_manager.check_door_collision(self.player.get_rect())
                    if door:
                        self.transition_to_level(door)
                
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False
            
            # Character selection events
            elif self.state == GameState.CHARACTER_SELECT:
                result = self.character_selection.handle_event(event)
                if result:
                    if result['action'] == 'select':
                        self.selected_character = result['character_id']
                        self.start_game_with_character(self.selected_character)
                    elif result['action'] == 'back':
                        self.running = False
    
    def transition_to_level(self, door: Door):
        """Handle level transition"""
        print(f"🚪 Transitioning to {door.target_level}")
        
        if self.level_manager.switch_level(door.target_level):
            # Move player to door target position
            self.player.x = door.target_x
            self.player.y = door.target_y
            
            # Reset player state
            self.player.vel_x = 0
            self.player.vel_y = 0
            self.player.on_ground = False
            
            # Create enemies for new level
            self.create_enemies_for_level()
            
            # Start transition effect
            self.state = GameState.LEVEL_TRANSITION
            self.transition_timer = 1000  # 1 second
            self.transition_target = door.target_level
    
    def start_game_with_character(self, character_id: str):
        """Start game with selected character"""
        print(f"🎭 Starting enhanced game with character: {character_id}")
        
        # Load character animations with optimization
        self.asset_manager.load_character_animations(character_id)
        
        # Create player
        self.player = Player(100, 600, character_id, self.asset_manager)
        
        # Create enemies for initial level
        self.create_enemies_for_level()
        
        # Switch to playing state
        self.state = GameState.PLAYING
    
    def update(self):
        """Update game state with performance optimizations"""
        dt = self.clock.get_time()
        self.performance.update_frame_time(dt)
        
        if self.state == GameState.CHARACTER_SELECT:
            self.character_selection.update(dt / 1000.0)
        
        elif self.state == GameState.LEVEL_TRANSITION:
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.state = GameState.PLAYING
        
        elif self.state == GameState.PLAYING and self.player:
            # Skip frame if performance is poor
            if self.performance.should_skip_frame():
                return
            
            # Update player
            self.player.handle_input(self.keys, dt)
            platforms = self.level_manager.get_collision_rects()
            self.player.update(dt, platforms)
            
            # Update camera smoothly
            target_camera_x = self.player.camera_target_x
            self.camera_x += (target_camera_x - self.camera_x) * self.camera_smooth
            self.camera_x = max(0, min(self.camera_x, SCREEN_WIDTH))  # Clamp camera
            
            # Update enemies with culling for performance
            for enemy in self.enemies[:]:
                # Only update enemies within reasonable distance
                if abs(enemy.x - self.player.x) < 800:
                    enemy.update(dt, self.player, platforms)
                
                # Combat
                if self.player.attacking:
                    attack_rect = self.player.get_attack_rect()
                    if attack_rect.colliderect(enemy.get_rect()):
                        if enemy.take_damage(50):
                            self.player.souls += enemy.souls_value
                            self.enemies.remove(enemy)
                
                # Enemy damage to player
                if enemy.get_rect().colliderect(self.player.get_rect()):
                    if self.player.invulnerable_timer <= 0:
                        self.player.take_damage(enemy.damage)
                        self.player.invulnerable_timer = 1000
                        
                        if self.player.health <= 0:
                            self.state = GameState.GAME_OVER
    
    def draw(self):
        """Draw everything with optimizations"""
        self.screen.fill(BLACK)
        
        if self.state == GameState.CHARACTER_SELECT:
            self.character_selection.draw()
        
        elif self.state in [GameState.PLAYING, GameState.LEVEL_TRANSITION] and self.player:
            # Draw background
            if 'castle_bg' in self.asset_manager.images:
                # Parallax background
                bg_x = -(self.camera_x * 0.5) % SCREEN_WIDTH
                bg = self.asset_manager.images['castle_bg']
                self.screen.blit(bg, (bg_x, 0))
                if bg_x > 0:
                    self.screen.blit(bg, (bg_x - SCREEN_WIDTH, 0))
            
            # Draw level terrain
            self.level_manager.draw_level(self.screen, int(self.camera_x), 0)
            
            # Draw enemies (with culling)
            for enemy in self.enemies:
                if -100 <= enemy.x - self.camera_x <= SCREEN_WIDTH + 100:
                    enemy.draw(self.screen, int(self.camera_x))
            
            # Draw player
            self.player.draw(self.screen, int(self.camera_x))
            
            # Draw UI
            self.ui.draw_hud(self.screen, self.player, self.performance, 
                           self.level_manager.current_level)
            
            # Transition effect
            if self.state == GameState.LEVEL_TRANSITION:
                alpha = int(255 * (1 - self.transition_timer / 1000.0))
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(alpha)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                if self.transition_target:
                    transition_text = self.ui.large_font.render(f"Entering {self.transition_target}", True, WHITE)
                    text_rect = transition_text.get_rect()
                    text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    self.screen.blit(transition_text, text_rect)
        
        elif self.state == GameState.PAUSED:
            # Draw pause overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.ui.large_font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect()
            text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.screen.blit(pause_text, text_rect)
        
        elif self.state == GameState.GAME_OVER:
            self.screen.fill(DARK_RED)
            game_over_text = self.ui.large_font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect()
            text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Optimized main game loop"""
        print("🚀 Starting enhanced game loop with 60fps target")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    """Main function"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running enhanced game: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()

if __name__ == "__main__":
    main()
