#!/usr/bin/env python3
"""
Enhanced Level System for Reserka Gothic
Includes improved terrain, textures, doors, and level progression
"""

import pygame
import json
import math
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

# Import our new pixel texture manager
try:
    from pixel_texture_manager import PixelTextureManager
    PIXEL_TEXTURES_AVAILABLE = True
except ImportError:
    print("⚠️ Pixel texture manager not available, using fallback textures")
    PIXEL_TEXTURES_AVAILABLE = False

class TileType(Enum):
    EMPTY = 0
    STONE_PLATFORM = 1
    STONE_WALL = 2
    GRASS_PLATFORM = 3
    DIRT = 4
    DOOR = 5
    SPIKE = 6
    DECORATION = 7

class DoorType(Enum):
    WOODEN = "wooden"
    IRON = "iron" 
    MAGIC = "magic"

@dataclass
class Door:
    x: int
    y: int
    width: int
    height: int
    door_type: DoorType
    target_level: str
    target_x: int = 100
    target_y: int = 600
    requires_key: bool = False
    key_type: str = None

@dataclass 
class Tile:
    x: int
    y: int
    tile_type: TileType
    texture_id: str = None
    collision: bool = True
    damage: int = 0

class TerrainGenerator:
    """Generates terrain using actual environment assets"""
    
    def __init__(self, screen_width: int, screen_height: int, asset_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = 32
        self.tiles = []
        self.textures = {}
        self.asset_manager = asset_manager
        self.load_terrain_textures()
    
    def load_terrain_textures(self):
        """Load terrain textures from actual game assets"""
        if self.asset_manager:
            self.load_textures_from_assets()
        else:
            self.create_fallback_textures()
    
    def load_textures_from_assets(self):
        """Load textures from the asset manager using atlas textures and environment assets"""
        # Load from texture atlas - these are the actual game textures
        if hasattr(self.asset_manager, 'textures'):
            # Use specific tiles from the atlas for different terrain types
            terrain_mapping = {
                'stone': 'tile_0_0',      # Top-left tile for stone
                'stone_wall': 'tile_1_0',  # Stone wall variant
                'grass': 'tile_2_0',       # Grass tile
                'dirt': 'tile_3_0',        # Dirt tile
                'stone_dark': 'tile_0_1',  # Darker stone variant
                'stone_light': 'tile_1_1', # Lighter stone variant
                'moss_stone': 'tile_2_1',  # Mossy stone
                'cracked_stone': 'tile_3_1', # Cracked stone
            }
            
            # Load textures from atlas
            for terrain_type, atlas_id in terrain_mapping.items():
                texture = self.asset_manager.get_texture(atlas_id)
                if texture:
                    self.textures[terrain_type] = texture
                    print(f"  ✓ Loaded {terrain_type} from {atlas_id}")
        
        # Load tileset for more detailed terrain
        cave_tileset = self.asset_manager.get_environment('cave_tileset')
        if cave_tileset:
            # Extract specific tiles from the tileset
            self.extract_tileset_textures(cave_tileset)
        
        # Create door textures from props
        self.create_door_textures()
        
        # If we don't have enough textures, create fallbacks
        if len(self.textures) < 4:
            self.create_fallback_textures()
    
    def extract_tileset_textures(self, tileset):
        """Extract individual tiles from the environment tileset"""
        tile_size = 32  # Assuming 32x32 tiles in the tileset
        tileset_width = tileset.get_width()
        tileset_height = tileset.get_height()
        
        tiles_x = min(tileset_width // tile_size, 8)  # Limit to reasonable number
        tiles_y = min(tileset_height // tile_size, 8)
        
        # Extract tiles for different purposes
        terrain_assignments = {
            (0, 0): 'platform_stone',
            (1, 0): 'platform_stone_alt',
            (2, 0): 'wall_stone',
            (3, 0): 'wall_stone_alt', 
            (0, 1): 'floor_stone',
            (1, 1): 'floor_stone_cracked',
            (2, 1): 'wall_detail',
            (3, 1): 'corner_stone',
        }
        
        for y in range(min(tiles_y, 4)):
            for x in range(min(tiles_x, 4)):
                if (x, y) in terrain_assignments:
                    try:
                        rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                        tile = tileset.subsurface(rect).copy()
                        terrain_name = terrain_assignments[(x, y)]
                        self.textures[terrain_name] = tile
                        print(f"  ✓ Extracted {terrain_name} from tileset")
                    except ValueError:
                        # Subsurface failed, skip this tile
                        continue
    
    def create_door_textures(self):
        """Create door textures from props or generate them"""
        # Try to get door textures from cave props
        cave_props_1 = self.asset_manager.get_environment('cave_props_1')
        cave_props_2 = self.asset_manager.get_environment('cave_props_2')
        
        if cave_props_1:
            # Try to extract a door-like texture from props
            # This is a guess - adjust coordinates based on actual prop layout
            try:
                door_rect = pygame.Rect(64, 0, 32, 64)  # Assuming door at position 64,0
                if door_rect.right <= cave_props_1.get_width() and door_rect.bottom <= cave_props_1.get_height():
                    door_texture = cave_props_1.subsurface(door_rect).copy()
                    self.textures['door'] = door_texture
                    print("  ✓ Extracted door from cave_props_1")
                    return
            except ValueError:
                pass
        
        # Fallback: create a simple door texture that matches the environment
        self.create_environment_door()
    
    def create_environment_door(self):
        """Create a door texture that matches the cave environment"""
        door_surf = pygame.Surface((self.tile_size, self.tile_size * 2))
        
        # Use darker cave colors to match environment
        wood_colors = [(101, 67, 33), (139, 89, 49), (85, 55, 25), (120, 80, 40)]
        
        # Create wood grain pattern matching cave aesthetic
        for y in range(0, self.tile_size * 2, 4):
            for x in range(0, self.tile_size, 4):
                grain_index = (y // 8) % len(wood_colors)
                color = wood_colors[grain_index]
                pygame.draw.rect(door_surf, color, (x, y, 4, 4))
        
        # Add iron reinforcements to match cave theme
        iron_color = (80, 80, 90)
        # Horizontal reinforcements
        pygame.draw.rect(door_surf, iron_color, (4, 16, self.tile_size - 8, 4))
        pygame.draw.rect(door_surf, iron_color, (4, 40, self.tile_size - 8, 4))
        
        # Door handle
        handle_color = (120, 120, 100)
        pygame.draw.rect(door_surf, handle_color, (self.tile_size - 8, self.tile_size, 4, 6))
        
        self.textures['door'] = door_surf
    
    def create_fallback_textures(self):
        """Create fallback textures if assets are not available"""
        print("  ⚠️ Creating fallback textures - using environment-matched colors")
        
        # Use colors that match the cave environment backgrounds
        cave_stone_colors = [(85, 85, 95), (70, 70, 80), (100, 100, 110)]
        cave_wall_colors = [(60, 60, 70), (50, 50, 60), (75, 75, 85)]
        
        # Stone platform texture
        stone_surf = pygame.Surface((self.tile_size, self.tile_size))
        for y in range(0, self.tile_size, 4):
            for x in range(0, self.tile_size, 4):
                color_index = ((x // 4) + (y // 4)) % len(cave_stone_colors)
                color = cave_stone_colors[color_index]
                pygame.draw.rect(stone_surf, color, (x, y, 4, 4))
        self.textures['stone'] = stone_surf
        self.textures['platform_stone'] = stone_surf
        
        # Stone wall texture (darker)
        wall_surf = pygame.Surface((self.tile_size, self.tile_size))
        for y in range(0, self.tile_size, 4):
            for x in range(0, self.tile_size, 4):
                color_index = ((x // 4) + (y // 4)) % len(cave_wall_colors)
                color = cave_wall_colors[color_index]
                pygame.draw.rect(wall_surf, color, (x, y, 4, 4))
        self.textures['stone_wall'] = wall_surf
        self.textures['wall_stone'] = wall_surf
        
        # Grass (mossy cave floor)
        grass_surf = pygame.Surface((self.tile_size, self.tile_size))
        moss_colors = [(40, 60, 30), (50, 70, 35), (35, 55, 25)]
        for y in range(0, self.tile_size, 4):
            for x in range(0, self.tile_size, 4):
                color_index = ((x // 4) * 3 + (y // 4) * 7) % len(moss_colors)
                color = moss_colors[color_index]
                pygame.draw.rect(grass_surf, color, (x, y, 4, 4))
        self.textures['grass'] = grass_surf
        
        # Dirt (cave floor)
        dirt_surf = pygame.Surface((self.tile_size, self.tile_size))
        dirt_colors = [(70, 50, 35), (85, 60, 40), (60, 40, 30)]
        for y in range(0, self.tile_size, 4):
            for x in range(0, self.tile_size, 4):
                color_index = ((x // 4) * 5 + (y // 4) * 3) % len(dirt_colors)
                color = dirt_colors[color_index]
                pygame.draw.rect(dirt_surf, color, (x, y, 4, 4))
        self.textures['dirt'] = dirt_surf
        
        # Create door if not already created
        if 'door' not in self.textures:
            self.create_environment_door()
    
    # ===== CAVE ENVIRONMENTS =====
    def generate_cave_depths(self) -> Tuple[List[Tile], List[Door]]:
        """Generate deep cave level with stalactites and underground feel"""
        tiles = []
        doors = []
        
        # Cave floor
        ground_y = self.screen_height - 40
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, ground_y, TileType.STONE_PLATFORM, 'stone'))
            tiles.append(Tile(x, ground_y + self.tile_size, TileType.STONE_WALL, 'stone'))
        
        # Stalactites from ceiling
        for x in range(100, self.screen_width - 100, 150):
            height = 80 + (x % 120)
            for y in range(0, height, self.tile_size):
                tiles.append(Tile(x, y, TileType.STONE_WALL, 'stone'))
        
        # Cave platforms at different heights
        platforms = [
            (200, 450, 4, 'stone'),
            (450, 380, 6, 'stone'),
            (750, 320, 5, 'stone'),
            (1050, 250, 4, 'stone'),
        ]
        
        for px, py, width, texture in platforms:
            for i in range(width):
                x = px + i * self.tile_size
                tiles.append(Tile(x, py, TileType.STONE_PLATFORM, texture))
        
        # Connections to other cave areas
        doors.append(Door(50, ground_y - 64, 64, 64, DoorType.WOODEN, "cave_passages"))
        doors.append(Door(self.screen_width - 100, ground_y - 64, 64, 64, DoorType.IRON, "gothic_castle"))
        
        return tiles, doors
    
    def generate_cave_passages(self) -> Tuple[List[Tile], List[Door]]:
        """Generate winding cave passages"""
        tiles = []
        doors = []
        
        # Winding cave floor
        y_levels = [600, 550, 500, 480, 520, 560, 580]
        section_width = self.screen_width // len(y_levels)
        
        for i, y_level in enumerate(y_levels):
            start_x = i * section_width
            end_x = (i + 1) * section_width
            
            for x in range(start_x, end_x, self.tile_size):
                tiles.append(Tile(x, y_level, TileType.STONE_PLATFORM, 'stone'))
                tiles.append(Tile(x, y_level + self.tile_size, TileType.DIRT, 'dirt'))
        
        # Add connecting platforms
        for i in range(len(y_levels) - 1):
            x_pos = (i + 1) * section_width - 32
            y1 = y_levels[i]
            y2 = y_levels[i + 1]
            
            # Create steps between levels
            if y1 != y2:
                steps = abs(y1 - y2) // 32 + 1
                step_height = (y2 - y1) // steps
                for s in range(steps):
                    step_y = y1 + s * step_height
                    tiles.append(Tile(x_pos, step_y, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(50, y_levels[0] - 64, 64, 64, DoorType.WOODEN, "cave_depths"))
        doors.append(Door(self.screen_width - 100, y_levels[-1] - 64, 64, 64, DoorType.WOODEN, "cave_chamber"))
        
        return tiles, doors
    
    def generate_cave_chamber(self) -> Tuple[List[Tile], List[Door]]:
        """Generate large cave chamber with treasure"""
        tiles = []
        doors = []
        
        # Large chamber floor
        ground_y = self.screen_height - 80
        for x in range(100, self.screen_width - 100, self.tile_size):
            tiles.append(Tile(x, ground_y, TileType.STONE_PLATFORM, 'stone'))
            tiles.append(Tile(x, ground_y + self.tile_size, TileType.STONE_WALL, 'stone'))
        
        # Central raised platform for treasure/boss
        center_x = self.screen_width // 2
        for x in range(center_x - 96, center_x + 96, self.tile_size):
            tiles.append(Tile(x, ground_y - 64, TileType.STONE_PLATFORM, 'stone'))
        
        # Side platforms
        side_platforms = [
            (300, ground_y - 120, 3),
            (self.screen_width - 400, ground_y - 120, 3)
        ]
        
        for px, py, width in side_platforms:
            for i in range(width):
                tiles.append(Tile(px + i * self.tile_size, py, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(150, ground_y - 64, 64, 64, DoorType.WOODEN, "cave_passages"))
        doors.append(Door(center_x - 32, ground_y - 128, 64, 64, DoorType.MAGIC, "treasure_chamber"))
        
        return tiles, doors
    
    # ===== GOTHIC ENVIRONMENTS =====
    def generate_gothic_castle(self) -> Tuple[List[Tile], List[Door]]:
        """Generate gothic castle exterior with towers"""
        tiles = []
        doors = []
        
        # Castle courtyard
        ground_y = self.screen_height - 40
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, ground_y, TileType.STONE_PLATFORM, 'stone'))
            tiles.append(Tile(x, ground_y + self.tile_size, TileType.STONE_WALL, 'stone'))
        
        # Castle towers and battlements
        tower_configs = [
            (200, ground_y - 200, 4, 'stone'),  # Left tower
            (600, ground_y - 150, 6, 'stone'),  # Main keep
            (1000, ground_y - 180, 3, 'stone')  # Right tower
        ]
        
        for tx, ty, width, texture in tower_configs:
            for i in range(width):
                x = tx + i * self.tile_size
                # Tower walls
                for y in range(ty, ground_y, self.tile_size):
                    tiles.append(Tile(x, y, TileType.STONE_WALL, texture))
                # Tower top platforms
                tiles.append(Tile(x, ty - self.tile_size, TileType.STONE_PLATFORM, texture))
        
        # Connecting walkways
        walkway_configs = [
            (300, ground_y - 120, 200),  # Left to center
            (850, ground_y - 120, 150)   # Center to right
        ]
        
        for wx, wy, length in walkway_configs:
            for x in range(wx, wx + length, self.tile_size):
                tiles.append(Tile(x, wy, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(50, ground_y - 64, 64, 64, DoorType.WOODEN, "cave_chamber"))
        doors.append(Door(632, ground_y - 214, 64, 64, DoorType.IRON, "castle_interior"))  # Main keep entrance
        doors.append(Door(self.screen_width - 100, ground_y - 64, 64, 64, DoorType.WOODEN, "gothic_town"))
        
        return tiles, doors
    
    def generate_castle_interior(self) -> Tuple[List[Tile], List[Door]]:
        """Generate castle interior with multiple floors"""
        tiles = []
        doors = []
        
        # Multiple floor levels
        floor_levels = [self.screen_height - 40, self.screen_height - 200, self.screen_height - 360]
        
        for floor_y in floor_levels:
            # Floor platforms
            for x in range(100, self.screen_width - 100, self.tile_size):
                tiles.append(Tile(x, floor_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Staircases between floors
        stair_x = 200
        for i in range(len(floor_levels) - 1):
            start_y = floor_levels[i]
            end_y = floor_levels[i + 1]
            steps = (start_y - end_y) // self.tile_size
            
            for step in range(steps):
                step_y = start_y - (step + 1) * self.tile_size
                step_x = stair_x + step * 16
                tiles.append(Tile(step_x, step_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Room divisions (walls)
        wall_positions = [400, 800]
        for wall_x in wall_positions:
            for floor_y in floor_levels:
                for y in range(floor_y - 160, floor_y, self.tile_size):
                    tiles.append(Tile(wall_x, y, TileType.STONE_WALL, 'stone'))
        
        doors.append(Door(632 - 64, floor_levels[0] - 64, 64, 64, DoorType.IRON, "gothic_castle"))
        doors.append(Door(self.screen_width - 150, floor_levels[-1] - 64, 64, 64, DoorType.MAGIC, "demon_throne"))
        
        return tiles, doors
    
    def generate_gothic_town(self) -> Tuple[List[Tile], List[Door]]:
        """Generate gothic town with buildings"""
        tiles = []
        doors = []
        
        # Town street
        ground_y = self.screen_height - 40
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, ground_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Buildings of varying heights
        building_configs = [
            (150, ground_y - 160, 4, 'stone'),
            (350, ground_y - 200, 5, 'stone'),
            (600, ground_y - 120, 3, 'stone'),
            (850, ground_y - 240, 6, 'stone'),
            (1100, ground_y - 180, 4, 'stone')
        ]
        
        for bx, by, width, texture in building_configs:
            for i in range(width):
                x = bx + i * self.tile_size
                # Building walls
                for y in range(by, ground_y, self.tile_size):
                    tiles.append(Tile(x, y, TileType.STONE_WALL, texture))
                # Rooftop
                tiles.append(Tile(x, by - self.tile_size, TileType.STONE_PLATFORM, texture))
        
        # Connecting rooftop platforms
        roof_connections = [
            (280, ground_y - 130, 70),
            (730, ground_y - 150, 120)
        ]
        
        for rx, ry, length in roof_connections:
            for x in range(rx, rx + length, self.tile_size):
                tiles.append(Tile(x, ry, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(50, ground_y - 64, 64, 64, DoorType.WOODEN, "gothic_castle"))
        doors.append(Door(self.screen_width - 100, ground_y - 64, 64, 64, DoorType.WOODEN, "night_town"))
        
        return tiles, doors
    
    # ===== NIGHT ENVIRONMENTS =====
    def generate_night_town(self) -> Tuple[List[Tile], List[Door]]:
        """Generate spooky night town"""
        tiles = []
        doors = []
        
        # Cobblestone street
        ground_y = self.screen_height - 40
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, ground_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Abandoned buildings with broken platforms
        building_ruins = [
            (200, ground_y - 140, 3),
            (450, ground_y - 180, 4),
            (750, ground_y - 100, 2),
            (950, ground_y - 220, 5)
        ]
        
        for bx, by, width in building_ruins:
            for i in range(width):
                x = bx + i * self.tile_size
                # Broken walls (not full height)
                wall_height = (i % 3 + 2) * self.tile_size
                for y in range(by + wall_height, ground_y, self.tile_size):
                    tiles.append(Tile(x, y, TileType.STONE_WALL, 'stone'))
                # Broken platforms
                if i % 2 == 0:  # Only every other platform
                    tiles.append(Tile(x, by, TileType.STONE_PLATFORM, 'stone'))
        
        # Floating debris platforms
        debris = [
            (350, ground_y - 80, 1),
            (600, ground_y - 160, 2),
            (850, ground_y - 120, 1)
        ]
        
        for dx, dy, width in debris:
            for i in range(width):
                tiles.append(Tile(dx + i * self.tile_size, dy, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(50, ground_y - 64, 64, 64, DoorType.WOODEN, "gothic_town"))
        doors.append(Door(self.screen_width - 100, ground_y - 64, 64, 64, DoorType.IRON, "haunted_forest"))
        
        return tiles, doors
    
    def generate_haunted_forest(self) -> Tuple[List[Tile], List[Door]]:
        """Generate haunted forest with tree platforms"""
        tiles = []
        doors = []
        
        # Forest floor (uneven)
        ground_heights = [640, 650, 630, 660, 640, 655, 645]
        section_width = self.screen_width // len(ground_heights)
        
        for i, height in enumerate(ground_heights):
            start_x = i * section_width
            end_x = (i + 1) * section_width
            
            for x in range(start_x, end_x, self.tile_size):
                tiles.append(Tile(x, height, TileType.GRASS_PLATFORM, 'grass'))
                tiles.append(Tile(x, height + self.tile_size, TileType.DIRT, 'dirt'))
        
        # Tree trunk platforms (vertical)
        tree_positions = [250, 500, 750, 1000]
        
        for tree_x in tree_positions:
            tree_height = 300 + (tree_x % 150)
            ground_y = 650  # Approximate ground level
            
            # Tree trunk (every few blocks for climbing)
            for y in range(ground_y - tree_height, ground_y, self.tile_size * 2):
                tiles.append(Tile(tree_x, y, TileType.STONE_WALL, 'stone'))
            
            # Tree branch platforms
            branch_levels = [ground_y - 120, ground_y - 200, ground_y - 280]
            for branch_y in branch_levels:
                # Left branch
                for x in range(tree_x - 64, tree_x, self.tile_size):
                    tiles.append(Tile(x, branch_y, TileType.GRASS_PLATFORM, 'grass'))
                # Right branch
                for x in range(tree_x + 32, tree_x + 96, self.tile_size):
                    tiles.append(Tile(x, branch_y, TileType.GRASS_PLATFORM, 'grass'))
        
        doors.append(Door(50, 640 - 64, 64, 64, DoorType.IRON, "night_town"))
        doors.append(Door(self.screen_width - 100, 640 - 64, 64, 64, DoorType.WOODEN, "mountain_pass"))
        
        return tiles, doors
    
    # ===== MOUNTAIN ENVIRONMENTS =====
    def generate_mountain_pass(self) -> Tuple[List[Tile], List[Door]]:
        """Generate mountain pass with steep terrain"""
        tiles = []
        doors = []
        
        # Ascending mountain path
        base_heights = [650, 600, 550, 480, 420, 380, 300]
        section_width = self.screen_width // len(base_heights)
        
        for i, height in enumerate(base_heights):
            start_x = i * section_width
            end_x = (i + 1) * section_width
            
            # Create rocky platforms at different heights
            for x in range(start_x, end_x, self.tile_size):
                variation = (x % 64) - 32  # Add some height variation
                actual_height = height + variation
                tiles.append(Tile(x, actual_height, TileType.STONE_PLATFORM, 'stone'))
                tiles.append(Tile(x, actual_height + self.tile_size, TileType.STONE_WALL, 'stone'))
        
        # Rocky outcroppings and cliff faces
        cliff_positions = [300, 700, 1000]
        for cliff_x in cliff_positions:
            cliff_height = 200 + (cliff_x % 100)
            base_y = 600
            
            for y in range(base_y - cliff_height, base_y, self.tile_size):
                tiles.append(Tile(cliff_x, y, TileType.STONE_WALL, 'stone'))
                # Add some horizontal platforms for climbing
                if y % 64 == 0:
                    tiles.append(Tile(cliff_x + self.tile_size, y, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(50, 640, 64, 64, DoorType.WOODEN, "haunted_forest"))
        doors.append(Door(self.screen_width - 100, 290, 64, 64, DoorType.IRON, "rocky_cliffs"))
        
        return tiles, doors
    
    def generate_rocky_cliffs(self) -> Tuple[List[Tile], List[Door]]:
        """Generate dangerous rocky cliffs"""
        tiles = []
        doors = []
        
        # Vertical cliff faces with sparse platforms
        cliff_levels = [600, 500, 400, 300, 200, 100]
        
        for i, level_y in enumerate(cliff_levels):
            # Create narrow ledges
            ledge_positions = [(200 + i * 150, 4), (600 + i * 100, 3), (1000 - i * 50, 5)]
            
            for ledge_x, width in ledge_positions:
                if ledge_x + width * self.tile_size <= self.screen_width:
                    for j in range(width):
                        x = ledge_x + j * self.tile_size
                        tiles.append(Tile(x, level_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Dangerous spike areas at bottom
        for x in range(400, 800, self.tile_size):
            tiles.append(Tile(x, 650, TileType.SPIKE, 'stone'))
        
        # Climbing walls
        wall_positions = [150, 550, 950]
        for wall_x in wall_positions:
            for y in range(150, 650, self.tile_size * 2):  # Sparse handholds
                tiles.append(Tile(wall_x, y, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(200, 590, 64, 64, DoorType.IRON, "mountain_pass"))
        doors.append(Door(self.screen_width - 150, 90, 64, 64, DoorType.MAGIC, "lava_caverns"))
        
        return tiles, doors
    
    # ===== UNDERGROUND DANGEROUS AREAS =====
    def generate_lava_caverns(self) -> Tuple[List[Tile], List[Door]]:
        """Generate lava-filled caverns with dangerous platforms"""
        tiles = []
        doors = []
        
        # Lava floor (deadly)
        lava_y = self.screen_height - 80
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, lava_y, TileType.SPIKE, 'stone'))  # Lava is deadly
        
        # Safe rocky platforms above lava
        safe_platforms = [
            (100, lava_y - 100, 3),
            (280, lava_y - 150, 2),
            (450, lava_y - 80, 4),
            (650, lava_y - 180, 3),
            (850, lava_y - 120, 5),
            (1100, lava_y - 200, 3)
        ]
        
        for px, py, width in safe_platforms:
            for i in range(width):
                x = px + i * self.tile_size
                tiles.append(Tile(x, py, TileType.STONE_PLATFORM, 'stone'))
        
        # Hanging stalactites (obstacles)
        stalactite_positions = [200, 400, 600, 800, 1000]
        for stala_x in stalactite_positions:
            height = 100 + (stala_x % 80)
            for y in range(0, height, self.tile_size):
                tiles.append(Tile(stala_x + 16, y, TileType.STONE_WALL, 'stone'))
        
        # Lava geysers (moving spikes - represented as spikes for now)
        geyser_positions = [300, 500, 700, 900]
        for geyser_x in geyser_positions:
            tiles.append(Tile(geyser_x, lava_y - 32, TileType.SPIKE, 'stone'))
        
        doors.append(Door(120, lava_y - 164, 64, 64, DoorType.MAGIC, "rocky_cliffs"))
        doors.append(Door(1120, lava_y - 264, 64, 64, DoorType.MAGIC, "treasure_chamber"))
        
        return tiles, doors
    
    def generate_treasure_chamber(self) -> Tuple[List[Tile], List[Door]]:
        """Generate treasure chamber with valuable loot"""
        tiles = []
        doors = []
        
        # Ornate chamber floor
        ground_y = self.screen_height - 120
        for x in range(200, self.screen_width - 200, self.tile_size):
            tiles.append(Tile(x, ground_y, TileType.STONE_PLATFORM, 'stone'))
            tiles.append(Tile(x, ground_y + self.tile_size, TileType.STONE_WALL, 'stone'))
        
        # Central treasure platform
        center_x = self.screen_width // 2
        treasure_platform_width = 6
        
        for i in range(treasure_platform_width):
            x = center_x - (treasure_platform_width // 2) * self.tile_size + i * self.tile_size
            tiles.append(Tile(x, ground_y - 64, TileType.STONE_PLATFORM, 'stone'))
        
        # Ornate pillars around the chamber
        pillar_positions = [250, 450, 850, 1050]
        for pillar_x in pillar_positions:
            for y in range(ground_y - 200, ground_y, self.tile_size):
                tiles.append(Tile(pillar_x, y, TileType.STONE_WALL, 'stone'))
            # Pillar tops
            for x in range(pillar_x - self.tile_size, pillar_x + self.tile_size * 2, self.tile_size):
                tiles.append(Tile(x, ground_y - 232, TileType.STONE_PLATFORM, 'stone'))
        
        # Elevated walkways connecting pillars
        walkway_y = ground_y - 160
        # Left to center
        for x in range(250 + self.tile_size, center_x - 96, self.tile_size):
            tiles.append(Tile(x, walkway_y, TileType.STONE_PLATFORM, 'stone'))
        # Center to right
        for x in range(center_x + 96, 850, self.tile_size):
            tiles.append(Tile(x, walkway_y, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(center_x - 32, ground_y - 128, 64, 64, DoorType.MAGIC, "cave_chamber"))
        doors.append(Door(250, ground_y - 296, 64, 64, DoorType.MAGIC, "demon_throne"))
        
        return tiles, doors
    
    # ===== PIXEL PLATFORMER LEVELS =====
    def generate_pixel_dungeon(self) -> Tuple[List[Tile], List[Door]]:
        """Generate pixel-art style dungeon"""
        tiles = []
        doors = []
        
        # Dungeon corridors
        corridor_y = self.screen_height - 80
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, corridor_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Dungeon rooms with different levels
        room_configs = [
            (150, corridor_y - 120, 6, 4),  # x, y, width, height
            (450, corridor_y - 160, 8, 5),
            (850, corridor_y - 140, 7, 4)
        ]
        
        for rx, ry, width, height in room_configs:
            # Room floor
            for x in range(rx, rx + width * self.tile_size, self.tile_size):
                tiles.append(Tile(x, ry + height * self.tile_size, TileType.STONE_PLATFORM, 'stone'))
            
            # Room walls
            for y in range(ry, ry + height * self.tile_size, self.tile_size):
                tiles.append(Tile(rx - self.tile_size, y, TileType.STONE_WALL, 'stone'))  # Left wall
                tiles.append(Tile(rx + width * self.tile_size, y, TileType.STONE_WALL, 'stone'))  # Right wall
            
            # Internal platforms
            if width > 4:
                for x in range(rx + self.tile_size, rx + (width - 1) * self.tile_size, self.tile_size * 2):
                    tiles.append(Tile(x, ry + self.tile_size, TileType.STONE_PLATFORM, 'stone'))
        
        # Connecting platforms between rooms
        bridge_configs = [
            (300, corridor_y - 60, 100),  # x, y, length
            (700, corridor_y - 80, 120)
        ]
        
        for bx, by, length in bridge_configs:
            for x in range(bx, bx + length, self.tile_size):
                tiles.append(Tile(x, by, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(50, corridor_y - 64, 64, 64, DoorType.WOODEN, "pixel_forest"))
        doors.append(Door(self.screen_width - 100, corridor_y - 64, 64, 64, DoorType.IRON, "scifi_lab"))
        
        return tiles, doors
    
    def generate_pixel_forest(self) -> Tuple[List[Tile], List[Door]]:
        """Generate pixel-art style forest level"""
        tiles = []
        doors = []
        
        # Forest ground (uneven)
        ground_heights = [660, 640, 670, 650, 630, 680, 660]
        section_width = self.screen_width // len(ground_heights)
        
        for i, height in enumerate(ground_heights):
            start_x = i * section_width
            end_x = (i + 1) * section_width
            
            for x in range(start_x, end_x, self.tile_size):
                tiles.append(Tile(x, height, TileType.GRASS_PLATFORM, 'grass'))
                tiles.append(Tile(x, height + self.tile_size, TileType.DIRT, 'dirt'))
        
        # Pixel-style tree platforms
        tree_configs = [
            (200, 500, 2),  # x, y, width
            (500, 480, 3),
            (800, 520, 2),
            (1100, 460, 3)
        ]
        
        for tx, ty, width in tree_configs:
            # Tree base
            for x in range(tx, tx + width * self.tile_size, self.tile_size):
                for y in range(ty + 64, 660, self.tile_size):  # Tree trunk
                    tiles.append(Tile(x, y, TileType.STONE_WALL, 'stone'))
            
            # Tree canopy platforms
            canopy_levels = [ty, ty - 80, ty - 160]
            for level in canopy_levels:
                canopy_width = width + 2
                start_x = tx - self.tile_size
                for x in range(start_x, start_x + canopy_width * self.tile_size, self.tile_size):
                    tiles.append(Tile(x, level, TileType.GRASS_PLATFORM, 'grass'))
        
        # Mushroom platforms (bouncy)
        mushroom_positions = [350, 650, 950]
        for mushroom_x in mushroom_positions:
            tiles.append(Tile(mushroom_x, 620, TileType.GRASS_PLATFORM, 'grass'))
        
        doors.append(Door(50, 650, 64, 64, DoorType.WOODEN, "pixel_dungeon"))
        doors.append(Door(self.screen_width - 100, 650, 64, 64, DoorType.WOODEN, "underwater_ruins"))
        
        return tiles, doors
    
    # ===== OCEAN AND WATER LEVELS =====
    def generate_underwater_ruins(self) -> Tuple[List[Tile], List[Door]]:
        """Generate underwater ruins level"""
        tiles = []
        doors = []
        
        # Ocean floor
        ocean_floor_y = self.screen_height - 40
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, ocean_floor_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Sunken ruins at different depths
        ruin_configs = [
            (150, ocean_floor_y - 120, 5, 3),  # x, y, width, height
            (400, ocean_floor_y - 180, 6, 4),
            (700, ocean_floor_y - 100, 4, 2),
            (1000, ocean_floor_y - 200, 7, 5)
        ]
        
        for rx, ry, width, height in ruin_configs:
            # Ruin base
            for x in range(rx, rx + width * self.tile_size, self.tile_size):
                tiles.append(Tile(x, ry + height * self.tile_size, TileType.STONE_PLATFORM, 'stone'))
            
            # Broken walls and columns
            for i in range(width):
                x = rx + i * self.tile_size
                # Random broken wall heights
                wall_height = (i % 3 + 1) * self.tile_size
                for y in range(ry + height * self.tile_size - wall_height, ry + height * self.tile_size, self.tile_size):
                    tiles.append(Tile(x, y, TileType.STONE_WALL, 'stone'))
            
            # Interior platforms (partially collapsed)
            if width > 3:
                for x in range(rx + self.tile_size, rx + (width - 1) * self.tile_size, self.tile_size * 2):
                    if (x // self.tile_size) % 2 == 0:  # Only some platforms remain
                        tiles.append(Tile(x, ry + self.tile_size, TileType.STONE_PLATFORM, 'stone'))
        
        # Floating debris platforms
        debris_positions = [(300, 450), (600, 400), (900, 380)]
        for dx, dy in debris_positions:
            tiles.append(Tile(dx, dy, TileType.STONE_PLATFORM, 'stone'))
        
        # Coral formations (decorative obstacles)
        coral_positions = [250, 550, 850]
        for coral_x in coral_positions:
            for y in range(ocean_floor_y - 60, ocean_floor_y, self.tile_size):
                tiles.append(Tile(coral_x, y, TileType.DECORATION, 'grass'))  # Use grass texture for coral
        
        doors.append(Door(50, ocean_floor_y - 64, 64, 64, DoorType.WOODEN, "pixel_forest"))
        doors.append(Door(self.screen_width - 100, ocean_floor_y - 64, 64, 64, DoorType.IRON, "ocean_depths"))
        
        return tiles, doors
    
    def generate_ocean_depths(self) -> Tuple[List[Tile], List[Door]]:
        """Generate deep ocean abyss level"""
        tiles = []
        doors = []
        
        # Abyssal plain
        abyss_y = self.screen_height - 80
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, abyss_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Underwater mountains and trenches
        depth_variations = [
            (200, abyss_y - 200, 4),  # Underwater mountain
            (500, abyss_y - 100, 6),  # Lower ridge
            (800, abyss_y - 250, 5),  # Tall seamount
        ]
        
        for mx, my, width in depth_variations:
            # Build up from base
            for i in range(width):
                x = mx + i * self.tile_size
                # Pyramid-like shape
                height = min(i + 1, width - i) * self.tile_size
                for y in range(my + height, abyss_y, self.tile_size):
                    tiles.append(Tile(x, y, TileType.STONE_WALL, 'stone'))
                # Top platform
                tiles.append(Tile(x, my, TileType.STONE_PLATFORM, 'stone'))
        
        # Deep trenches (deadly)
        trench_positions = [350, 650, 950]
        for trench_x in trench_positions:
            for trench_i in range(3):
                x = trench_x + trench_i * self.tile_size
                tiles.append(Tile(x, abyss_y + self.tile_size, TileType.SPIKE, 'stone'))  # Deadly trench
        
        # Bioluminescent platforms (safe spots)
        bio_platforms = [(150, abyss_y - 150), (700, abyss_y - 120), (1100, abyss_y - 180)]
        for bx, by in bio_platforms:
            tiles.append(Tile(bx, by, TileType.STONE_PLATFORM, 'stone'))
        
        doors.append(Door(50, abyss_y - 64, 64, 64, DoorType.IRON, "underwater_ruins"))
        doors.append(Door(self.screen_width - 100, abyss_y - 64, 64, 64, DoorType.MAGIC, "alien_world"))
        
        return tiles, doors
    
    # ===== SCI-FI ENVIRONMENTS =====
    def generate_scifi_lab(self) -> Tuple[List[Tile], List[Door]]:
        """Generate futuristic laboratory"""
        tiles = []
        doors = []
        
        # Laboratory floor
        lab_floor_y = self.screen_height - 80
        for x in range(0, self.screen_width, self.tile_size):
            tiles.append(Tile(x, lab_floor_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Laboratory sections with different elevations
        lab_sections = [
            (100, lab_floor_y - 120, 8, 'stone'),  # Research area
            (400, lab_floor_y - 80, 10, 'stone'),   # Main lab floor
            (750, lab_floor_y - 160, 6, 'stone'),   # Elevated control room
            (1050, lab_floor_y - 100, 5, 'stone')   # Storage area
        ]
        
        for sx, sy, width, texture in lab_sections:
            for i in range(width):
                x = sx + i * self.tile_size
                tiles.append(Tile(x, sy, TileType.STONE_PLATFORM, texture))
        
        # Equipment/machinery (walls as obstacles)
        equipment_positions = [
            (200, lab_floor_y - 200, 2),  # Control console
            (500, lab_floor_y - 160, 3),  # Main equipment
            (800, lab_floor_y - 240, 2),  # Elevated machinery
        ]
        
        for ex, ey, width in equipment_positions:
            for i in range(width):
                x = ex + i * self.tile_size
                for y in range(ey, ey + 80, self.tile_size):
                    tiles.append(Tile(x, y, TileType.STONE_WALL, 'stone'))
        
        # Connecting bridges/walkways
        bridge_configs = [
            (350, lab_floor_y - 40, 50),   # Connect sections
            (650, lab_floor_y - 120, 100)
        ]
        
        for bx, by, length in bridge_configs:
            for x in range(bx, bx + length, self.tile_size):
                tiles.append(Tile(x, by, TileType.STONE_PLATFORM, 'stone'))
        
        # Hazard areas (energy fields)
        hazard_positions = [300, 600, 900]
        for hz_x in hazard_positions:
            tiles.append(Tile(hz_x, lab_floor_y - 32, TileType.SPIKE, 'stone'))
        
        doors.append(Door(50, lab_floor_y - 64, 64, 64, DoorType.IRON, "pixel_dungeon"))
        doors.append(Door(self.screen_width - 100, lab_floor_y - 64, 64, 64, DoorType.MAGIC, "alien_world"))
        
        return tiles, doors
    
    def generate_alien_world(self) -> Tuple[List[Tile], List[Door]]:
        """Generate alien planet surface"""
        tiles = []
        doors = []
        
        # Alien terrain (varied surface)
        alien_heights = [620, 580, 640, 560, 600, 650, 590]
        section_width = self.screen_width // len(alien_heights)
        
        for i, height in enumerate(alien_heights):
            start_x = i * section_width
            end_x = (i + 1) * section_width
            
            for x in range(start_x, end_x, self.tile_size):
                # Alien surface material
                tiles.append(Tile(x, height, TileType.STONE_PLATFORM, 'stone'))
                tiles.append(Tile(x, height + self.tile_size, TileType.STONE_WALL, 'stone'))
        
        # Alien crystal formations (decorative and functional)
        crystal_configs = [
            (200, 500, 3, 100),  # x, y, width, height
            (600, 450, 4, 120),
            (1000, 480, 2, 80)
        ]
        
        for cx, cy, width, height in crystal_configs:
            # Crystal base
            for i in range(width):
                x = cx + i * self.tile_size
                tiles.append(Tile(x, cy + height, TileType.STONE_PLATFORM, 'stone'))
                
                # Crystal spires
                spire_height = height - (i * 20) if i % 2 == 0 else height - 40
                for y in range(cy + height - spire_height, cy + height, self.tile_size):
                    tiles.append(Tile(x, y, TileType.STONE_WALL, 'stone'))
        
        # Floating alien platforms
        float_platforms = [
            (350, 400, 2),
            (750, 350, 3),
            (1150, 420, 2)
        ]
        
        for fx, fy, width in float_platforms:
            for i in range(width):
                tiles.append(Tile(fx + i * self.tile_size, fy, TileType.STONE_PLATFORM, 'stone'))
        
        # Alien energy fields (hazards)
        energy_positions = [300, 500, 800]
        for energy_x in energy_positions:
            tiles.append(Tile(energy_x, 580, TileType.SPIKE, 'stone'))
        
        doors.append(Door(50, 610, 64, 64, DoorType.MAGIC, "scifi_lab"))
        doors.append(Door(self.screen_width - 100, 580, 64, 64, DoorType.MAGIC, "final_sanctum"))
        
        return tiles, doors
    
    # ===== FINAL BOSS AREAS =====
    def generate_demon_throne(self) -> Tuple[List[Tile], List[Door]]:
        """Generate demon lord's throne room"""
        tiles = []
        doors = []
        
        # Throne room floor
        throne_floor_y = self.screen_height - 100
        for x in range(150, self.screen_width - 150, self.tile_size):
            tiles.append(Tile(x, throne_floor_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Elevated throne platform
        center_x = self.screen_width // 2
        throne_width = 8
        throne_height = 120
        
        for i in range(throne_width):
            x = center_x - (throne_width // 2) * self.tile_size + i * self.tile_size
            tiles.append(Tile(x, throne_floor_y - throne_height, TileType.STONE_PLATFORM, 'stone'))
            
            # Throne steps
            steps = 4
            for step in range(steps):
                step_y = throne_floor_y - (step + 1) * (throne_height // steps)
                if i >= step and i < throne_width - step:  # Narrowing steps
                    tiles.append(Tile(x, step_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Demonic pillars around the room
        pillar_positions = [200, 350, 950, 1100]
        for pillar_x in pillar_positions:
            pillar_height = 250
            for y in range(throne_floor_y - pillar_height, throne_floor_y, self.tile_size):
                tiles.append(Tile(pillar_x, y, TileType.STONE_WALL, 'stone'))
                tiles.append(Tile(pillar_x + self.tile_size, y, TileType.STONE_WALL, 'stone'))
            
            # Pillar platforms
            for x in range(pillar_x, pillar_x + self.tile_size * 2, self.tile_size):
                tiles.append(Tile(x, throne_floor_y - pillar_height - self.tile_size, TileType.STONE_PLATFORM, 'stone'))
        
        # Elevated walkways for battle
        walkway_y = throne_floor_y - 180
        walkway_sections = [
            (180, 200),  # Left side
            (920, 200)   # Right side
        ]
        
        for wx, length in walkway_sections:
            for x in range(wx, wx + length, self.tile_size):
                tiles.append(Tile(x, walkway_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Lava moats (deadly)
        for x in range(0, 150, self.tile_size):
            tiles.append(Tile(x, throne_floor_y + self.tile_size, TileType.SPIKE, 'stone'))
        for x in range(self.screen_width - 150, self.screen_width, self.tile_size):
            tiles.append(Tile(x, throne_floor_y + self.tile_size, TileType.SPIKE, 'stone'))
        
        doors.append(Door(center_x - 32, throne_floor_y - throne_height - 64, 64, 64, DoorType.MAGIC, "castle_interior"))
        doors.append(Door(center_x - 32, throne_floor_y + 32, 64, 64, DoorType.MAGIC, "final_sanctum"))
        
        return tiles, doors
    
    def generate_final_sanctum(self) -> Tuple[List[Tile], List[Door]]:
        """Generate ultimate final boss arena"""
        tiles = []
        doors = []
        
        # Arena floor (circular-ish)
        arena_center_x = self.screen_width // 2
        arena_center_y = self.screen_height - 200
        arena_radius = 200
        
        # Create circular platform
        for x in range(arena_center_x - arena_radius, arena_center_x + arena_radius, self.tile_size):
            for y in range(arena_center_y - 50, arena_center_y + 50, self.tile_size):
                distance = ((x - arena_center_x) ** 2 + (y - arena_center_y) ** 2) ** 0.5
                if distance <= arena_radius:
                    tiles.append(Tile(x, y, TileType.STONE_PLATFORM, 'stone'))
        
        # Floating ring platforms around the arena
        ring_configs = [
            (arena_center_x - 250, arena_center_y - 100, 3),
            (arena_center_x + 200, arena_center_y - 120, 3),
            (arena_center_x - 200, arena_center_y + 80, 2),
            (arena_center_x + 250, arena_center_y + 60, 2)
        ]
        
        for rx, ry, width in ring_configs:
            for i in range(width):
                tiles.append(Tile(rx + i * self.tile_size, ry, TileType.STONE_PLATFORM, 'stone'))
        
        # Central elevated platform for final confrontation
        central_platform_width = 4
        for i in range(central_platform_width):
            x = arena_center_x - (central_platform_width // 2) * self.tile_size + i * self.tile_size
            tiles.append(Tile(x, arena_center_y - 100, TileType.STONE_PLATFORM, 'stone'))
        
        # Mystical pillars at cardinal points
        pillar_distance = 150
        cardinal_positions = [
            (arena_center_x, arena_center_y - pillar_distance),  # North
            (arena_center_x + pillar_distance, arena_center_y),  # East
            (arena_center_x, arena_center_y + pillar_distance),  # South
            (arena_center_x - pillar_distance, arena_center_y)   # West
        ]
        
        for px, py in cardinal_positions:
            # Pillar base
            tiles.append(Tile(px, py, TileType.STONE_PLATFORM, 'stone'))
            # Pillar height
            for y in range(py - 160, py, self.tile_size):
                tiles.append(Tile(px, y, TileType.STONE_WALL, 'stone'))
        
        # Void around the arena (deadly)
        void_positions = [
            # Top void
            *[(x, arena_center_y - 300) for x in range(0, self.screen_width, self.tile_size)],
            # Bottom void  
            *[(x, self.screen_height - 50) for x in range(0, self.screen_width, self.tile_size)],
            # Side voids
            *[(50, y) for y in range(0, self.screen_height, self.tile_size)],
            *[(self.screen_width - 50, y) for y in range(0, self.screen_height, self.tile_size)]
        ]
        
        for vx, vy in void_positions[:20]:  # Limit to avoid too many tiles
            tiles.append(Tile(vx, vy, TileType.SPIKE, 'stone'))
        
        # Return portal (victory!)
        doors.append(Door(arena_center_x - 32, arena_center_y - 164, 64, 64, DoorType.MAGIC, "cave_depths", 100, 600))
        
        return tiles, doors
    
    def generate_level_1(self) -> Tuple[List[Tile], List[Door]]:
        """Generate level 1 with varied terrain"""
        tiles = []
        doors = []
        
        # Ground level
        ground_y = self.screen_height - 40
        for x in range(0, self.screen_width, self.tile_size):
            # Grass on top
            tiles.append(Tile(x, ground_y, TileType.GRASS_PLATFORM, 'grass'))
            # Dirt underneath
            for y in range(ground_y + self.tile_size, self.screen_height, self.tile_size):
                tiles.append(Tile(x, y, TileType.DIRT, 'dirt'))
        
        # Floating platforms with varied heights
        platform_configs = [
            (200, 500, 6, 'stone'),  # x, y, width_in_tiles, texture
            (500, 400, 4, 'stone'),
            (800, 300, 5, 'stone'),
            (1100, 200, 3, 'stone'),
        ]
        
        for px, py, width, texture in platform_configs:
            for i in range(width):
                x = px + i * self.tile_size
                tiles.append(Tile(x, py, TileType.STONE_PLATFORM, texture))
                # Add support pillars
                if i == 0 or i == width - 1:
                    for support_y in range(py + self.tile_size, ground_y, self.tile_size):
                        tiles.append(Tile(x, support_y, TileType.STONE_WALL, texture))
        
        # Add door at the end of level
        door_x = self.screen_width - 100
        door_y = ground_y - 64
        doors.append(Door(door_x, door_y, 64, 64, DoorType.WOODEN, "level_2"))
        
        return tiles, doors
    
    def generate_level_2(self) -> Tuple[List[Tile], List[Door]]:
        """Generate level 2 with more complex terrain"""
        tiles = []
        doors = []
        
        # Multi-level ground
        for x in range(0, self.screen_width // 3, self.tile_size):
            y = self.screen_height - 80
            tiles.append(Tile(x, y, TileType.STONE_PLATFORM, 'stone'))
            tiles.append(Tile(x, y + self.tile_size, TileType.DIRT, 'dirt'))
        
        for x in range(self.screen_width // 3, self.screen_width * 2 // 3, self.tile_size):
            y = self.screen_height - 120
            tiles.append(Tile(x, y, TileType.GRASS_PLATFORM, 'grass'))
            for dy in range(self.tile_size, self.screen_height - y, self.tile_size):
                tiles.append(Tile(x, y + dy, TileType.DIRT, 'dirt'))
        
        for x in range(self.screen_width * 2 // 3, self.screen_width, self.tile_size):
            y = self.screen_height - 40
            tiles.append(Tile(x, y, TileType.STONE_PLATFORM, 'stone'))
            tiles.append(Tile(x, y + self.tile_size, TileType.DIRT, 'dirt'))
        
        # Staircase pattern
        stair_configs = [
            (400, 350, 8),  # x, y, steps
            (700, 250, 6),
        ]
        
        for sx, sy, steps in stair_configs:
            for i in range(steps):
                step_x = sx + i * self.tile_size
                step_y = sy + i * self.tile_size // 2
                tiles.append(Tile(step_x, step_y, TileType.STONE_PLATFORM, 'stone'))
        
        # Door back to level 1 and forward to level 3
        doors.append(Door(50, self.screen_height - 144, 64, 64, DoorType.WOODEN, "level_1"))
        doors.append(Door(self.screen_width - 100, self.screen_height - 104, 64, 64, DoorType.IRON, "level_3"))
        
        return tiles, doors
    
    def generate_level_3(self) -> Tuple[List[Tile], List[Door]]:
        """Generate level 3 with challenging terrain"""
        tiles = []
        doors = []
        
        # Floating island theme
        island_configs = [
            (100, 500, 5, 'stone'),   # x, y, width_in_tiles, texture
            (300, 400, 4, 'grass'),
            (550, 350, 6, 'stone'),
            (850, 250, 3, 'grass'),
            (1050, 150, 4, 'stone'),
        ]
        
        for ix, iy, width, texture in island_configs:
            for i in range(width):
                x = ix + i * self.tile_size
                tiles.append(Tile(x, iy, TileType.STONE_PLATFORM, texture))
        
        # Add some scattered small platforms
        small_platforms = [
            (200, 300, 2, 'stone'),
            (450, 200, 1, 'stone'),
            (700, 100, 2, 'stone'),
            (900, 400, 1, 'grass'),
        ]
        
        for px, py, width, texture in small_platforms:
            for i in range(width):
                x = px + i * self.tile_size
                tiles.append(Tile(x, py, TileType.STONE_PLATFORM, texture))
        
        # Ground level at bottom (partial)
        ground_y = self.screen_height - 40
        for x in range(0, 200, self.tile_size):  # Left side only
            tiles.append(Tile(x, ground_y, TileType.GRASS_PLATFORM, 'grass'))
            tiles.append(Tile(x, ground_y + self.tile_size, TileType.DIRT, 'dirt'))
        
        for x in range(self.screen_width - 200, self.screen_width, self.tile_size):  # Right side only
            tiles.append(Tile(x, ground_y, TileType.STONE_PLATFORM, 'stone'))
            tiles.append(Tile(x, ground_y + self.tile_size, TileType.DIRT, 'dirt'))
        
        # Doors - back to level 2 and maybe a victory door
        doors.append(Door(50, ground_y - 64, 64, 64, DoorType.IRON, "level_2"))
        doors.append(Door(self.screen_width - 100, ground_y - 64, 64, 64, DoorType.MAGIC, "level_1", 100, 600))  # Victory loop back
        
        return tiles, doors

class EnhancedLevelManager:
    """Manages levels with terrain, textures, and doors"""
    
    def __init__(self, screen_width: int, screen_height: int, asset_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_level = "level_1"
        self.terrain_generator = TerrainGenerator(screen_width, screen_height, asset_manager)
        
        self.levels = {}
        self.generate_all_levels()
    
    def generate_all_levels(self):
        """Generate all level data using available environments"""
        # Cave levels (using existing cave backgrounds)
        self.levels["cave_depths"] = self.terrain_generator.generate_cave_depths()
        self.levels["cave_passages"] = self.terrain_generator.generate_cave_passages()
        self.levels["cave_chamber"] = self.terrain_generator.generate_cave_chamber()
        
        # Gothic environments
        self.levels["gothic_castle"] = self.terrain_generator.generate_gothic_castle()
        self.levels["castle_interior"] = self.terrain_generator.generate_castle_interior()
        self.levels["gothic_town"] = self.terrain_generator.generate_gothic_town()
        
        # Night environments
        self.levels["night_town"] = self.terrain_generator.generate_night_town()
        self.levels["haunted_forest"] = self.terrain_generator.generate_haunted_forest()
        
        # Mountain and outdoor environments
        self.levels["mountain_pass"] = self.terrain_generator.generate_mountain_pass()
        self.levels["rocky_cliffs"] = self.terrain_generator.generate_rocky_cliffs()
        
        # Underground and dangerous areas
        self.levels["lava_caverns"] = self.terrain_generator.generate_lava_caverns()
        self.levels["treasure_chamber"] = self.terrain_generator.generate_treasure_chamber()
        
        # Pixel platformer levels
        self.levels["pixel_dungeon"] = self.terrain_generator.generate_pixel_dungeon()
        self.levels["pixel_forest"] = self.terrain_generator.generate_pixel_forest()
        
        # Ocean and water levels
        self.levels["underwater_ruins"] = self.terrain_generator.generate_underwater_ruins()
        self.levels["ocean_depths"] = self.terrain_generator.generate_ocean_depths()
        
        # Sci-fi environments
        self.levels["scifi_lab"] = self.terrain_generator.generate_scifi_lab()
        self.levels["alien_world"] = self.terrain_generator.generate_alien_world()
        
        # Final boss areas
        self.levels["demon_throne"] = self.terrain_generator.generate_demon_throne()
        self.levels["final_sanctum"] = self.terrain_generator.generate_final_sanctum()
        
        # Keep original levels for compatibility
        self.levels["level_1"] = self.terrain_generator.generate_cave_depths()  # Redirect to cave_depths
        self.levels["level_2"] = self.terrain_generator.generate_gothic_castle()  # Redirect to gothic_castle
        self.levels["level_3"] = self.terrain_generator.generate_demon_throne()  # Redirect to demon_throne
    
    def get_current_level_tiles(self) -> List[Tile]:
        """Get tiles for current level"""
        if self.current_level in self.levels:
            return self.levels[self.current_level][0]
        return []
    
    def get_current_level_doors(self) -> List[Door]:
        """Get doors for current level"""
        if self.current_level in self.levels:
            return self.levels[self.current_level][1]
        return []
    
    def get_collision_rects(self) -> List[pygame.Rect]:
        """Get collision rectangles for current level"""
        collision_rects = []
        tiles = self.get_current_level_tiles()
        
        for tile in tiles:
            if tile.collision:
                collision_rects.append(pygame.Rect(tile.x, tile.y, 
                                                  self.terrain_generator.tile_size, 
                                                  self.terrain_generator.tile_size))
        return collision_rects
    
    def check_door_collision(self, player_rect: pygame.Rect) -> Optional[Door]:
        """Check if player is colliding with any doors"""
        doors = self.get_current_level_doors()
        for door in doors:
            door_rect = pygame.Rect(door.x, door.y, door.width, door.height)
            if player_rect.colliderect(door_rect):
                return door
        return None
    
    def switch_level(self, target_level: str, player_x: int = None, player_y: int = None):
        """Switch to target level"""
        if target_level in self.levels:
            self.current_level = target_level
            return True
        return False
    
    def draw_level(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """Draw current level with textures"""
        tiles = self.get_current_level_tiles()
        doors = self.get_current_level_doors()
        
        # Draw tiles
        for tile in tiles:
            tile_x = tile.x - camera_x
            tile_y = tile.y - camera_y
            
            # Only draw visible tiles
            if (-32 <= tile_x <= self.screen_width and 
                -32 <= tile_y <= self.screen_height):
                
                if tile.texture_id in self.terrain_generator.textures:
                    texture = self.terrain_generator.textures[tile.texture_id]
                    screen.blit(texture, (tile_x, tile_y))
                else:
                    # Fallback color based on tile type
                    color = self.get_tile_color(tile.tile_type)
                    pygame.draw.rect(screen, color, 
                                   (tile_x, tile_y, 
                                    self.terrain_generator.tile_size, 
                                    self.terrain_generator.tile_size))
        
        # Draw doors
        for door in doors:
            door_x = door.x - camera_x
            door_y = door.y - camera_y
            
            if (-64 <= door_x <= self.screen_width and 
                -64 <= door_y <= self.screen_height):
                
                if 'door' in self.terrain_generator.textures:
                    door_texture = self.terrain_generator.textures['door']
                    screen.blit(door_texture, (door_x, door_y))
                else:
                    # Fallback door drawing
                    pygame.draw.rect(screen, (139, 69, 19), 
                                   (door_x, door_y, door.width, door.height))
                    pygame.draw.rect(screen, (101, 67, 33), 
                                   (door_x, door_y, door.width, door.height), 3)
                
                # Draw door interaction hint
                if door.door_type == DoorType.WOODEN:
                    hint_color = (255, 255, 255)
                elif door.door_type == DoorType.IRON:
                    hint_color = (200, 200, 200)
                else:
                    hint_color = (255, 100, 255)
                
                font = pygame.font.Font(None, 24)
                hint_text = font.render("E", True, hint_color)
                screen.blit(hint_text, (door_x + door.width // 2 - 5, door_y - 25))
    
    def get_tile_color(self, tile_type: TileType) -> Tuple[int, int, int]:
        """Get fallback color for tile type"""
        color_map = {
            TileType.STONE_PLATFORM: (100, 100, 120),
            TileType.STONE_WALL: (80, 80, 100),
            TileType.GRASS_PLATFORM: (50, 120, 30),
            TileType.DIRT: (80, 50, 30),
            TileType.SPIKE: (200, 0, 0),
            TileType.DECORATION: (150, 150, 150),
        }
        return color_map.get(tile_type, (128, 128, 128))

class PerformanceOptimizer:
    """Optimizes game performance for smooth 60fps"""
    
    def __init__(self):
        self.frame_times = []
        self.max_frame_samples = 60
        self.target_fps = 60
        self.vsync_enabled = True
    
    def update_frame_time(self, dt: float):
        """Track frame times for performance monitoring"""
        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_frame_samples:
            self.frame_times.pop(0)
    
    def get_average_fps(self) -> float:
        """Get average FPS over recent frames"""
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        if avg_frame_time > 0:
            return 1000.0 / avg_frame_time  # Convert ms to FPS
        return 0
    
    def should_skip_frame(self) -> bool:
        """Determine if frame should be skipped for performance"""
        if len(self.frame_times) < 10:
            return False
        
        recent_avg = sum(self.frame_times[-10:]) / 10
        return recent_avg > (1000.0 / self.target_fps) * 1.5
    
    def optimize_surfaces(self, surfaces: List[pygame.Surface]) -> List[pygame.Surface]:
        """Convert surfaces to display format for better performance"""
        optimized = []
        for surface in surfaces:
            if surface.get_alpha() is not None or surface.get_colorkey() is not None:
                optimized.append(surface.convert_alpha())
            else:
                optimized.append(surface.convert())
        return optimized

def main():
    """Test the enhanced level system"""
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Enhanced Level System Test")
    clock = pygame.time.Clock()
    
    level_manager = EnhancedLevelManager(1280, 720)
    performance = PerformanceOptimizer()
    
    # Test player rectangle for door collision
    player_rect = pygame.Rect(100, 600, 64, 80)
    camera_x, camera_y = 0, 0
    
    running = True
    while running:
        dt = clock.tick(60)
        performance.update_frame_time(dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    level_manager.switch_level("level_1")
                elif event.key == pygame.K_2:
                    level_manager.switch_level("level_2")
                elif event.key == pygame.K_e:
                    # Test door collision
                    door = level_manager.check_door_collision(player_rect)
                    if door:
                        print(f"Switching to {door.target_level}")
                        level_manager.switch_level(door.target_level)
                        player_rect.x = door.target_x
                        player_rect.y = door.target_y
        
        # Simple player movement for testing
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= 5
        if keys[pygame.K_RIGHT]:
            player_rect.x += 5
        
        # Clear screen
        screen.fill((20, 20, 30))
        
        # Draw level
        level_manager.draw_level(screen, camera_x, camera_y)
        
        # Draw player (simple rectangle)
        pygame.draw.rect(screen, (255, 100, 100), 
                        (player_rect.x - camera_x, player_rect.y - camera_y, 
                         player_rect.width, player_rect.height))
        
        # Draw performance info
        fps = performance.get_average_fps()
        font = pygame.font.Font(None, 36)
        fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))
        
        level_text = font.render(f"Level: {level_manager.current_level}", True, (255, 255, 255))
        screen.blit(level_text, (10, 50))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
