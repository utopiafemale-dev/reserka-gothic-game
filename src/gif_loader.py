#!/usr/bin/env python3
"""
GIF Animation Loader for Reserka Gothic
Handles animated GIF loading and playback
"""

import pygame
from PIL import Image
from pathlib import Path
from typing import List, Optional
import time

class AnimatedGIF:
    """Class to handle animated GIF playback"""
    
    def __init__(self, gif_path: Path):
        self.gif_path = gif_path
        self.frames = []
        self.frame_durations = []
        self.current_frame = 0
        self.frame_timer = 0.0
        self.total_frames = 0
        self.loaded = False
        
        self.load_gif()
    
    def load_gif(self):
        """Load GIF frames using PIL and convert to pygame surfaces"""
        try:
            # Open GIF with PIL
            pil_image = Image.open(self.gif_path)
            
            frame_index = 0
            while True:
                try:
                    # Seek to frame
                    pil_image.seek(frame_index)
                    
                    # Convert PIL frame to pygame surface
                    frame_data = pil_image.convert("RGBA")
                    pygame_surface = pygame.image.fromstring(
                        frame_data.tobytes(), frame_data.size, "RGBA"
                    )
                    
                    self.frames.append(pygame_surface)
                    
                    # Get frame duration (default to 100ms if not available)
                    duration = pil_image.info.get('duration', 100)
                    self.frame_durations.append(duration)
                    
                    frame_index += 1
                    
                except EOFError:
                    # End of frames
                    break
            
            self.total_frames = len(self.frames)
            self.loaded = True
            print(f"✅ Loaded animated GIF: {self.total_frames} frames from {self.gif_path}")
            
        except Exception as e:
            print(f"❌ Failed to load GIF {self.gif_path}: {e}")
            self.loaded = False
    
    def update(self, dt: float):
        """Update animation frame based on elapsed time"""
        if not self.loaded or self.total_frames <= 1:
            return
        
        self.frame_timer += dt * 1000  # Convert to milliseconds
        
        current_duration = self.frame_durations[self.current_frame]
        
        if self.frame_timer >= current_duration:
            self.frame_timer = 0.0
            self.current_frame = (self.current_frame + 1) % self.total_frames
    
    def get_current_surface(self) -> Optional[pygame.Surface]:
        """Get the current frame surface"""
        if not self.loaded or not self.frames:
            return None
        
        return self.frames[self.current_frame]
    
    def get_scaled_surface(self, size: tuple) -> Optional[pygame.Surface]:
        """Get current frame scaled to specified size"""
        current_surface = self.get_current_surface()
        if current_surface:
            return pygame.transform.scale(current_surface, size)
        return None
    
    def reset(self):
        """Reset animation to first frame"""
        self.current_frame = 0
        self.frame_timer = 0.0


class GIFManager:
    """Manager for multiple animated GIFs"""
    
    def __init__(self):
        self.gifs = {}
        self.last_update_time = time.time()
    
    def load_gif(self, name: str, gif_path: Path) -> bool:
        """Load an animated GIF with a given name"""
        try:
            animated_gif = AnimatedGIF(gif_path)
            if animated_gif.loaded:
                self.gifs[name] = animated_gif
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to load GIF {name}: {e}")
            return False
    
    def update_all(self):
        """Update all loaded GIF animations"""
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        for gif in self.gifs.values():
            gif.update(dt)
    
    def get_gif(self, name: str) -> Optional[AnimatedGIF]:
        """Get animated GIF by name"""
        return self.gifs.get(name)
    
    def get_current_frame(self, name: str, size: Optional[tuple] = None) -> Optional[pygame.Surface]:
        """Get current frame of named GIF, optionally scaled"""
        gif = self.get_gif(name)
        if gif:
            if size:
                return gif.get_scaled_surface(size)
            else:
                return gif.get_current_surface()
        return None
