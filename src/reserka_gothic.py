#!/usr/bin/env python3
"""
Reserka - Gothic Edition
A dark fantasy action-platformer game using Gothicvania assets
Inspired by classic Metroidvania games with a gothic horror theme
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

# Import existing asset managers
from enhanced_asset_manager import EnhancedAssetManager
from character_asset_manager import CharacterAssetManager

class AssetManager:
    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.images = {}
        self.animations = {}
        self.sounds = {}
        
        # Use existing asset managers
        self.enhanced_manager = EnhancedAssetManager(assets_path)
        self.character_manager = CharacterAssetManager(assets_path)
        self.load_assets()
    
    def load_image(self, path: str, scale: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """Load and optionally scale an image"""
        full_path = self.assets_path / path
        if full_path.exists():
            image = pygame.image.load(str(full_path)).convert_alpha()
            if scale:
                image = pygame.transform.scale(image, scale)
            return image
        else:
            # Create placeholder if image not found
            surface = pygame.Surface((64, 64))
            surface.fill(PURPLE)
            return surface
    
    def load_spritesheet(self, path: str, frame_width: int, frame_height: int, 
                        frame_count: int, scale: Optional[Tuple[int, int]] = None) -> List[pygame.Surface]:
        """Load a spritesheet and split it into frames"""
        spritesheet = self.load_image(path, None)
        frames = []
        
        for i in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(spritesheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            
            if scale:
                frame = pygame.transform.scale(frame, scale)
            frames.append(frame)
        
        return frames
    
    def load_assets(self):
        """Load all game assets using improved processing"""
        print("Loading Gothic assets with improved processing...")
        
        # Load hero animations from improved manager
        hero_animations = {
            'hero_idle': 250,  # Frame duration in ms
            'hero_run': 150,
            'hero_jump': 100,
            'hero_attack': 100
        }
        
        for anim_key, frame_duration in hero_animations.items():
            # Map to character manager naming
            char_key = anim_key.replace('hero_', 'gothicvania_hero_')
            frames = self.character_manager.get_sprite_frames(char_key)
            if frames:
                self.animations[anim_key] = Animation([
                    AnimationFrame(frame, frame_duration) for frame in frames
                ], loop=(anim_key not in ['hero_jump', 'hero_attack']))
                print(f"  ✓ Loaded {anim_key}: {len(frames)} frames")
        
        # Load enemy animations from improved manager
        self.load_enemy_animations()
        
        # Load background assets from improved manager
        self.load_environment_assets()
    
    def load_enemy_animations(self):
        """Load enemy sprites and animations using improved processing"""
        # Load enemy animations from improved manager
        enemy_animations = {
            'fire_skull': 200,  # Frame duration
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
        """Load background and tileset assets using enhanced processing"""
        # Load processed backgrounds from enhanced manager
        bg_assets = ['cave_bg_1', 'cave_bg_2', 'cave_bg_3', 'cave_bg_4a', 'cave_tileset', 'cave_props_1']
        
        for asset_key in bg_assets:
            processed_bg = self.enhanced_manager.get_environment(asset_key)
            if processed_bg:
                self.images[asset_key] = processed_bg
                print(f"  ✓ Loaded {asset_key}: {processed_bg.get_width()}x{processed_bg.get_height()}")
        
        # Map to expected keys for backward compatibility
        if 'cave_bg_1' in self.images:
            self.images['castle_bg'] = self.images['cave_bg_1']
        elif 'cave_bg_2' in self.images:
            self.images['castle_bg'] = self.images['cave_bg_2']
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
    def __init__(self, x: int, y: int, asset_manager: AssetManager):
        super().__init__(x, y, 64, 80)
        self.asset_manager = asset_manager
        self.current_animation = 'hero_idle'
        self.attacking = False
        self.attack_cooldown = 0
        self.jump_count = 0
        self.max_jumps = 2  # Double jump
        self.invulnerable_timer = 0
        
        # Player stats
        self.experience = 0
        self.level = 1
        self.souls = 0  # Currency in gothic theme
    
    def handle_input(self, keys: Dict[int, bool], dt: int):
        """Handle player input"""
        # Reset horizontal velocity
        self.vel_x = 0
        
        # Movement
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            self.vel_x = -PLAYER_SPEED
            self.facing = Direction.LEFT
            if self.on_ground and not self.attacking:
                self.current_animation = 'hero_run'
        elif keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            self.vel_x = PLAYER_SPEED
            self.facing = Direction.RIGHT
            if self.on_ground and not self.attacking:
                self.current_animation = 'hero_run'
        else:
            if self.on_ground and not self.attacking:
                self.current_animation = 'hero_idle'
        
        # Jumping
        if (keys.get(pygame.K_SPACE) or keys.get(pygame.K_w)) and self.jump_count < self.max_jumps:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jump_count += 1
            self.current_animation = 'hero_jump'
            if hasattr(self, 'jump_sound'):
                self.jump_sound.play()
        
        # Attack
        if (keys.get(pygame.K_x) or keys.get(pygame.K_j)) and self.attack_cooldown <= 0:
            self.attacking = True
            self.current_animation = 'hero_attack'
            self.attack_cooldown = 500
            self.asset_manager.animations['hero_attack'].reset()
    
    def update(self, dt: int, platforms: List[pygame.Rect]):
        """Update player state"""
        # Update timers
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        
        # Check if attack animation finished
        if self.attacking and self.asset_manager.animations['hero_attack'].finished:
            self.attacking = False
            self.current_animation = 'hero_idle'
        
        # Apply gravity and update position
        self.apply_gravity()
        self.update_position()
        
        # Platform collision
        self.handle_platform_collision(platforms)
        
        # Keep player on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
        # Update animation
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
            screen.blit(frame, (self.x - 16, self.y - 16))  # Offset for sprite centering
        
        # Draw attack hitbox in debug mode
        # attack_rect = self.get_attack_rect()
        # if attack_rect.width > 0:
        #     pygame.draw.rect(screen, RED, attack_rect, 2)

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
            
            # Attack if in range
            if player_distance < self.attack_range and self.attack_cooldown <= 0:
                self.current_animation = f'{self.enemy_type}_attack'
                self.attack_cooldown = 2000
                # Damage player if they're close
                if player.invulnerable_timer <= 0:
                    player.take_damage(self.damage)
                    player.invulnerable_timer = 1000
        else:
            self.vel_x = 0
            self.current_animation = f'{self.enemy_type}_idle'
        
        # Apply gravity and update position
        self.apply_gravity()
        self.update_position()
        
        # Platform collision
        self.handle_platform_collision(platforms)
        
        # Update animation
        if self.current_animation in self.asset_manager.animations:
            self.asset_manager.animations[self.current_animation].update(dt)
    
    def handle_platform_collision(self, platforms: List[pygame.Rect]):
        """Handle collision with platforms"""
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
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 6
            health_ratio = self.health / self.max_health
            
            # Background
            pygame.draw.rect(screen, RED, (self.x, self.y - 15, bar_width, bar_height))
            # Health
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 15, bar_width * health_ratio, bar_height))

class Level:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.platforms = []
        self.enemies = []
        self.background_layers = []
        
    def add_platform(self, x: int, y: int, width: int, height: int):
        """Add a platform to the level"""
        self.platforms.append(pygame.Rect(x, y, width, height))
    
    def add_enemy(self, enemy: Enemy):
        """Add an enemy to the level"""
        self.enemies.append(enemy)
    
    def update(self, dt: int, player: Player):
        """Update level state"""
        # Update enemies
        for enemy in self.enemies[:]:  # Create copy to allow removal during iteration
            enemy.update(dt, player, self.platforms)
            
            # Check if enemy is dead
            if enemy.health <= 0:
                player.souls += enemy.souls_value
                player.experience += 10
                self.enemies.remove(enemy)
            
            # Check player attack hitting enemy
            attack_rect = player.get_attack_rect()
            if attack_rect.colliderect(enemy.get_rect()) and player.attacking:
                enemy.take_damage(50)
    
    def draw(self, screen: pygame.Surface, asset_manager: AssetManager):
        """Draw the level"""
        # Draw background
        if 'castle_bg' in asset_manager.images:
            screen.blit(asset_manager.images['castle_bg'], (0, 0))
        
        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(screen, (100, 50, 0), platform)
            pygame.draw.rect(screen, (150, 75, 0), platform, 2)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Reserka - Gothic Edition")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        
        # Load assets
        assets_path = Path(__file__).parent.parent / "assets"
        self.asset_manager = AssetManager(assets_path)
        
        # Game objects
        self.player = None
        self.current_level = None
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        
        # Game state
        self.keys_pressed = {}
        self.menu_selection = 0
        self.menu_options = ["Start Game", "Controls", "Quit"]
        
        self.init_level()
    
    def init_level(self):
        """Initialize the game level"""
        self.current_level = Level(SCREEN_WIDTH * 2, SCREEN_HEIGHT)
        
        # Create platforms
        self.current_level.add_platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH * 2, 40)  # Ground
        self.current_level.add_platform(200, SCREEN_HEIGHT - 200, 300, 20)  # Platform 1
        self.current_level.add_platform(600, SCREEN_HEIGHT - 150, 200, 20)  # Platform 2
        self.current_level.add_platform(900, SCREEN_HEIGHT - 300, 250, 20)  # Platform 3
        self.current_level.add_platform(400, SCREEN_HEIGHT - 350, 150, 20)  # High platform
        
        # Create player
        self.player = Player(100, SCREEN_HEIGHT - 200, self.asset_manager)
        
        # Add enemies
        self.current_level.add_enemy(Enemy(300, SCREEN_HEIGHT - 280, 60, 60, 'fire_skull', self.asset_manager))
        self.current_level.add_enemy(Enemy(650, SCREEN_HEIGHT - 230, 80, 80, 'demon', self.asset_manager))
        self.current_level.add_enemy(Enemy(950, SCREEN_HEIGHT - 380, 70, 60, 'hell_hound', self.asset_manager))
        self.current_level.add_enemy(Enemy(1200, SCREEN_HEIGHT - 120, 60, 60, 'fire_skull', self.asset_manager))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:  # Start Game
                            self.state = GameState.PLAYING
                        elif self.menu_selection == 1:  # Controls
                            pass  # TODO: Show controls screen
                        elif self.menu_selection == 2:  # Quit
                            return False
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
        
        return True
    
    def update(self, dt: int):
        """Update game state"""
        if self.state == GameState.PLAYING:
            # Update player
            self.player.handle_input(self.keys_pressed, dt)
            self.player.update(dt, self.current_level.platforms)
            
            # Update level
            self.current_level.update(dt, self.player)
            
            # Check game over condition
            if self.player.health <= 0:
                self.state = GameState.GAME_OVER
            
            # Check if player fell off screen
            if self.player.y > SCREEN_HEIGHT:
                self.player.health = 0
                self.state = GameState.GAME_OVER
    
    def draw(self):
        """Draw the game"""
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw the main menu"""
        title = self.large_font.render("RESERKA", True, GOLD)
        subtitle = self.font.render("Gothic Edition", True, WHITE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw menu options
        for i, option in enumerate(self.menu_options):
            color = GOLD if i == self.menu_selection else WHITE
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 350 + i * 60))
            self.screen.blit(text, text_rect)
        
        # Instructions
        instruction = self.font.render("Use arrow keys and ENTER to navigate", True, WHITE)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_game(self):
        """Draw the main game"""
        # Draw level
        self.current_level.draw(self.screen, self.asset_manager)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw the game UI"""
        # Health bar
        bar_width = 200
        bar_height = 20
        health_ratio = self.player.health / self.player.max_health
        
        pygame.draw.rect(self.screen, RED, (20, 20, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 20, bar_width * health_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (20, 20, bar_width, bar_height), 2)
        
        health_text = self.font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (20, 50))
        
        # Souls (currency)
        souls_text = self.font.render(f"Souls: {self.player.souls}", True, GOLD)
        self.screen.blit(souls_text, (20, 80))
        
        # Level
        level_text = self.font.render(f"Level: {self.player.level}", True, WHITE)
        self.screen.blit(level_text, (20, 110))
        
        # Controls
        controls = [
            "WASD/Arrows: Move",
            "SPACE/W: Jump (double jump)",
            "X/J: Attack",
            "ESC: Pause"
        ]
        
        for i, control in enumerate(controls):
            text = pygame.font.Font(None, 24).render(control, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 250, 20 + i * 25))
    
    def draw_pause_overlay(self):
        """Draw pause screen overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.large_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        instruction = self.font.render("Press ESC to resume", True, WHITE)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(DARK_RED)
        
        game_over_text = self.large_font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        souls_text = self.font.render(f"Souls Collected: {self.player.souls}", True, GOLD)
        souls_rect = souls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(souls_text, souls_rect)
        
        restart_text = self.font.render("Press R to restart or ESC to menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
        
        # Handle restart
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.init_level()
            self.state = GameState.PLAYING
        elif keys[pygame.K_ESCAPE]:
            self.state = GameState.MENU
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS)
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
