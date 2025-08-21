#!/usr/bin/env python3
"""
Metroidvania Progression System for Reserka Gothic
Implements guided nonlinearity with ability gates, power-ups, and interconnected world design
"""

import pygame
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class AbilityType(Enum):
    DOUBLE_JUMP = "double_jump"
    DASH = "dash"
    WALL_JUMP = "wall_jump" 
    HIGH_JUMP = "high_jump"
    SUPER_DASH = "super_dash"
    BREAK_BLOCKS = "break_blocks"
    SWIM = "swim"
    CLIMB = "climb"
    FIRE_RESIST = "fire_resist"
    KEY_RED = "key_red"
    KEY_BLUE = "key_blue"
    KEY_GOLD = "key_gold"

class AreaState(Enum):
    LOCKED = "locked"
    ACCESSIBLE = "accessible" 
    PARTIALLY_ACCESSIBLE = "partially_accessible"
    COMPLETED = "completed"

@dataclass
class AbilityGate:
    """Represents a barrier that requires specific abilities to pass"""
    required_abilities: Set[AbilityType]
    gate_type: str  # "door", "pit", "wall", "enemy", "puzzle"
    position: Tuple[int, int]
    size: Tuple[int, int]
    active: bool = True
    description: str = ""

@dataclass
class PowerUp:
    """Collectible power-up that grants new abilities"""
    ability: AbilityType
    position: Tuple[int, int]
    collected: bool = False
    name: str = ""
    description: str = ""
    sprite_name: str = ""

@dataclass
class AreaConnection:
    """Connection between two areas"""
    from_area: str
    to_area: str
    gates: List[AbilityGate]
    bidirectional: bool = True

@dataclass 
class GameArea:
    """A distinct area/room in the game world"""
    name: str
    display_name: str
    size: Tuple[int, int]
    connections: List[str]  # Connected area names
    power_ups: List[PowerUp]
    required_abilities: Set[AbilityType]  # Minimum abilities needed to enter
    optional_abilities: Set[AbilityType]  # Abilities that unlock secrets/shortcuts
    completion_percentage: float = 0.0
    discovered: bool = False

class MetroidvaniaProgression:
    """
    Manages the Metroidvania progression system with guided nonlinearity
    """
    
    def __init__(self):
        self.player_abilities: Set[AbilityType] = set()
        self.areas: Dict[str, GameArea] = {}
        self.connections: List[AreaConnection] = []
        self.current_area = "starting_cave"
        
        # Progression tracking
        self.total_power_ups = 0
        self.collected_power_ups = 0
        self.total_areas = 0
        self.discovered_areas = 0
        
        # Hints and guidance
        self.hint_system_enabled = True
        self.current_objectives: List[str] = []
        
        print("🗺️ Metroidvania Progression System initialized")
        self.setup_world()
    
    def setup_world(self):
        """Set up the interconnected world with areas, connections, and gates"""
        
        # Define all game areas
        areas_data = {
            "starting_cave": {
                "display_name": "Ancient Cave",
                "size": (2560, 1440),
                "connections": ["forest_entrance", "underground_passage"],
                "power_ups": [
                    PowerUp(AbilityType.DOUBLE_JUMP, (500, 400), False, "Double Jump Boots", 
                           "Allows jumping twice in mid-air", "double_jump_boots")
                ],
                "required_abilities": set(),
                "optional_abilities": set()
            },
            
            "forest_entrance": {
                "display_name": "Mystic Forest",
                "size": (3840, 1440), 
                "connections": ["starting_cave", "castle_courtyard", "hidden_shrine"],
                "power_ups": [
                    PowerUp(AbilityType.DASH, (800, 300), False, "Shadow Dash",
                           "Dash quickly through enemies and small gaps", "dash_ability")
                ],
                "required_abilities": {AbilityType.DOUBLE_JUMP},
                "optional_abilities": {AbilityType.DASH}
            },
            
            "underground_passage": {
                "display_name": "Underground Tunnels", 
                "size": (2560, 2160),
                "connections": ["starting_cave", "deep_chambers", "crystal_cavern"],
                "power_ups": [
                    PowerUp(AbilityType.BREAK_BLOCKS, (400, 800), False, "Power Gauntlets",
                           "Break through certain walls and blocks", "power_gauntlets")
                ],
                "required_abilities": set(),
                "optional_abilities": {AbilityType.BREAK_BLOCKS}
            },
            
            "castle_courtyard": {
                "display_name": "Gothic Castle Courtyard",
                "size": (2560, 1440),
                "connections": ["forest_entrance", "castle_interior", "tower_base"],
                "power_ups": [
                    PowerUp(AbilityType.KEY_RED, (1200, 200), False, "Crimson Key",
                           "Opens red doors throughout the castle", "red_key")
                ],
                "required_abilities": {AbilityType.DOUBLE_JUMP, AbilityType.DASH},
                "optional_abilities": set()
            },
            
            "castle_interior": {
                "display_name": "Castle Interior",
                "size": (3840, 2160),
                "connections": ["castle_courtyard", "throne_room", "dungeon_entrance"],
                "power_ups": [
                    PowerUp(AbilityType.WALL_JUMP, (600, 1000), False, "Wall Cling Claws",
                           "Cling to and jump off walls", "wall_jump_claws")
                ],
                "required_abilities": {AbilityType.KEY_RED},
                "optional_abilities": {AbilityType.WALL_JUMP}
            },
            
            "hidden_shrine": {
                "display_name": "Hidden Shrine",
                "size": (1280, 720),
                "connections": ["forest_entrance"],
                "power_ups": [
                    PowerUp(AbilityType.HIGH_JUMP, (400, 300), False, "Spring Boots",
                           "Jump much higher than normal", "spring_boots")
                ],
                "required_abilities": {AbilityType.DASH},  # Secret area requiring dash
                "optional_abilities": set()
            },
            
            "deep_chambers": {
                "display_name": "Deep Chambers",
                "size": (2560, 1440),
                "connections": ["underground_passage", "lava_caves"],
                "power_ups": [
                    PowerUp(AbilityType.KEY_BLUE, (800, 600), False, "Sapphire Key",
                           "Opens blue doors in the depths", "blue_key")
                ],
                "required_abilities": {AbilityType.BREAK_BLOCKS},
                "optional_abilities": set()
            },
            
            "crystal_cavern": {
                "display_name": "Crystal Cavern",
                "size": (1920, 1440),
                "connections": ["underground_passage"],
                "power_ups": [
                    PowerUp(AbilityType.SUPER_DASH, (960, 400), False, "Crystal Dash",
                           "Dash through multiple enemies and barriers", "crystal_dash")
                ],
                "required_abilities": {AbilityType.WALL_JUMP},
                "optional_abilities": set()
            },
            
            "lava_caves": {
                "display_name": "Lava Caves",
                "size": (2560, 1440),
                "connections": ["deep_chambers", "final_chamber"],
                "power_ups": [
                    PowerUp(AbilityType.FIRE_RESIST, (300, 700), False, "Heat Shield",
                           "Resist fire damage and walk through lava", "heat_shield")
                ],
                "required_abilities": {AbilityType.KEY_BLUE, AbilityType.HIGH_JUMP},
                "optional_abilities": set()
            },
            
            "final_chamber": {
                "display_name": "Final Chamber",
                "size": (1920, 1440),
                "connections": ["lava_caves"],
                "power_ups": [
                    PowerUp(AbilityType.KEY_GOLD, (960, 200), False, "Golden Master Key",
                           "The ultimate key - opens all remaining barriers", "gold_key")
                ],
                "required_abilities": {AbilityType.FIRE_RESIST, AbilityType.SUPER_DASH},
                "optional_abilities": set()
            }
        }
        
        # Create GameArea objects
        for area_name, area_data in areas_data.items():
            area = GameArea(
                name=area_name,
                display_name=area_data["display_name"],
                size=area_data["size"],
                connections=area_data["connections"],
                power_ups=area_data["power_ups"],
                required_abilities=area_data["required_abilities"],
                optional_abilities=area_data["optional_abilities"]
            )
            self.areas[area_name] = area
        
        # Set up connections with ability gates
        self.setup_connections()
        
        # Count totals for progression tracking
        self.total_areas = len(self.areas)
        self.total_power_ups = sum(len(area.power_ups) for area in self.areas.values())
        
        # Mark starting area as discovered
        if "starting_cave" in self.areas:
            self.areas["starting_cave"].discovered = True
            self.discovered_areas = 1
        
        print(f"🗺️ World setup complete: {self.total_areas} areas, {self.total_power_ups} power-ups")
    
    def setup_connections(self):
        """Set up connections between areas with appropriate ability gates"""
        
        connection_data = [
            # Starting Cave connections
            {
                "from": "starting_cave",
                "to": "forest_entrance", 
                "gates": [AbilityGate({AbilityType.DOUBLE_JUMP}, "pit", (400, 300), (200, 100),
                                    description="A deep chasm blocks the way - need better jumping ability")]
            },
            {
                "from": "starting_cave",
                "to": "underground_passage",
                "gates": []  # Always accessible
            },
            
            # Forest connections
            {
                "from": "forest_entrance", 
                "to": "castle_courtyard",
                "gates": [AbilityGate({AbilityType.DASH}, "gap", (600, 200), (150, 50),
                                    description="A wide gap - need to dash across")]
            },
            {
                "from": "forest_entrance",
                "to": "hidden_shrine",
                "gates": [AbilityGate({AbilityType.DASH}, "secret", (900, 150), (64, 64),
                                    description="Hidden passage behind thorns - dash through")]
            },
            
            # Underground connections
            {
                "from": "underground_passage",
                "to": "deep_chambers", 
                "gates": [AbilityGate({AbilityType.BREAK_BLOCKS}, "wall", (300, 500), (100, 200),
                                    description="Cracked wall blocks the passage")]
            },
            {
                "from": "underground_passage",
                "to": "crystal_cavern",
                "gates": [AbilityGate({AbilityType.WALL_JUMP}, "vertical", (800, 300), (50, 400),
                                    description="Tall vertical shaft - need wall jumping")]
            },
            
            # Castle connections
            {
                "from": "castle_courtyard",
                "to": "castle_interior",
                "gates": [AbilityGate({AbilityType.KEY_RED}, "door", (500, 400), (64, 128),
                                    description="Locked red door")]
            },
            
            # Deep area connections
            {
                "from": "deep_chambers",
                "to": "lava_caves",
                "gates": [AbilityGate({AbilityType.KEY_BLUE, AbilityType.HIGH_JUMP}, "door_pit", (400, 600), (100, 200),
                                    description="Blue door over a deep pit")]
            },
            
            # Final connections
            {
                "from": "lava_caves",
                "to": "final_chamber",
                "gates": [AbilityGate({AbilityType.FIRE_RESIST, AbilityType.SUPER_DASH}, "lava_dash", (800, 300), (300, 100),
                                    description="Must dash through lava stream")]
            }
        ]
        
        for conn_data in connection_data:
            connection = AreaConnection(
                from_area=conn_data["from"],
                to_area=conn_data["to"], 
                gates=conn_data["gates"],
                bidirectional=True
            )
            self.connections.append(connection)
    
    def can_access_area(self, area_name: str, from_area: str = None) -> bool:
        """Check if player can access a specific area"""
        if area_name not in self.areas:
            return False
        
        area = self.areas[area_name]
        
        # Check if player has required abilities for the area itself
        if not self.player_abilities.issuperset(area.required_abilities):
            return False
        
        # If checking from a specific area, check connection gates
        if from_area:
            for connection in self.connections:
                if ((connection.from_area == from_area and connection.to_area == area_name) or
                    (connection.bidirectional and connection.from_area == area_name and connection.to_area == from_area)):
                    
                    # Check all gates in this connection
                    for gate in connection.gates:
                        if gate.active and not self.player_abilities.issuperset(gate.required_abilities):
                            return False
        
        return True
    
    def get_accessible_areas(self) -> List[str]:
        """Get list of all areas currently accessible to the player"""
        accessible = []
        
        for area_name, area in self.areas.items():
            if self.can_access_area(area_name):
                accessible.append(area_name)
        
        return accessible
    
    def get_blocked_connections(self) -> List[Tuple[str, str, List[AbilityType]]]:
        """Get connections blocked by missing abilities"""
        blocked = []
        
        for connection in self.connections:
            for gate in connection.gates:
                if gate.active:
                    missing_abilities = gate.required_abilities - self.player_abilities
                    if missing_abilities:
                        blocked.append((connection.from_area, connection.to_area, list(missing_abilities)))
        
        return blocked
    
    def collect_power_up(self, area_name: str, power_up_index: int) -> bool:
        """Attempt to collect a power-up"""
        if area_name not in self.areas:
            return False
        
        area = self.areas[area_name]
        if power_up_index >= len(area.power_ups):
            return False
        
        power_up = area.power_ups[power_up_index]
        if power_up.collected:
            return False
        
        # Collect the power-up
        power_up.collected = True
        self.player_abilities.add(power_up.ability)
        self.collected_power_ups += 1
        
        print(f"🎯 Collected {power_up.name}! Gained ability: {power_up.ability.value}")
        
        # Update objectives based on new ability
        self.update_objectives()
        
        return True
    
    def update_objectives(self):
        """Update current objectives based on player's abilities and progress"""
        self.current_objectives.clear()
        
        # Find newly accessible areas
        newly_accessible = []
        for area_name, area in self.areas.items():
            if not area.discovered and self.can_access_area(area_name):
                newly_accessible.append(area.display_name)
        
        if newly_accessible:
            self.current_objectives.append(f"Explore newly accessible areas: {', '.join(newly_accessible)}")
        
        # Find obtainable power-ups
        obtainable_power_ups = []
        for area_name, area in self.areas.items():
            if self.can_access_area(area_name):
                for power_up in area.power_ups:
                    if not power_up.collected:
                        obtainable_power_ups.append(power_up.name)
        
        if obtainable_power_ups:
            self.current_objectives.append(f"Find power-ups: {', '.join(obtainable_power_ups[:3])}")  # Show max 3
        
        # Suggest next steps based on blocked connections
        blocked = self.get_blocked_connections()
        if blocked:
            next_ability = list(blocked[0][2])[0]  # Get first missing ability
            self.current_objectives.append(f"Find ability: {next_ability.value.replace('_', ' ').title()}")
    
    def get_completion_percentage(self) -> float:
        """Calculate overall completion percentage"""
        if self.total_power_ups == 0:
            return 0.0
        
        power_up_completion = (self.collected_power_ups / self.total_power_ups) * 0.6
        area_completion = (self.discovered_areas / self.total_areas) * 0.4
        
        return (power_up_completion + area_completion) * 100
    
    def discover_area(self, area_name: str):
        """Mark an area as discovered"""
        if area_name in self.areas and not self.areas[area_name].discovered:
            self.areas[area_name].discovered = True
            self.discovered_areas += 1
            print(f"🗺️ Discovered new area: {self.areas[area_name].display_name}")
    
    def get_area_state(self, area_name: str) -> AreaState:
        """Get the current state of an area"""
        if area_name not in self.areas:
            return AreaState.LOCKED
        
        area = self.areas[area_name]
        
        if not self.can_access_area(area_name):
            return AreaState.LOCKED
        
        # Check if all power-ups are collected
        all_collected = all(power_up.collected for power_up in area.power_ups)
        
        if all_collected:
            return AreaState.COMPLETED
        elif area.discovered:
            return AreaState.ACCESSIBLE
        else:
            return AreaState.PARTIALLY_ACCESSIBLE
    
    def get_hint_for_area(self, area_name: str) -> str:
        """Get a hint for accessing or completing an area"""
        if area_name not in self.areas:
            return "Unknown area"
        
        area = self.areas[area_name]
        state = self.get_area_state(area_name)
        
        if state == AreaState.LOCKED:
            missing = area.required_abilities - self.player_abilities
            if missing:
                ability_names = [ability.value.replace('_', ' ').title() for ability in missing]
                return f"Need abilities: {', '.join(ability_names)}"
        
        elif state == AreaState.ACCESSIBLE:
            uncollected = [p for p in area.power_ups if not p.collected]
            if uncollected:
                return f"Find {uncollected[0].name} in {area.display_name}"
        
        return "Area fully explored"
    
    def save_progress(self, filename: str = "metroidvania_save.json"):
        """Save progression state to file"""
        save_data = {
            "player_abilities": list(ability.value for ability in self.player_abilities),
            "current_area": self.current_area,
            "collected_power_ups": self.collected_power_ups,
            "discovered_areas": self.discovered_areas,
            "areas": {}
        }
        
        # Save area states
        for area_name, area in self.areas.items():
            save_data["areas"][area_name] = {
                "discovered": area.discovered,
                "power_ups": [p.collected for p in area.power_ups]
            }
        
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"💾 Progress saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save progress: {e}")
    
    def load_progress(self, filename: str = "metroidvania_save.json"):
        """Load progression state from file"""
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            # Restore abilities
            self.player_abilities = {AbilityType(ability) for ability in save_data["player_abilities"]}
            self.current_area = save_data["current_area"]
            self.collected_power_ups = save_data["collected_power_ups"] 
            self.discovered_areas = save_data["discovered_areas"]
            
            # Restore area states
            for area_name, area_data in save_data["areas"].items():
                if area_name in self.areas:
                    area = self.areas[area_name]
                    area.discovered = area_data["discovered"]
                    for i, collected in enumerate(area_data["power_ups"]):
                        if i < len(area.power_ups):
                            area.power_ups[i].collected = collected
            
            self.update_objectives()
            print(f"💾 Progress loaded from {filename}")
            
        except Exception as e:
            print(f"❌ Failed to load progress: {e}")

def main():
    """Test the progression system"""
    print("Testing Metroidvania Progression System...")
    
    progression = MetroidvaniaProgression()
    
    # Test initial state
    print(f"Accessible areas: {progression.get_accessible_areas()}")
    print(f"Completion: {progression.get_completion_percentage():.1f}%")
    
    # Test collecting power-up
    progression.collect_power_up("starting_cave", 0)  # Double jump
    print(f"After collecting double jump: {progression.get_accessible_areas()}")
    
    # Test progression
    progression.collect_power_up("forest_entrance", 0)  # Dash
    print(f"After collecting dash: {progression.get_accessible_areas()}")
    
    print(f"Current objectives: {progression.current_objectives}")
    print(f"Final completion: {progression.get_completion_percentage():.1f}%")
    
    print("✅ Progression system test complete")

if __name__ == "__main__":
    main()
