#!/usr/bin/env python3
"""
Reserka - Gothic Edition with Character Selection
A dark fantasy action-platformer game with multiple playable characters
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

# Import character systems
from character_asset_manager import CharacterAssetManager
from character_selection import CharacterSelection

# Initialize Pygame
pygame.init()

# Game Configuration
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
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
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
        return self.frames[self.current_frame].surface
    
    def reset(self):
        self.current_frame = 0
        self.frame_timer = 0
        self.finished = False

class AssetManager:
    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.character_manager = CharacterAssetManager(assets_path)
        self.animations = {}
        
    def load_character_animations(self, character_id: str):
        """Load animations for a specific character"""
        self.animations.clear()
        
        # Get character animations from asset manager
        character_animations = self.character_manager.get_character_animations(character_id)
        
        # Convert to Animation objects
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
                
                self.animations[f'{character_id}_{anim_name}'] = Animation([
                    AnimationFrame(frame, duration) for frame in frames
                ], loop=is_looping)
                
                print(f"  ✓ Loaded {character_id}_{anim_name}: {len(frames)} frames")
        
        # Load enemy animations (unchanged)
        self.load_enemy_animations()
        
        # Load environment assets
        self.load_environment_assets()
    
    def load_enemy_animations(self):
        """Load enemy sprites and animations"""
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
                self.animations[anim_key] = Animation([
                    AnimationFrame(frame, frame_duration) for frame in frames
                ], loop=not is_attack)
                print(f"  ✓ Loaded {anim_key}: {len(frames)} frames")
        
        # Map hell_hound animations to expected names
        if 'hell_hound_idle' in self.animations:
            self.animations['hell_hound'] = self.animations['hell_hound_idle']
    
    def load_environment_assets(self):
        """Load background and environment assets"""
        self.images = {}
        
        bg_assets = ['castle_background', 'castle_tileset', 'horror_town', 'horror_clouds', 'horror_tiles']
        
        for asset_key in bg_assets:
            processed_bg = self.character_manager.get_image(asset_key)
            if processed_bg:
                self.images[asset_key] = processed_bg
                print(f"  ✓ Loaded {asset_key}: {processed_bg.get_width()}x{processed_bg.get_height()}")
        
        # Map to expected keys for backward compatibility
        if 'castle_background' in self.images:
            self.images['castle_bg'] = self.images['castle_background']
        else:
            # Create placeholder if not found
            self.images['castle_bg'] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.images['castle_bg'].fill(DARK_BLUE)

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
        self.max_jumps = 2  # Double jump
        self.invulnerable_timer = 0
        
        # Character-specific properties
        self.setup_character_properties()
        
        # Player stats
        self.experience = 0
        self.level = 1
        self.souls = 0
    
    def setup_character_properties(self):
        """Setup character-specific properties"""
        if self.character_id == 'female_adventurer':
            self.max_jumps = 3  # Triple jump for adventurer
            self.dash_distance = 150
            self.dash_duration = 300  # ms
        elif self.character_id == 'gothicvania_hero':
            self.max_jumps = 2
            self.dash_distance = 0  # No dash ability
            self.dash_duration = 0
    
    def handle_input(self, keys: Dict[int, bool], dt: int):
        """Handle player input with character-specific abilities"""
        # Reset horizontal velocity
        self.vel_x = 0
        
        # Movement
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            self.vel_x = -PLAYER_SPEED
            self.facing = Direction.LEFT
            if self.on_ground and not self.attacking and not self.dashing:
                if self.character_id == 'female_adventurer':
                    self.current_animation = f'{self.character_id}_walk'
                else:
                    self.current_animation = f'{self.character_id}_run'
        elif keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            self.vel_x = PLAYER_SPEED
            self.facing = Direction.RIGHT
            if self.on_ground and not self.attacking and not self.dashing:
                if self.character_id == 'female_adventurer':
                    self.current_animation = f'{self.character_id}_walk'
                else:
                    self.current_animation = f'{self.character_id}_run'
        else:
            if self.on_ground and not self.attacking and not self.dashing:
                self.current_animation = f'{self.character_id}_idle'
        
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
            self.dash_cooldown = 1000  # 1 second cooldown
            self.current_animation = f'{self.character_id}_dash'
            
            # Set dash velocity
            dash_speed = self.dash_distance / (self.dash_duration / 1000.0)
            if self.facing == Direction.LEFT:
                self.vel_x = -dash_speed
            else:
                self.vel_x = dash_speed
            
            # Start dash timer
            self.dash_timer = self.dash_duration
            
            if f'{self.character_id}_dash' in self.asset_manager.animations:
                self.asset_manager.animations[f'{self.character_id}_dash'].reset()
    
    def update(self, dt: int, platforms: List[pygame.Rect]):
        """Update player state"""
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
        
        # Check if attack animation finished
        attack_anim = f'{self.character_id}_attack'
        if self.attacking and attack_anim in self.asset_manager.animations:
            if self.asset_manager.animations[attack_anim].finished:
                self.attacking = False
                self.current_animation = f'{self.character_id}_idle'
        
        # Check if dash animation finished
        dash_anim = f'{self.character_id}_dash'
        if self.dashing and dash_anim in self.asset_manager.animations:
            if self.asset_manager.animations[dash_anim].finished:
                self.dashing = False
        
        # Apply gravity and update position
        if not self.dashing:  # No gravity during dash
            self.apply_gravity()
        self.update_position()
        
        # Platform collision
        self.handle_platform_collision(platforms)
        
        # Keep player on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
        # Update animation
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Handle collision with platforms"""
        player_rect = self.get_rect()
        self.on_ground = False
        
        for platform in platforms:
            if player_rect.colliderect(platform):
                # Landing on top of platform
                if self.vel_y > 0 and player_rect.bottom <= platform.top + 10:
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                # Hitting platform from below
                elif self.vel_y < 0 and player_rect.top >= platform.bottom - 10:
                    self.y = platform.bottom
                    self.vel_y = 0
    
    def get_attack_rect(self) -> pygame.Rect:
        """Get the attack hitbox"""
        if not self.attacking:
            return pygame.Rect(0, 0, 0, 0)
        
        if self.facing == Direction.RIGHT:
            return pygame.Rect(self.x + self.width, self.y, 40, self.height)
        else:
            return pygame.Rect(self.x - 40, self.y, 40, self.height)
    
    def draw(self, screen: pygame.Surface):
        """Draw the player"""
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            # Flip sprite based on facing direction
            if self.facing == Direction.LEFT:
                frame = pygame.transform.flip(frame, True, False)
            
            # Flash if invulnerable
            if self.invulnerable_timer > 0 and (self.invulnerable_timer // 100) % 2:
                # Don't draw (flashing effect)
                pass
            else:
                # Center the sprite on the player position
                frame_rect = frame.get_rect()
                frame_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
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
        """Update enemy AI and state"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Simple AI: move towards player if in range
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
        
        # Apply gravity and update position
        self.apply_gravity()
        self.update_position()
        
        # Platform collision (simplified)
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
    
    def draw(self, screen: pygame.Surface):
        """Draw the enemy"""
        if self.current_animation in self.asset_manager.animations:
            animation = self.asset_manager.animations[self.current_animation]
            frame = animation.get_current_frame()
            
            # Flip sprite based on facing direction
            if self.facing == Direction.LEFT:
                frame = pygame.transform.flip(frame, True, False)
            
            screen.blit(frame, (self.x, self.y))

class UI:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)
    
    def draw_hud(self, screen: pygame.Surface, player: Player):
        """Draw the heads-up display"""
        # Health bar
        health_bar_width = 200
        health_bar_height = 20
        health_ratio = player.health / player.max_health
        
        # Background (red)
        health_bg = pygame.Rect(20, 20, health_bar_width, health_bar_height)
        pygame.draw.rect(screen, DARK_RED, health_bg)
        
        # Foreground (green)
        health_fg = pygame.Rect(20, 20, int(health_bar_width * health_ratio), health_bar_height)
        pygame.draw.rect(screen, (0, 255, 0), health_fg)
        
        # Health text
        health_text = self.small_font.render(f"HP: {player.health}/{player.max_health}", True, WHITE)
        screen.blit(health_text, (25, 45))
        
        # Character info
        char_name = player.character_id.replace('_', ' ').title()
        char_text = self.small_font.render(f"Character: {char_name}", True, WHITE)
        screen.blit(char_text, (20, 70))
        
        # Souls (currency)
        souls_text = self.small_font.render(f"Souls: {player.souls}", True, GOLD)
        screen.blit(souls_text, (20, 95))
        
        # Ability cooldowns
        if player.character_id == 'female_adventurer':
            dash_ready = player.dash_cooldown <= 0
            dash_color = WHITE if dash_ready else (100, 100, 100)
            dash_text = self.small_font.render("Z: Dash", True, dash_color)
            screen.blit(dash_text, (20, 120))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Reserka - Gothic Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.CHARACTER_SELECT
        
        # Assets
        assets_path = Path(__file__).parent.parent / "assets"
        self.asset_manager = AssetManager(assets_path)
        
        # Character selection
        self.character_selection = CharacterSelection(self.screen, assets_path)
        self.selected_character = None
        
        # Game objects (initialized after character selection)
        self.player = None
        self.enemies = []
        self.platforms = []
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Game state
        self.keys = {}
        
        # Create some platforms for testing
        self.create_level()
    
    def create_level(self):
        """Create a simple test level"""
        self.platforms = [
            pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Ground
            pygame.Rect(300, 500, 200, 20),  # Platform 1
            pygame.Rect(600, 400, 200, 20),  # Platform 2
            pygame.Rect(900, 300, 200, 20),  # Platform 3
        ]
    
    def create_enemies(self):
        """Create test enemies"""
        self.enemies = [
            Enemy(400, 460, 48, 48, 'fire_skull', self.asset_manager),
            Enemy(700, 360, 64, 64, 'hell_hound', self.asset_manager),
            Enemy(1000, 260, 80, 80, 'demon', self.asset_manager),
        ]
    
    def handle_events(self):
        """Handle pygame events"""
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
                
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False
            
            # Handle character selection events
            elif self.state == GameState.CHARACTER_SELECT:
                result = self.character_selection.handle_event(event)
                if result:
                    if result['action'] == 'select':
                        self.selected_character = result['character_id']
                        self.start_game_with_character(self.selected_character)
                    elif result['action'] == 'back':
                        self.running = False
    
    def start_game_with_character(self, character_id: str):
        """Start the game with the selected character"""
        print(f"Starting game with character: {character_id}")
        
        # Load character-specific animations
        self.asset_manager.load_character_animations(character_id)
        
        # Create player with selected character
        self.player = Player(100, 600, character_id, self.asset_manager)
        
        # Create enemies
        self.create_enemies()
        
        # Switch to playing state
        self.state = GameState.PLAYING
    
    def update(self):
        """Update game state"""
        dt = self.clock.get_time()
        
        if self.state == GameState.CHARACTER_SELECT:
            self.character_selection.update(dt / 1000.0)
        
        elif self.state == GameState.PLAYING and self.player:
            # Update player
            self.player.handle_input(self.keys, dt)
            self.player.update(dt, self.platforms)
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update(dt, self.player, self.platforms)
                
                # Check player attack vs enemy
                if self.player.attacking:
                    attack_rect = self.player.get_attack_rect()
                    if attack_rect.colliderect(enemy.get_rect()):
                        if enemy.take_damage(50):
                            self.player.souls += enemy.souls_value
                            self.enemies.remove(enemy)
                
                # Check enemy vs player collision
                if enemy.get_rect().colliderect(self.player.get_rect()):
                    if self.player.invulnerable_timer <= 0:
                        self.player.take_damage(enemy.damage)
                        self.player.invulnerable_timer = 1000  # 1 second invulnerability
                        
                        if self.player.health <= 0:
                            self.state = GameState.GAME_OVER
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        
        if self.state == GameState.CHARACTER_SELECT:
            self.character_selection.draw()
        
        elif self.state == GameState.PLAYING and self.player:
            # Draw background
            if 'castle_bg' in self.asset_manager.images:
                self.screen.blit(self.asset_manager.images['castle_bg'], (0, 0))
            
            # Draw platforms
            for platform in self.platforms:
                pygame.draw.rect(self.screen, (100, 100, 100), platform)
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Draw player
            self.player.draw(self.screen)
            
            # Draw UI
            self.ui.draw_hud(self.screen, self.player)
        
        elif self.state == GameState.PAUSED:
            # Draw paused overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.ui.large_font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect()
            text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.screen.blit(pause_text, text_rect)
        
        elif self.state == GameState.GAME_OVER:
            # Draw game over screen
            self.screen.fill(DARK_RED)
            game_over_text = self.ui.large_font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect()
            text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    """Main function"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
