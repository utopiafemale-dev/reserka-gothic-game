#!/usr/bin/env python3
"""
Character Selection Screen for Reserka Gothic
Allows players to choose between different characters
"""

import pygame
import sys
import math
from pathlib import Path
from typing import Optional, Dict, Any
from character_asset_manager import CharacterAssetManager

class CharacterSelection:
    """Character selection screen"""
    
    def __init__(self, screen: pygame.Surface, assets_path: Path):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.assets_path = assets_path
        
        # Load character asset manager
        self.asset_manager = CharacterAssetManager(assets_path)
        
        # UI configuration
        self.background_color = (20, 20, 30)
        self.title_color = (255, 215, 0)  # Gold
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 100, 100)
        self.selected_color = (100, 255, 100)
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 64)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        # Character selection state
        self.characters = self.asset_manager.get_available_characters()
        self.selected_character_index = 0
        self.selected_character_id = None
        self.hover_index = -1
        
        # Animation
        self.animation_time = 0
        self.preview_animation_time = 0
        
        # Character preview panels
        self.setup_character_panels()
    
    def setup_character_panels(self):
        """Setup character selection panels"""
        self.character_panels = []
        
        panel_width = 300
        panel_height = 400
        panel_margin = 50
        
        # Calculate positioning for centered panels
        total_width = len(self.characters) * panel_width + (len(self.characters) - 1) * panel_margin
        start_x = (self.screen_width - total_width) // 2
        panel_y = (self.screen_height - panel_height) // 2 + 50
        
        for i, character in enumerate(self.characters):
            panel_x = start_x + i * (panel_width + panel_margin)
            
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            
            # Create character preview
            preview_surface = self.create_character_preview(character['id'])
            
            panel_info = {
                'rect': panel_rect,
                'character': character,
                'preview': preview_surface,
                'selected': False,
                'hover': False
            }
            
            self.character_panels.append(panel_info)
    
    def create_character_preview(self, character_id: str) -> pygame.Surface:
        """Create animated character preview"""
        preview_size = (200, 200)
        preview_surface = pygame.Surface(preview_size, pygame.SRCALPHA)
        
        # Get character animations
        animations = self.asset_manager.get_character_animations(character_id)
        
        # Use idle animation if available, otherwise use first available animation
        if 'idle' in animations:
            frames = animations['idle']
        elif 'walk' in animations:
            frames = animations['walk']
        else:
            frames = list(animations.values())[0] if animations else []
        
        if frames:
            # Use first frame for static preview
            frame = frames[0]
            frame_rect = frame.get_rect()
            frame_rect.center = preview_surface.get_rect().center
            preview_surface.blit(frame, frame_rect)
        
        return preview_surface
    
    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return {'action': 'back'}
            elif event.key == pygame.K_LEFT:
                self.selected_character_index = (self.selected_character_index - 1) % len(self.characters)
            elif event.key == pygame.K_RIGHT:
                self.selected_character_index = (self.selected_character_index + 1) % len(self.characters)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                selected_character = self.characters[self.selected_character_index]
                return {
                    'action': 'select',
                    'character_id': selected_character['id'],
                    'character_name': selected_character['name']
                }
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.hover_index = -1
            
            for i, panel in enumerate(self.character_panels):
                if panel['rect'].collidepoint(mouse_pos):
                    self.hover_index = i
                    self.selected_character_index = i
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.hover_index >= 0:
                    selected_character = self.characters[self.hover_index]
                    return {
                        'action': 'select',
                        'character_id': selected_character['id'],
                        'character_name': selected_character['name']
                    }
        
        return None
    
    def update(self, dt: float):
        """Update animation and state"""
        self.animation_time += dt
        self.preview_animation_time += dt
        
        # Update panel states
        for i, panel in enumerate(self.character_panels):
            panel['selected'] = (i == self.selected_character_index)
            panel['hover'] = (i == self.hover_index)
    
    def draw(self):
        """Draw the character selection screen"""
        # Clear screen
        self.screen.fill(self.background_color)
        
        # Draw title
        title_text = self.title_font.render("Choose Your Character", True, self.title_color)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen_width // 2
        title_rect.y = 50
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.subtitle_font.render("Select a character to begin your adventure", True, self.text_color)
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.centerx = self.screen_width // 2
        subtitle_rect.y = title_rect.bottom + 20
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw character panels
        self.draw_character_panels()
        
        # Draw instructions
        self.draw_instructions()
        
        # Draw selected character info
        if 0 <= self.selected_character_index < len(self.characters):
            self.draw_character_info(self.characters[self.selected_character_index])
    
    def draw_character_panels(self):
        """Draw character selection panels"""
        for i, panel in enumerate(self.character_panels):
            rect = panel['rect']
            character = panel['character']
            
            # Determine panel colors based on state
            if panel['selected']:
                border_color = self.selected_color
                bg_color = (40, 60, 40)
                border_width = 4
            elif panel['hover']:
                border_color = self.highlight_color
                bg_color = (60, 40, 40)
                border_width = 3
            else:
                border_color = (100, 100, 100)
                bg_color = (30, 30, 40)
                border_width = 2
            
            # Add pulse effect for selected character
            if panel['selected']:
                pulse = abs(math.sin(self.animation_time * 3)) * 0.3 + 0.7
                border_color = tuple(int(c * pulse) for c in border_color)
            
            # Draw panel background
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, border_width)
            
            # Draw character preview
            preview = panel['preview']
            preview_rect = preview.get_rect()
            preview_rect.centerx = rect.centerx
            preview_rect.y = rect.y + 30
            self.screen.blit(preview, preview_rect)
            
            # Draw character name
            name_text = self.text_font.render(character['name'], True, self.text_color)
            name_rect = name_text.get_rect()
            name_rect.centerx = rect.centerx
            name_rect.y = preview_rect.bottom + 20
            self.screen.blit(name_text, name_rect)
            
            # Draw animation list
            animations_text = f"Animations: {', '.join(character['animations'])}"
            animations_surface = self.wrap_text(animations_text, self.small_font, rect.width - 20, self.text_color)
            animations_rect = animations_surface.get_rect()
            animations_rect.centerx = rect.centerx
            animations_rect.y = name_rect.bottom + 15
            self.screen.blit(animations_surface, animations_rect)
    
    def draw_character_info(self, character: Dict[str, Any]):
        """Draw detailed info for selected character"""
        info_y = self.screen_height - 120
        
        # Character abilities or special info
        info_text = f"Selected: {character['name']}"
        info_surface = self.subtitle_font.render(info_text, True, self.title_color)
        info_rect = info_surface.get_rect()
        info_rect.centerx = self.screen_width // 2
        info_rect.y = info_y
        self.screen.blit(info_surface, info_rect)
        
        # Character description (you can expand this)
        descriptions = {
            'gothicvania_hero': "A battle-hardened warrior with sword mastery and agile combat skills.",
            'female_adventurer': "A nimble explorer with dash abilities and graceful movements."
        }
        
        description = descriptions.get(character['id'], "A mysterious character ready for adventure.")
        desc_surface = self.wrap_text(description, self.text_font, self.screen_width - 100, self.text_color)
        desc_rect = desc_surface.get_rect()
        desc_rect.centerx = self.screen_width // 2
        desc_rect.y = info_rect.bottom + 10
        self.screen.blit(desc_surface, desc_rect)
    
    def draw_instructions(self):
        """Draw control instructions"""
        instructions = [
            "Use ARROW KEYS or MOUSE to select character",
            "Press ENTER or CLICK to confirm selection",
            "Press ESC to go back"
        ]
        
        start_y = self.screen_height - 60
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect()
            text_rect.centerx = self.screen_width // 2
            text_rect.y = start_y + i * 20
            self.screen.blit(text, text_rect)
    
    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int, color: tuple) -> pygame.Surface:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Create surface with wrapped text
        line_height = font.get_height()
        surface = pygame.Surface((max_width, len(lines) * line_height), pygame.SRCALPHA)
        
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect()
            line_rect.centerx = max_width // 2
            line_rect.y = i * line_height
            surface.blit(line_surface, line_rect)
        
        return surface

def main():
    """Test the character selection screen"""
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Character Selection Test")
    clock = pygame.time.Clock()
    
    assets_path = Path(__file__).parent.parent / "assets"
    character_selection = CharacterSelection(screen, assets_path)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = character_selection.handle_event(event)
                if result:
                    if result['action'] == 'back':
                        running = False
                    elif result['action'] == 'select':
                        print(f"Selected character: {result['character_name']} (ID: {result['character_id']})")
                        running = False
        
        character_selection.update(dt)
        character_selection.draw()
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
