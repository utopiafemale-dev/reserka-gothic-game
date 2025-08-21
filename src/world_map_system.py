#!/usr/bin/env python3
"""
Reserka Gothic - Complete World Map System
Advanced Metroidvania world design with interconnected areas and progression gates
"""

import pygame
import json
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

class AreaType(Enum):
    STARTING_AREA = "starting"
    MAIN_PATH = "main"
    OPTIONAL = "optional"
    SECRET = "secret"
    BOSS_AREA = "boss"
    HUB_AREA = "hub"
    LATE_GAME = "late_game"
    FINAL_AREA = "final"

class GateType(Enum):
    # Movement abilities
    DOUBLE_JUMP = "double_jump"
    WALL_JUMP = "wall_jump"
    DASH = "dash"
    AIR_DASH = "air_dash"
    GROUND_POUND = "ground_pound"
    
    # Environmental abilities  
    FIRE_IMMUNITY = "fire_immunity"
    ICE_IMMUNITY = "ice_immunity"
    ACID_IMMUNITY = "acid_immunity"
    WATER_BREATHING = "water_breathing"
    
    # Combat abilities
    HEAVY_ATTACK = "heavy_attack"
    RANGED_ATTACK = "ranged_attack"
    MAGIC_ATTACK = "magic_attack"
    
    # Keys and switches
    RED_KEY = "red_key"
    BLUE_KEY = "blue_key"
    GOLD_KEY = "gold_key"
    MASTER_KEY = "master_key"
    
    # Story progression
    BOSS_1_DEFEATED = "boss_1_defeated"
    BOSS_2_DEFEATED = "boss_2_defeated"
    BOSS_3_DEFEATED = "boss_3_defeated"
    FINAL_BOSS_ACCESS = "final_boss_access"
    
    # Special gates
    CRYSTAL_POWER = "crystal_power"
    ANCIENT_RUNE = "ancient_rune"
    DEMON_PACT = "demon_pact"
    VOID_RESISTANCE = "void_resistance"

@dataclass
class Connection:
    """Represents a connection between two areas"""
    target_area: str
    gate_requirements: List[GateType] = field(default_factory=list)
    is_hidden: bool = False  # Secret passages
    is_shortcut: bool = False  # Unlocked after first visit
    connection_type: str = "door"  # door, elevator, teleporter, etc.
    description: str = ""
    
    def is_accessible(self, player_abilities: Set[GateType]) -> bool:
        """Check if player can access this connection"""
        if not self.gate_requirements:
            return True
        return all(req in player_abilities for req in self.gate_requirements)

@dataclass
class WorldArea:
    """Represents a complete area in the game world"""
    id: str
    name: str
    display_name: str
    area_type: AreaType
    size: Tuple[int, int]  # Width, height in pixels
    
    # Visual properties
    background_theme: str
    tileset_theme: str
    music_track: str
    ambient_sound: str = ""
    
    # Connections to other areas
    connections: Dict[str, Connection] = field(default_factory=dict)
    
    # Content in this area
    enemies: List[str] = field(default_factory=list)
    power_ups: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    save_points: int = 1
    
    # Story and lore
    lore_items: List[str] = field(default_factory=list)
    story_triggers: List[str] = field(default_factory=list)
    
    # Technical properties
    camera_constraints: Tuple[int, int, int, int] = (0, 0, 0, 0)  # min_x, max_x, min_y, max_y
    visited: bool = False
    completion_percentage: float = 0.0

class WorldMapSystem:
    """Complete world map system for Metroidvania gameplay"""
    
    def __init__(self):
        self.areas: Dict[str, WorldArea] = {}
        self.current_area = "ancient_caverns"  # Starting area
        self.player_abilities: Set[GateType] = set()
        self.visited_areas: Set[str] = set()
        self.discovered_shortcuts: Set[str] = set()
        
        # Initialize the complete world
        self._create_world_map()
        
        print("🗺️ Complete World Map System initialized!")
        print(f"   📍 {len(self.areas)} areas created")
        print(f"   🔗 {sum(len(area.connections) for area in self.areas.values())} connections")
        print(f"   🎯 Starting area: {self.areas[self.current_area].display_name}")
    
    def _create_world_map(self):
        """Create the complete interconnected world map"""
        
        # =================== STARTING AREAS ===================
        
        # 1. Ancient Caverns (Tutorial/Starting area)
        self.areas["ancient_caverns"] = WorldArea(
            id="ancient_caverns",
            name="ancient_caverns", 
            display_name="Ancient Caverns",
            area_type=AreaType.STARTING_AREA,
            size=(2560, 720),
            background_theme="cave_bg_1",
            tileset_theme="cave_basic",
            music_track="cavern_depths",
            connections={
                "crystal_caves": Connection("crystal_caves", description="Mysterious glowing passage"),
                "abandoned_mines": Connection("abandoned_mines", [GateType.DOUBLE_JUMP], 
                                            description="High ledge requiring enhanced jumping"),
            },
            enemies=["fire_skull", "cave_bat"],
            power_ups=["health_tank_1", "energy_tank_1"],
            save_points=2,
            camera_constraints=(0, 2560, 0, 720)
        )
        
        # 2. Crystal Caves (Early exploration)
        self.areas["crystal_caves"] = WorldArea(
            id="crystal_caves",
            name="crystal_caves",
            display_name="Crystal Caves", 
            area_type=AreaType.MAIN_PATH,
            size=(3840, 1440),
            background_theme="crystal_cave_bg",
            tileset_theme="crystal_tileset",
            music_track="crystal_resonance",
            connections={
                "ancient_caverns": Connection("ancient_caverns", description="Return to starting caves"),
                "underground_lake": Connection("underground_lake", description="Deeper into the earth"),
                "forgotten_shrine": Connection("forgotten_shrine", [GateType.CRYSTAL_POWER], is_hidden=True,
                                              description="Hidden passage revealed by crystal power"),
            },
            enemies=["crystal_spider", "gem_guardian"],
            power_ups=["crystal_power", "wall_jump_boots"],
            secrets=["crystal_heart_fragment_1"],
            save_points=2,
            camera_constraints=(0, 3840, 0, 1440)
        )
        
        # =================== MAIN PROGRESSION AREAS ===================
        
        # 3. Underground Lake (First major area)
        self.areas["underground_lake"] = WorldArea(
            id="underground_lake",
            name="underground_lake",
            display_name="Underground Lake",
            area_type=AreaType.MAIN_PATH,
            size=(4096, 1800),
            background_theme="underground_water",
            tileset_theme="water_cave",
            music_track="depths_of_sorrow",
            ambient_sound="water_dripping",
            connections={
                "crystal_caves": Connection("crystal_caves", description="Back to crystal formations"),
                "sunken_ruins": Connection("sunken_ruins", [GateType.WATER_BREATHING], 
                                          description="Submerged passage requires water breathing"),
                "flooded_tunnels": Connection("flooded_tunnels", description="Partially flooded caverns"),
                "ancient_bridge": Connection("ancient_bridge", [GateType.WALL_JUMP], 
                                           description="Ancient stone bridge high above"),
            },
            enemies=["aquatic_horror", "drowned_soul", "water_elemental"],
            power_ups=["water_breathing_apparatus", "health_tank_2"],
            lore_items=["ancient_tablet_1", "drowned_explorer_log"],
            save_points=3,
            camera_constraints=(0, 4096, 0, 1800)
        )
        
        # 4. Abandoned Mines (Vertical exploration)
        self.areas["abandoned_mines"] = WorldArea(
            id="abandoned_mines",
            name="abandoned_mines", 
            display_name="Abandoned Mines",
            area_type=AreaType.MAIN_PATH,
            size=(2880, 2160),
            background_theme="mine_shaft",
            tileset_theme="industrial_decay",
            music_track="industrial_decay",
            ambient_sound="machinery_distant",
            connections={
                "ancient_caverns": Connection("ancient_caverns", description="Back to the caverns"),
                "mining_depths": Connection("mining_depths", description="Deeper mine shafts"),
                "surface_ruins": Connection("surface_ruins", [GateType.DASH, GateType.DOUBLE_JUMP],
                                           description="Long-abandoned elevator shaft"),
                "ore_processing": Connection("ore_processing", [GateType.RED_KEY],
                                           description="Locked industrial area"),
            },
            enemies=["mining_robot", "cave_troll", "toxic_slime"],
            power_ups=["dash_boots", "red_keycard", "energy_tank_2"],
            secrets=["hidden_ore_cache", "miner_ghost_encounter"],
            save_points=2,
            camera_constraints=(0, 2880, 0, 2160)
        )
        
        # =================== MID-GAME AREAS ===================
        
        # 5. Gothic Castle (Major hub area)
        self.areas["gothic_castle"] = WorldArea(
            id="gothic_castle",
            name="gothic_castle",
            display_name="Gothic Castle",
            area_type=AreaType.HUB_AREA,
            size=(5120, 2880),
            background_theme="castle_interior",
            tileset_theme="gothic_stone",
            music_track="castle_of_shadows",
            connections={
                "castle_entrance": Connection("castle_entrance", description="Grand entrance hall"),
                "throne_room": Connection("throne_room", [GateType.BOSS_1_DEFEATED],
                                         description="Sealed throne room"),
                "castle_tower": Connection("castle_tower", [GateType.DOUBLE_JUMP, GateType.WALL_JUMP],
                                          description="Ancient tower spire"),
                "castle_dungeons": Connection("castle_dungeons", [GateType.BLUE_KEY],
                                             description="Locked dungeon entrance"),
                "secret_passages": Connection("secret_passages", [GateType.HEAVY_ATTACK], is_hidden=True,
                                             description="Hidden wall, destructible"),
                "courtyard": Connection("courtyard", description="Castle grounds"),
            },
            enemies=["skeleton_knight", "ghost_maiden", "armored_sentinel"],
            power_ups=["heavy_gauntlets", "blue_keycard", "health_tank_3"],
            lore_items=["castle_history", "lord_diary_1", "ancient_portrait"],
            story_triggers=["castle_arrival_cutscene"],
            save_points=4,
            camera_constraints=(0, 5120, 0, 2880)
        )
        
        # 6. Haunted Forest (Atmospheric area)
        self.areas["haunted_forest"] = WorldArea(
            id="haunted_forest",
            name="haunted_forest",
            display_name="Haunted Forest", 
            area_type=AreaType.MAIN_PATH,
            size=(4800, 1440),
            background_theme="dark_forest",
            tileset_theme="twisted_trees",
            music_track="whispers_in_darkness",
            ambient_sound="wind_through_trees",
            connections={
                "surface_ruins": Connection("surface_ruins", description="Forest edge near ruins"),
                "witch_hut": Connection("witch_hut", [GateType.ANCIENT_RUNE], 
                                       description="Mystical barrier requires ancient knowledge"),
                "dark_grove": Connection("dark_grove", description="Heart of the cursed forest"),
                "cemetery": Connection("cemetery", description="Old graveyard"),
                "moonlight_clearing": Connection("moonlight_clearing", is_hidden=True,
                                                description="Secret moonlit sanctuary"),
            },
            enemies=["shadow_wolf", "cursed_treant", "will_o_wisp"],
            power_ups=["ancient_rune_tablet", "fire_immunity_charm"],
            secrets=["witch_blessing", "moonlight_crystal"],
            lore_items=["forest_legend", "witch_prophecy"],
            save_points=3,
            camera_constraints=(0, 4800, 0, 1440)
        )
        
        # =================== BOSS AREAS ===================
        
        # 7. Demon Lord Chamber (First major boss)
        self.areas["demon_lord_chamber"] = WorldArea(
            id="demon_lord_chamber",
            name="demon_lord_chamber",
            display_name="Demon Lord's Chamber",
            area_type=AreaType.BOSS_AREA,
            size=(1920, 1080),
            background_theme="hellish_chamber",
            tileset_theme="demonic_architecture", 
            music_track="demon_lord_battle",
            connections={
                "castle_dungeons": Connection("castle_dungeons", description="Escape from the depths"),
                "hell_gates": Connection("hell_gates", [GateType.BOSS_1_DEFEATED, GateType.DEMON_PACT],
                                        description="Passage to the underworld"),
            },
            enemies=["demon_lord_boss"],
            power_ups=["demon_pact_seal", "health_tank_4"],
            story_triggers=["demon_lord_encounter", "demon_pact_choice"],
            save_points=1,
            camera_constraints=(0, 1920, 0, 1080)
        )
        
        # 8. Ancient Dragon Lair (Second major boss)
        self.areas["ancient_dragon_lair"] = WorldArea(
            id="ancient_dragon_lair", 
            name="ancient_dragon_lair",
            display_name="Ancient Dragon's Lair",
            area_type=AreaType.BOSS_AREA,
            size=(2560, 1440),
            background_theme="dragon_cave",
            tileset_theme="scorched_stone",
            music_track="ancient_dragon_theme",
            ambient_sound="dragon_breathing",
            connections={
                "volcanic_depths": Connection("volcanic_depths", description="Deeper into the volcano"),
                "dragon_hoard": Connection("dragon_hoard", [GateType.BOSS_2_DEFEATED],
                                          description="The dragon's treasure chamber"),
            },
            enemies=["ancient_dragon_boss"],
            power_ups=["dragon_scale_armor", "fire_immunity_upgrade"],
            lore_items=["dragon_history", "ancient_prophecy"],
            story_triggers=["dragon_encounter", "dragon_bargain"],
            save_points=1,
            camera_constraints=(0, 2560, 0, 1440)
        )
        
        # =================== LATE GAME AREAS ===================
        
        # 9. Void Realm (Late game challenge)
        self.areas["void_realm"] = WorldArea(
            id="void_realm",
            name="void_realm", 
            display_name="Void Realm",
            area_type=AreaType.LATE_GAME,
            size=(6400, 3600),
            background_theme="cosmic_void",
            tileset_theme="ethereal_platforms",
            music_track="void_whispers",
            connections={
                "reality_anchor": Connection("reality_anchor", [GateType.CRYSTAL_POWER, GateType.ANCIENT_RUNE],
                                           description="Mystical gateway"),
                "shadow_maze": Connection("shadow_maze", [GateType.AIR_DASH],
                                         description="Labyrinth of shadows"),
                "final_sanctum": Connection("final_sanctum", [GateType.BOSS_1_DEFEATED, GateType.BOSS_2_DEFEATED],
                                           description="Path to the final confrontation"),
            },
            enemies=["void_wraith", "shadow_clone", "reality_distortion"],
            power_ups=["air_dash_upgrade", "void_resistance", "master_key"],
            secrets=["void_heart_fragment", "reality_crystal"],
            save_points=4,
            camera_constraints=(0, 6400, 0, 3600)
        )
        
        # 10. Final Sanctum (Final boss area)
        self.areas["final_sanctum"] = WorldArea(
            id="final_sanctum",
            name="final_sanctum",
            display_name="Final Sanctum", 
            area_type=AreaType.FINAL_AREA,
            size=(2048, 1152),
            background_theme="final_chamber",
            tileset_theme="ancient_technology",
            music_track="final_confrontation",
            connections={
                "void_realm": Connection("void_realm", description="Return to the void"),
                "ending_chamber": Connection("ending_chamber", [GateType.BOSS_3_DEFEATED],
                                           description="The truth awaits"),
            },
            enemies=["final_boss", "shadow_self"],
            story_triggers=["final_revelation", "ending_choice"],
            save_points=1,
            camera_constraints=(0, 2048, 0, 1152)
        )
        
        # =================== SECRET & OPTIONAL AREAS ===================
        
        # 11. Forgotten Shrine (Secret ability area)
        self.areas["forgotten_shrine"] = WorldArea(
            id="forgotten_shrine",
            name="forgotten_shrine",
            display_name="Forgotten Shrine",
            area_type=AreaType.SECRET,
            size=(1600, 900),
            background_theme="mystical_shrine", 
            tileset_theme="ancient_runes",
            music_track="mystical_sanctuary",
            connections={
                "crystal_caves": Connection("crystal_caves", description="Hidden return passage"),
            },
            power_ups=["ground_pound_ability", "magic_attack_scroll"],
            secrets=["shrine_blessing", "ancient_wisdom"],
            lore_items=["shrine_keeper_message", "forgotten_ritual"],
            save_points=1,
            camera_constraints=(0, 1600, 0, 900)
        )
        
        # 12. Hidden Laboratory (Secret tech area)  
        self.areas["hidden_laboratory"] = WorldArea(
            id="hidden_laboratory",
            name="hidden_laboratory",
            display_name="Hidden Laboratory",
            area_type=AreaType.SECRET,
            size=(2240, 1260),
            background_theme="abandoned_lab",
            tileset_theme="scientific_equipment", 
            music_track="abandoned_science",
            connections={
                "ore_processing": Connection("ore_processing", [GateType.HEAVY_ATTACK], is_hidden=True,
                                           description="Blast through reinforced wall"),
            },
            enemies=["security_drone", "failed_experiment"],
            power_ups=["ranged_attack_upgrade", "energy_shield"],
            secrets=["research_data", "prototype_weapon"],
            lore_items=["scientist_notes", "experiment_log"],
            save_points=2,
            camera_constraints=(0, 2240, 0, 1260)
        )
        
        # Add more connections and shortcuts
        self._add_shortcuts_and_secrets()
    
    def _add_shortcuts_and_secrets(self):
        """Add shortcuts and hidden connections discovered during gameplay"""
        
        # Shortcut from castle back to starting area
        self.areas["gothic_castle"].connections["ancient_caverns_shortcut"] = Connection(
            "ancient_caverns", [GateType.MASTER_KEY], is_shortcut=True,
            description="Ancient elevator, master key required"
        )
        
        # Hidden connection between forest and underground
        self.areas["haunted_forest"].connections["underground_lake_secret"] = Connection(
            "underground_lake", [GateType.GROUND_POUND], is_hidden=True,
            description="Break through forest floor to underground caverns"
        )
        
        # Late game shortcut through void realm
        self.areas["void_realm"].connections["castle_void_portal"] = Connection(
            "gothic_castle", [GateType.VOID_RESISTANCE], is_shortcut=True,
            description="Void portal for fast travel"
        )
    
    def get_accessible_areas(self, from_area: str = None) -> List[str]:
        """Get list of areas accessible from current location"""
        if from_area is None:
            from_area = self.current_area
            
        if from_area not in self.areas:
            return []
        
        accessible = []
        area = self.areas[from_area]
        
        for connection_id, connection in area.connections.items():
            if connection.is_accessible(self.player_abilities):
                # Don't show hidden connections unless they've been discovered
                if connection.is_hidden and connection_id not in self.discovered_shortcuts:
                    continue
                accessible.append(connection.target_area)
        
        return accessible
    
    def can_access_area(self, target_area: str, from_area: str = None) -> bool:
        """Check if target area is accessible from current area"""
        return target_area in self.get_accessible_areas(from_area)
    
    def discover_shortcut(self, shortcut_id: str):
        """Discover a hidden shortcut or connection"""
        self.discovered_shortcuts.add(shortcut_id)
        print(f"🔍 Discovered shortcut: {shortcut_id}")
    
    def gain_ability(self, ability: GateType):
        """Player gains a new ability"""
        if ability not in self.player_abilities:
            self.player_abilities.add(ability)
            print(f"⭐ New ability gained: {ability.value}")
            
            # Check for newly accessible areas
            newly_accessible = []
            for area_id, area in self.areas.items():
                if area_id != self.current_area and area_id not in self.visited_areas:
                    if self.can_access_area(area_id):
                        newly_accessible.append(area.display_name)
            
            if newly_accessible:
                print(f"🗺️ New areas now accessible: {', '.join(newly_accessible)}")
    
    def visit_area(self, area_id: str):
        """Mark area as visited and set as current"""
        if area_id in self.areas:
            self.visited_areas.add(area_id)
            self.current_area = area_id
            area = self.areas[area_id]
            print(f"📍 Entered: {area.display_name}")
            
            # Trigger story events
            for trigger in area.story_triggers:
                print(f"🎭 Story trigger: {trigger}")
    
    def get_world_completion(self) -> Dict[str, Any]:
        """Calculate world exploration completion"""
        total_areas = len(self.areas)
        visited_areas = len(self.visited_areas)
        
        # Calculate secrets found
        total_secrets = sum(len(area.secrets) for area in self.areas.values())
        found_secrets = 0  # Would track in actual implementation
        
        # Calculate power-ups collected
        total_powerups = sum(len(area.power_ups) for area in self.areas.values())
        collected_powerups = len(self.player_abilities)  # Simplified
        
        return {
            "area_completion": (visited_areas / total_areas) * 100,
            "secret_completion": (found_secrets / total_secrets) * 100 if total_secrets > 0 else 0,
            "powerup_completion": (collected_powerups / total_powerups) * 100 if total_powerups > 0 else 0,
            "visited_areas": visited_areas,
            "total_areas": total_areas,
            "abilities_found": len(self.player_abilities)
        }
    
    def get_area_info(self, area_id: str = None) -> Dict[str, Any]:
        """Get detailed information about an area"""
        if area_id is None:
            area_id = self.current_area
            
        if area_id not in self.areas:
            return {}
        
        area = self.areas[area_id]
        connections = []
        
        for conn_id, conn in area.connections.items():
            connections.append({
                "target": conn.target_area,
                "target_name": self.areas[conn.target_area].display_name if conn.target_area in self.areas else "Unknown",
                "accessible": conn.is_accessible(self.player_abilities),
                "requirements": [req.value for req in conn.gate_requirements],
                "description": conn.description,
                "is_hidden": conn.is_hidden,
                "is_shortcut": conn.is_shortcut
            })
        
        return {
            "id": area.id,
            "name": area.display_name,
            "type": area.area_type.value,
            "size": area.size,
            "visited": area_id in self.visited_areas,
            "connections": connections,
            "enemies": area.enemies,
            "power_ups": area.power_ups,
            "secrets": area.secrets,
            "lore_items": area.lore_items,
            "save_points": area.save_points,
            "music": area.music_track
        }
    
    def save_world_state(self, filepath: str):
        """Save current world exploration state"""
        state = {
            "current_area": self.current_area,
            "player_abilities": [ability.value for ability in self.player_abilities],
            "visited_areas": list(self.visited_areas),
            "discovered_shortcuts": list(self.discovered_shortcuts)
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"💾 World state saved to {filepath}")
    
    def load_world_state(self, filepath: str):
        """Load world exploration state"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.current_area = state.get("current_area", "ancient_caverns")
            self.player_abilities = {GateType(ability) for ability in state.get("player_abilities", [])}
            self.visited_areas = set(state.get("visited_areas", []))
            self.discovered_shortcuts = set(state.get("discovered_shortcuts", []))
            
            print(f"📁 World state loaded from {filepath}")
            return True
        except Exception as e:
            print(f"❌ Failed to load world state: {e}")
            return False
    
    def print_world_overview(self):
        """Print a complete overview of the world map"""
        print("\n" + "="*80)
        print("🗺️ RESERKA GOTHIC - COMPLETE WORLD MAP")
        print("="*80)
        
        areas_by_type = {}
        for area in self.areas.values():
            area_type = area.area_type
            if area_type not in areas_by_type:
                areas_by_type[area_type] = []
            areas_by_type[area_type].append(area)
        
        for area_type, areas_list in areas_by_type.items():
            print(f"\n📍 {area_type.value.upper()} AREAS:")
            for area in areas_list:
                visited_marker = "✅" if area.id in self.visited_areas else "⬜"
                current_marker = "👤" if area.id == self.current_area else "  "
                print(f"  {visited_marker} {current_marker} {area.display_name}")
                print(f"     Size: {area.size[0]}x{area.size[1]} | Music: {area.music_track}")
                if area.connections:
                    accessible_connections = [
                        conn.target_area for conn in area.connections.values() 
                        if conn.is_accessible(self.player_abilities)
                    ]
                    print(f"     Accessible connections: {len(accessible_connections)}/{len(area.connections)}")
        
        # Show completion stats
        completion = self.get_world_completion()
        print(f"\n📊 EXPLORATION PROGRESS:")
        print(f"   Areas explored: {completion['visited_areas']}/{completion['total_areas']} ({completion['area_completion']:.1f}%)")
        print(f"   Abilities found: {completion['abilities_found']}")
        print(f"   Current location: {self.areas[self.current_area].display_name}")


def main():
    """Demonstration of the world map system"""
    world = WorldMapSystem()
    
    # Show initial state
    world.print_world_overview()
    
    print("\n" + "="*60)
    print("🎮 GAMEPLAY SIMULATION")
    print("="*60)
    
    # Simulate gameplay progression
    print("\n1. Starting exploration...")
    world.visit_area("crystal_caves")
    
    print("\n2. Found first ability!")
    world.gain_ability(GateType.DOUBLE_JUMP)
    
    print("\n3. Exploring further...")
    world.visit_area("abandoned_mines")
    world.gain_ability(GateType.DASH)
    
    print("\n4. Major progression - accessing castle!")
    world.visit_area("gothic_castle")
    world.gain_ability(GateType.WALL_JUMP)
    
    print("\n5. Boss defeated!")
    world.gain_ability(GateType.BOSS_1_DEFEATED)
    
    # Show current area details
    print("\n📍 CURRENT AREA DETAILS:")
    area_info = world.get_area_info()
    print(f"Area: {area_info['name']}")
    print(f"Type: {area_info['type']}")
    print(f"Accessible connections:")
    for conn in area_info['connections']:
        status = "✅ Accessible" if conn['accessible'] else "❌ Blocked"
        requirements = f" (Requires: {', '.join(conn['requirements'])})" if conn['requirements'] else ""
        print(f"  - {conn['target_name']}: {status}{requirements}")
    
    # Save state
    world.save_world_state("world_state.json")

if __name__ == "__main__":
    main()
