#!/usr/bin/env python3
"""
Reserka Gothic - World Map Integration
Connects the advanced world map system with the lightweight game
"""

import pygame
from typing import Dict, List, Optional, Set, Tuple
from world_map_system import WorldMapSystem, GateType, AreaType
from metroidvania_camera import CameraConstraints

class WorldMapIntegration:
    """Integrates the world map system with the game"""
    
    def __init__(self, game_instance, world_map: WorldMapSystem):
        self.game = game_instance
        self.world_map = world_map
        
        # Track collected items and defeated bosses
        self.collected_power_ups: Set[str] = set()
        self.defeated_bosses: Set[str] = set()
        self.discovered_secrets: Set[str] = set()
        
        # UI components
        self.map_display_enabled = False
        self.show_minimap = True
        
        print("🔗 World Map Integration initialized!")
        print("   Press 'M' in-game to toggle world map")
        print("   Press 'TAB' to toggle minimap")
    
    def sync_player_abilities(self, player):
        """Sync player abilities with world map gates"""
        # Movement abilities
        if hasattr(player, 'max_jumps') and player.max_jumps >= 2:
            self.world_map.gain_ability(GateType.DOUBLE_JUMP)
        
        if hasattr(player, 'abilities') and player.abilities.get('dash_available'):
            self.world_map.gain_ability(GateType.DASH)
        
        # Environmental abilities based on collected power-ups
        if 'water_breathing_apparatus' in self.collected_power_ups:
            self.world_map.gain_ability(GateType.WATER_BREATHING)
        
        if 'fire_immunity_charm' in self.collected_power_ups:
            self.world_map.gain_ability(GateType.FIRE_IMMUNITY)
        
        if 'crystal_power' in self.collected_power_ups:
            self.world_map.gain_ability(GateType.CRYSTAL_POWER)
        
        # Combat abilities
        if 'heavy_gauntlets' in self.collected_power_ups:
            self.world_map.gain_ability(GateType.HEAVY_ATTACK)
        
        if 'ranged_attack_upgrade' in self.collected_power_ups:
            self.world_map.gain_ability(GateType.RANGED_ATTACK)
        
        # Keys
        if 'red_keycard' in self.collected_power_ups:
            self.world_map.gain_ability(GateType.RED_KEY)
        
        if 'blue_keycard' in self.collected_power_ups:
            self.world_map.gain_ability(GateType.BLUE_KEY)
        
        # Boss progression
        if 'demon_lord_boss' in self.defeated_bosses:
            self.world_map.gain_ability(GateType.BOSS_1_DEFEATED)
        
        if 'ancient_dragon_boss' in self.defeated_bosses:
            self.world_map.gain_ability(GateType.BOSS_2_DEFEATED)
    
    def on_power_up_collected(self, power_up_id: str, player):
        """Handle power-up collection"""
        if power_up_id not in self.collected_power_ups:
            self.collected_power_ups.add(power_up_id)
            print(f"💎 Collected power-up: {power_up_id}")
            
            # Sync abilities after collection
            self.sync_player_abilities(player)
            
            # Show progression hint
            self.show_progression_hint(power_up_id)
    
    def on_boss_defeated(self, boss_id: str, player):
        """Handle boss defeat"""
        if boss_id not in self.defeated_bosses:
            self.defeated_bosses.add(boss_id)
            print(f"👹 Defeated boss: {boss_id}")
            
            # Sync abilities after boss defeat
            self.sync_player_abilities(player)
            
            # Show new areas unlocked
            self.show_new_areas_unlocked()
    
    def on_area_transition(self, from_area: str, to_area: str):
        """Handle area transition"""
        if to_area in self.world_map.areas:
            self.world_map.visit_area(to_area)
            
            # Check for story triggers
            area = self.world_map.areas[to_area]
            if area.story_triggers:
                print(f"🎬 Story events triggered in {area.display_name}")
    
    def get_camera_constraints_for_area(self, area_id: str) -> CameraConstraints:
        """Get camera constraints for the current area"""
        if area_id in self.world_map.areas:
            area = self.world_map.areas[area_id]
            min_x, max_x, min_y, max_y = area.camera_constraints
            return CameraConstraints(min_x, max_x, min_y, max_y)
        
        # Fallback constraints
        return CameraConstraints()
    
    def get_available_transitions(self, current_area: str) -> List[Dict]:
        """Get available area transitions from current location"""
        accessible_areas = self.world_map.get_accessible_areas(current_area)
        transitions = []
        
        if current_area in self.world_map.areas:
            area = self.world_map.areas[current_area]
            for connection_id, connection in area.connections.items():
                if connection.target_area in accessible_areas:
                    transitions.append({
                        'target_area': connection.target_area,
                        'display_name': self.world_map.areas[connection.target_area].display_name,
                        'description': connection.description,
                        'connection_type': connection.connection_type,
                        'is_shortcut': connection.is_shortcut
                    })
        
        return transitions
    
    def show_progression_hint(self, power_up_id: str):
        """Show hint about what this power-up unlocks"""
        hints = {
            'crystal_power': "✨ Crystal power resonates... hidden passages may reveal themselves.",
            'water_breathing_apparatus': "🫧 The depths no longer hold their breath from you.",
            'heavy_gauntlets': "💪 Heavy strikes may break through what seemed unbreakable.",
            'dash_boots': "💨 Swift movement opens new paths through the world.",
            'red_keycard': "🔴 Industrial areas await your access.",
            'blue_keycard': "🔵 The castle's deeper secrets can now be explored.",
            'ancient_rune_tablet': "📜 Ancient knowledge reveals mystical barriers.",
            'void_resistance': "🌌 The void no longer drains your essence.",
        }
        
        if power_up_id in hints:
            print(f"💡 {hints[power_up_id]}")
    
    def show_new_areas_unlocked(self):
        """Show newly accessible areas"""
        completion = self.world_map.get_world_completion()
        accessible_areas = []
        
        for area_id, area in self.world_map.areas.items():
            if (area_id not in self.world_map.visited_areas and 
                self.world_map.can_access_area(area_id)):
                accessible_areas.append(area.display_name)
        
        if accessible_areas:
            print(f"🗺️ New areas unlocked: {', '.join(accessible_areas)}")
    
    def draw_minimap(self, screen: pygame.Surface, player_pos: Tuple[int, int]):
        """Draw a simple minimap"""
        if not self.show_minimap:
            return
        
        minimap_size = (200, 150)
        minimap_pos = (screen.get_width() - minimap_size[0] - 20, 20)
        
        # Create minimap surface
        minimap = pygame.Surface(minimap_size, pygame.SRCALPHA)
        minimap.fill((0, 0, 0, 128))  # Semi-transparent black
        
        current_area = self.world_map.areas[self.world_map.current_area]
        
        # Draw current area bounds
        pygame.draw.rect(minimap, (100, 100, 100), (5, 5, minimap_size[0]-10, minimap_size[1]-10), 2)
        
        # Draw player position as a dot
        area_width, area_height = current_area.size
        player_x_ratio = player_pos[0] / area_width if area_width > 0 else 0.5
        player_y_ratio = player_pos[1] / area_height if area_height > 0 else 0.5
        
        minimap_player_x = int(5 + (minimap_size[0] - 10) * player_x_ratio)
        minimap_player_y = int(5 + (minimap_size[1] - 10) * player_y_ratio)
        
        pygame.draw.circle(minimap, (255, 255, 0), (minimap_player_x, minimap_player_y), 3)
        
        # Draw connections as arrows
        accessible_areas = self.world_map.get_accessible_areas()
        connection_color = (0, 255, 0)  # Green for accessible
        blocked_color = (255, 0, 0)     # Red for blocked
        
        # Draw area name
        font = pygame.font.Font(None, 24)
        area_text = font.render(current_area.display_name, True, (255, 255, 255))
        minimap.blit(area_text, (10, minimap_size[1] - 25))
        
        screen.blit(minimap, minimap_pos)
    
    def draw_world_map_overlay(self, screen: pygame.Surface):
        """Draw full world map overlay"""
        if not self.map_display_enabled:
            return
        
        # Create overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Dark semi-transparent background
        
        # Map dimensions
        map_width = screen.get_width() - 100
        map_height = screen.get_height() - 100
        map_x = 50
        map_y = 50
        
        # Draw map background
        pygame.draw.rect(overlay, (40, 40, 60), (map_x, map_y, map_width, map_height))
        pygame.draw.rect(overlay, (255, 255, 255), (map_x, map_y, map_width, map_height), 3)
        
        # Title
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        title = font_large.render("RESERKA GOTHIC - WORLD MAP", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=screen.get_width()//2, y=map_y + 20)
        overlay.blit(title, title_rect)
        
        # Draw areas in a grid layout
        areas_per_row = 4
        area_width = (map_width - 40) // areas_per_row
        area_height = 80
        
        row = 0
        col = 0
        
        # Group areas by type
        areas_by_type = {}
        for area in self.world_map.areas.values():
            area_type = area.area_type
            if area_type not in areas_by_type:
                areas_by_type[area_type] = []
            areas_by_type[area_type].append(area)
        
        y_offset = map_y + 80
        
        for area_type, areas_list in areas_by_type.items():
            # Type header
            type_text = font_medium.render(f"{area_type.value.upper()} AREAS", True, (255, 215, 0))
            overlay.blit(type_text, (map_x + 20, y_offset))
            y_offset += 35
            
            col = 0
            for area in areas_list:
                area_x = map_x + 20 + (col * (area_width + 10))
                area_y = y_offset
                
                # Area box
                area_visited = area.id in self.world_map.visited_areas
                area_current = area.id == self.world_map.current_area
                
                if area_current:
                    area_color = (255, 215, 0)  # Gold for current
                elif area_visited:
                    area_color = (100, 255, 100)  # Green for visited
                else:
                    area_color = (100, 100, 100)  # Gray for unvisited
                
                pygame.draw.rect(overlay, area_color, (area_x, area_y, area_width-5, area_height-5), 2)
                
                # Area name
                area_name = font_small.render(area.display_name, True, (255, 255, 255))
                name_rect = area_name.get_rect(centerx=area_x + area_width//2, y=area_y + 10)
                overlay.blit(area_name, name_rect)
                
                # Area info
                info_lines = [
                    f"Size: {area.size[0]}x{area.size[1]}",
                    f"Connections: {len(area.connections)}",
                    f"Secrets: {len(area.secrets)}"
                ]
                
                for i, line in enumerate(info_lines):
                    info_text = font_small.render(line, True, (200, 200, 200))
                    overlay.blit(info_text, (area_x + 5, area_y + 30 + i * 15))
                
                col += 1
                if col >= areas_per_row:
                    col = 0
                    y_offset += area_height + 10
            
            if col > 0:  # If we have areas in the current row
                y_offset += area_height + 20
            else:
                y_offset += 10
        
        # Completion stats
        completion = self.world_map.get_world_completion()
        stats_y = map_y + map_height - 60
        
        stats_lines = [
            f"Exploration: {completion['area_completion']:.1f}%",
            f"Areas: {completion['visited_areas']}/{completion['total_areas']}",
            f"Abilities: {completion['abilities_found']}"
        ]
        
        for i, line in enumerate(stats_lines):
            stats_text = font_medium.render(line, True, (255, 255, 255))
            overlay.blit(stats_text, (map_x + 20 + i * 200, stats_y))
        
        # Instructions
        instruction_text = font_small.render("Press 'M' to close map | Press 'TAB' to toggle minimap", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(centerx=screen.get_width()//2, y=map_y + map_height - 30)
        overlay.blit(instruction_text, instruction_rect)
        
        screen.blit(overlay, (0, 0))
    
    def handle_input(self, event):
        """Handle input for world map features"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.map_display_enabled = not self.map_display_enabled
                print(f"🗺️ World map {'enabled' if self.map_display_enabled else 'disabled'}")
            elif event.key == pygame.K_TAB:
                self.show_minimap = not self.show_minimap
                print(f"🧭 Minimap {'enabled' if self.show_minimap else 'disabled'}")
    
    def get_world_completion_percentage(self) -> float:
        """Get overall world completion percentage"""
        completion = self.world_map.get_world_completion()
        
        # Weight different completion aspects
        area_weight = 0.4
        powerup_weight = 0.4 
        secret_weight = 0.2
        
        total_completion = (
            completion['area_completion'] * area_weight +
            completion['powerup_completion'] * powerup_weight +
            completion['secret_completion'] * secret_weight
        )
        
        return min(100.0, total_completion)
    
    def save_integration_state(self, filepath: str):
        """Save integration state"""
        state = {
            'collected_power_ups': list(self.collected_power_ups),
            'defeated_bosses': list(self.defeated_bosses),
            'discovered_secrets': list(self.discovered_secrets)
        }
        
        import json
        with open(filepath.replace('.json', '_integration.json'), 'w') as f:
            json.dump(state, f, indent=2)
        
        # Also save world map state
        self.world_map.save_world_state(filepath)
    
    def load_integration_state(self, filepath: str):
        """Load integration state"""
        try:
            import json
            with open(filepath.replace('.json', '_integration.json'), 'r') as f:
                state = json.load(f)
            
            self.collected_power_ups = set(state.get('collected_power_ups', []))
            self.defeated_bosses = set(state.get('defeated_bosses', []))
            self.discovered_secrets = set(state.get('discovered_secrets', []))
            
            # Load world map state
            return self.world_map.load_world_state(filepath)
        except Exception as e:
            print(f"❌ Failed to load integration state: {e}")
            return False


def create_world_map_integration(game_instance):
    """Factory function to create world map integration"""
    world_map = WorldMapSystem()
    integration = WorldMapIntegration(game_instance, world_map)
    return integration


# Example usage with the lightweight game
if __name__ == "__main__":
    print("🎮 World Map Integration Demo")
    print("This system connects the advanced world map with your game!")
    
    # Create mock game instance
    class MockGame:
        def __init__(self):
            self.current_level = "ancient_caverns"
    
    mock_game = MockGame()
    integration = create_world_map_integration(mock_game)
    
    # Simulate gameplay events
    print("\n🎯 Simulating gameplay events...")
    
    # Mock player with abilities
    class MockPlayer:
        def __init__(self):
            self.max_jumps = 2
            self.abilities = {'dash_available': True}
    
    player = MockPlayer()
    
    # Simulate collecting power-ups
    integration.on_power_up_collected('crystal_power', player)
    integration.on_power_up_collected('heavy_gauntlets', player)
    integration.on_power_up_collected('red_keycard', player)
    
    # Simulate boss defeat
    integration.on_boss_defeated('demon_lord_boss', player)
    
    # Show completion
    completion = integration.get_world_completion_percentage()
    print(f"\n📊 Overall completion: {completion:.1f}%")
    
    print("\n✅ World Map Integration ready for game integration!")
