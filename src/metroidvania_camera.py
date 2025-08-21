#!/usr/bin/env python3
"""
Metroidvania Camera System for Reserka Gothic
Implements smooth camera following, room-based constraints, and cinematic transitions
"""

import pygame
import math
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

class CameraMode(Enum):
    FOLLOW_PLAYER = "follow_player"
    ROOM_LOCKED = "room_locked"
    CINEMATIC = "cinematic"
    TRANSITION = "transition"

@dataclass
class CameraConstraints:
    """Camera movement constraints for a room/area"""
    left: int = 0
    right: int = 1280
    top: int = 0
    bottom: int = 720
    smooth_edges: bool = True

@dataclass
class CameraTarget:
    """Camera target with position and priority"""
    x: float
    y: float
    priority: int = 1
    smooth_factor: float = 0.1

class MetroidvaniaCamera:
    """
    Advanced camera system for Metroidvania games
    Features smooth following, room constraints, and cinematic control
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Camera position (top-left of viewport)
        self.x = 0.0
        self.y = 0.0
        
        # Target position (what camera is trying to follow)
        self.target_x = 0.0
        self.target_y = 0.0
        
        # Camera settings
        self.mode = CameraMode.FOLLOW_PLAYER
        self.smooth_factor = 0.08  # How smoothly camera follows (lower = smoother)
        self.look_ahead_distance = 100  # How far ahead to look when moving
        self.deadzone_width = 80   # Horizontal deadzone around player
        self.deadzone_height = 60  # Vertical deadzone around player
        
        # Current constraints
        self.constraints = CameraConstraints()
        
        # Shake effect
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_timer = 0.0
        
        # Zoom (for future use)
        self.zoom = 1.0
        self.target_zoom = 1.0
        
        # Room transition
        self.transitioning = False
        self.transition_timer = 0.0
        self.transition_duration = 1000  # milliseconds
        self.transition_start_pos = (0, 0)
        self.transition_end_pos = (0, 0)
        
        # Player velocity tracking for look-ahead
        self.player_vel_x = 0.0
        self.player_vel_y = 0.0
        self.velocity_history = []
        self.max_history = 5
        
        print("📷 Metroidvania Camera System initialized")
    
    def update(self, dt: float, player_pos: Tuple[float, float], player_vel: Tuple[float, float] = (0, 0)):
        """Update camera position and effects"""
        
        # Update player velocity tracking
        self.player_vel_x, self.player_vel_y = player_vel
        self.velocity_history.append(player_vel)
        if len(self.velocity_history) > self.max_history:
            self.velocity_history.pop(0)
        
        # Calculate average velocity for smoother look-ahead
        avg_vel_x = sum(v[0] for v in self.velocity_history) / len(self.velocity_history) if self.velocity_history else 0
        avg_vel_y = sum(v[1] for v in self.velocity_history) / len(self.velocity_history) if self.velocity_history else 0
        
        if self.mode == CameraMode.FOLLOW_PLAYER:
            self._update_follow_player(player_pos, (avg_vel_x, avg_vel_y))
        elif self.mode == CameraMode.ROOM_LOCKED:
            self._update_room_locked(player_pos)
        elif self.mode == CameraMode.TRANSITION:
            self._update_transition(dt)
        
        # Apply constraints
        self._apply_constraints()
        
        # Update camera shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_intensity = 0
        
        # Update zoom
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * 0.05
    
    def _update_follow_player(self, player_pos: Tuple[float, float], player_vel: Tuple[float, float]):
        """Update camera when following player with advanced techniques"""
        player_x, player_y = player_pos
        vel_x, vel_y = player_vel
        
        # Calculate camera center position
        camera_center_x = self.x + self.screen_width // 2
        camera_center_y = self.y + self.screen_height // 2
        
        # Calculate target position with look-ahead
        look_ahead_x = vel_x * self.look_ahead_distance * 0.01  # Scale down velocity influence
        look_ahead_y = vel_y * self.look_ahead_distance * 0.005  # Less vertical look-ahead
        
        target_center_x = player_x + look_ahead_x
        target_center_y = player_y + look_ahead_y - 50  # Offset camera slightly above player
        
        # Apply deadzone - only move camera if player is outside deadzone
        dx = target_center_x - camera_center_x
        dy = target_center_y - camera_center_y
        
        # Horizontal deadzone
        if abs(dx) > self.deadzone_width:
            if dx > 0:
                target_center_x = camera_center_x + self.deadzone_width
            else:
                target_center_x = camera_center_x - self.deadzone_width
            
            # Smooth movement
            self.target_x = target_center_x - self.screen_width // 2
        
        # Vertical deadzone  
        if abs(dy) > self.deadzone_height:
            if dy > 0:
                target_center_y = camera_center_y + self.deadzone_height
            else:
                target_center_y = camera_center_y - self.deadzone_height
                
            # Smooth movement
            self.target_y = target_center_y - self.screen_height // 2
        
        # Apply smooth following
        self.x += (self.target_x - self.x) * self.smooth_factor
        self.y += (self.target_y - self.y) * self.smooth_factor
    
    def _update_room_locked(self, player_pos: Tuple[float, float]):
        """Update camera when locked to room boundaries"""
        # In room-locked mode, camera doesn't follow player
        # Used for boss fights, puzzle rooms, etc.
        pass
    
    def _update_transition(self, dt: float):
        """Update camera during room transitions"""
        if not self.transitioning:
            return
            
        self.transition_timer += dt
        progress = min(1.0, self.transition_timer / self.transition_duration)
        
        # Smooth transition using easing
        eased_progress = self._ease_in_out_cubic(progress)
        
        # Interpolate camera position
        start_x, start_y = self.transition_start_pos
        end_x, end_y = self.transition_end_pos
        
        self.x = start_x + (end_x - start_x) * eased_progress
        self.y = start_y + (end_y - start_y) * eased_progress
        
        if progress >= 1.0:
            self.transitioning = False
            self.mode = CameraMode.FOLLOW_PLAYER
    
    def _ease_in_out_cubic(self, t: float) -> float:
        """Cubic easing function for smooth transitions"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def _apply_constraints(self):
        """Apply camera movement constraints"""
        # Clamp camera position to constraints
        self.x = max(self.constraints.left, min(self.x, self.constraints.right - self.screen_width))
        self.y = max(self.constraints.top, min(self.y, self.constraints.bottom - self.screen_height))
        
        # Update targets to match constraints
        self.target_x = max(self.constraints.left, min(self.target_x, self.constraints.right - self.screen_width))
        self.target_y = max(self.constraints.top, min(self.target_y, self.constraints.bottom - self.screen_height))
    
    def get_render_position(self) -> Tuple[int, int]:
        """Get final camera position with shake applied"""
        shake_x = shake_y = 0
        
        if self.shake_intensity > 0:
            import random
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        
        return (int(self.x + shake_x), int(self.y + shake_y))
    
    def set_constraints(self, constraints: CameraConstraints):
        """Set new camera constraints for current room/area"""
        self.constraints = constraints
        print(f"📷 Camera constraints updated: {constraints.left}-{constraints.right}, {constraints.top}-{constraints.bottom}")
    
    def start_room_transition(self, end_pos: Tuple[float, float], duration: float = 1000):
        """Start a smooth transition to a new room"""
        self.mode = CameraMode.TRANSITION
        self.transitioning = True
        self.transition_timer = 0
        self.transition_duration = duration
        self.transition_start_pos = (self.x, self.y)
        self.transition_end_pos = end_pos
        
        print(f"📷 Starting room transition to {end_pos}")
    
    def set_mode(self, mode: CameraMode):
        """Change camera mode"""
        self.mode = mode
        print(f"📷 Camera mode changed to {mode.value}")
    
    def add_shake(self, intensity: float, duration: float):
        """Add camera shake effect"""
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_timer = max(self.shake_timer, duration)
    
    def set_zoom(self, zoom: float, smooth: bool = True):
        """Set camera zoom level"""
        if smooth:
            self.target_zoom = zoom
        else:
            self.zoom = zoom
            self.target_zoom = zoom
    
    def focus_on_point(self, pos: Tuple[float, float], immediate: bool = False):
        """Focus camera on a specific point"""
        target_x = pos[0] - self.screen_width // 2
        target_y = pos[1] - self.screen_height // 2
        
        if immediate:
            self.x = target_x
            self.y = target_y
            self.target_x = target_x
            self.target_y = target_y
        else:
            self.target_x = target_x
            self.target_y = target_y
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        world_x, world_y = world_pos
        camera_x, camera_y = self.get_render_position()
        
        screen_x = int((world_x - camera_x) * self.zoom)
        screen_y = int((world_y - camera_y) * self.zoom)
        
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        screen_x, screen_y = screen_pos
        camera_x, camera_y = self.get_render_position()
        
        world_x = (screen_x / self.zoom) + camera_x
        world_y = (screen_y / self.zoom) + camera_y
        
        return (world_x, world_y)
    
    def is_on_screen(self, pos: Tuple[float, float], size: Tuple[int, int] = (64, 64)) -> bool:
        """Check if a world position is visible on screen"""
        screen_pos = self.world_to_screen(pos)
        margin = 100  # Add margin for objects partially off-screen
        
        return (-margin < screen_pos[0] < self.screen_width + margin and 
                -margin < screen_pos[1] < self.screen_height + margin)
    
    def get_visible_bounds(self) -> Tuple[float, float, float, float]:
        """Get the world bounds of what's currently visible"""
        camera_x, camera_y = self.get_render_position()
        
        left = camera_x
        right = camera_x + self.screen_width
        top = camera_y
        bottom = camera_y + self.screen_height
        
        return (left, top, right, bottom)

def main():
    """Test the camera system"""
    print("Testing Metroidvania Camera System...")
    
    camera = MetroidvaniaCamera(1280, 720)
    
    # Test basic following
    camera.update(16, (640, 360), (5, 0))
    print(f"Camera position: ({camera.x:.1f}, {camera.y:.1f})")
    
    # Test constraints
    constraints = CameraConstraints(0, 2560, 0, 1440)  # 2x screen size room
    camera.set_constraints(constraints)
    
    # Test transition
    camera.start_room_transition((1280, 0), 1000)
    print("Room transition started")
    
    print("✅ Camera system test complete")

if __name__ == "__main__":
    main()
