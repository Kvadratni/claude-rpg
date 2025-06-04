"""
Quest Log UI for the RPG
"""

import pygame
from typing import List, Dict, Optional


class QuestLog:
    """Quest log interface for viewing active and available quests"""
    
    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader
        self.show = False
        self.quest_manager = None
        self.selected_quest = None
        self.scroll_offset = 0
        
        # Initialize fonts
        self._init_fonts()
        
        # Quest log dimensions
        self.width = 800
        self.height = 600
        self.padding = 20
        
        # Colors
        self.bg_color = (40, 40, 40)
        self.border_color = (120, 120, 120)
        self.title_color = (255, 255, 255)
        self.quest_active_color = (100, 255, 100)
        self.quest_available_color = (255, 255, 100)
        self.quest_completed_color = (150, 150, 150)
        self.objective_complete_color = (100, 255, 100)
        self.objective_incomplete_color = (255, 255, 255)
        self.description_color = (200, 200, 200)
        
    def _init_fonts(self):
        """Initialize fonts for quest log display"""
        try:
            self.title_font = pygame.font.Font(None, 32)
            self.quest_font = pygame.font.Font(None, 24)
            self.objective_font = pygame.font.Font(None, 20)
            self.description_font = pygame.font.Font(None, 18)
        except:
            self.title_font = pygame.font.Font(None, 32)
            self.quest_font = pygame.font.Font(None, 24)
            self.objective_font = pygame.font.Font(None, 20)
            self.description_font = pygame.font.Font(None, 18)
    
    def set_quest_manager(self, quest_manager):
        """Set the quest manager reference"""
        self.quest_manager = quest_manager
    
    def toggle(self):
        """Toggle quest log visibility"""
        self.show = not self.show
        if self.show and self.asset_loader and hasattr(self.asset_loader, 'audio_manager'):
            self.asset_loader.audio_manager.play_ui_sound("inventory_open")
        elif not self.show and self.asset_loader and hasattr(self.asset_loader, 'audio_manager'):
            self.asset_loader.audio_manager.play_ui_sound("inventory_close")
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input events. Returns True if event was consumed."""
        if not self.show:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                self.toggle()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += 1
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - 5)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset += 5
                return True
        
        return False
    
    def render(self, screen: pygame.Surface):
        """Render the quest log"""
        if not self.show or not self.quest_manager:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Position quest log in center
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        # Draw background with transparency
        quest_surface = pygame.Surface((self.width, self.height))
        quest_surface.set_alpha(240)
        quest_surface.fill(self.bg_color)
        screen.blit(quest_surface, (x, y))
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, (x, y, self.width, self.height), 3)
        
        # Draw title
        title_text = self.title_font.render("Quest Log", True, self.title_color)
        screen.blit(title_text, (x + self.padding, y + 10))
        
        # Draw close instruction
        close_text = self.description_font.render("Press Q or ESC to close", True, self.description_color)
        screen.blit(close_text, (x + self.width - 200, y + 15))
        
        # Content area
        content_y = y + 60
        content_height = self.height - 80
        
        # Get quest data
        active_quests = list(self.quest_manager.active_quests.values())
        available_quests = self.quest_manager.get_available_quests()
        
        # Render quest content
        current_y = content_y
        line_height = 25
        
        # Active Quests Section
        if active_quests:
            section_title = self.quest_font.render("=== Active Quests ===", True, self.quest_active_color)
            if current_y - y < content_height:
                screen.blit(section_title, (x + self.padding, current_y))
            current_y += line_height + 10
            
            for quest in active_quests:
                if current_y - y > content_height:
                    break
                    
                # Quest title
                quest_title = self.quest_font.render(f"• {quest.title}", True, self.quest_active_color)
                screen.blit(quest_title, (x + self.padding, current_y))
                current_y += line_height
                
                # Quest description
                if current_y - y < content_height:
                    desc_text = self.description_font.render(quest.description, True, self.description_color)
                    screen.blit(desc_text, (x + self.padding + 20, current_y))
                    current_y += 20
                
                # Objectives
                for i in range(len(quest.objectives)):
                    if current_y - y > content_height:
                        break
                        
                    objective_text = quest.get_objective_text(i)
                    is_completed = quest.progress[i]["completed"]
                    
                    status_symbol = "✓" if is_completed else "○"
                    color = self.objective_complete_color if is_completed else self.objective_incomplete_color
                    
                    obj_text = self.objective_font.render(f"  {status_symbol} {objective_text}", True, color)
                    screen.blit(obj_text, (x + self.padding + 20, current_y))
                    current_y += 22
                
                current_y += 10  # Space between quests
        
        # Available Quests Section
        if available_quests and current_y - y < content_height:
            current_y += 10
            section_title = self.quest_font.render("=== Available Quests ===", True, self.quest_available_color)
            screen.blit(section_title, (x + self.padding, current_y))
            current_y += line_height + 10
            
            for quest in available_quests:
                if current_y - y > content_height:
                    break
                    
                # Quest title
                quest_title = self.quest_font.render(f"• {quest.title}", True, self.quest_available_color)
                screen.blit(quest_title, (x + self.padding, current_y))
                current_y += line_height
                
                # Quest description
                if current_y - y < content_height:
                    desc_text = self.description_font.render(quest.description, True, self.description_color)
                    screen.blit(desc_text, (x + self.padding + 20, current_y))
                    current_y += 20
                
                # Show objectives preview
                if quest.objectives and current_y - y < content_height:
                    preview_text = self.description_font.render("Objectives:", True, self.description_color)
                    screen.blit(preview_text, (x + self.padding + 20, current_y))
                    current_y += 18
                    
                    for i, objective in enumerate(quest.objectives[:3]):  # Show max 3 objectives
                        if current_y - y > content_height:
                            break
                            
                        obj_preview = f"  • {self._get_objective_preview(objective)}"
                        obj_text = self.description_font.render(obj_preview, True, self.description_color)
                        screen.blit(obj_text, (x + self.padding + 30, current_y))
                        current_y += 16
                
                current_y += 15  # Space between quests
        
        # No quests message
        if not active_quests and not available_quests:
            no_quests_text = self.quest_font.render("No quests available", True, self.description_color)
            text_rect = no_quests_text.get_rect(center=(x + self.width // 2, y + self.height // 2))
            screen.blit(no_quests_text, text_rect)
        
        # Scroll indicator
        if current_y - content_y > content_height:
            scroll_text = self.description_font.render("Use ↑↓ or Page Up/Down to scroll", True, self.description_color)
            screen.blit(scroll_text, (x + self.padding, y + self.height - 25))
    
    def _get_objective_preview(self, objective):
        """Get preview text for an objective"""
        obj_type = objective["type"]
        target = objective.get("target", "")
        amount = objective.get("target", 1) if isinstance(objective.get("target"), int) else 1
        
        if obj_type == "kill":
            return f"Defeat {amount} {target}"
        elif obj_type == "collect":
            return f"Collect {amount} {target}"
        elif obj_type == "talk":
            return f"Talk to {target}"
        elif obj_type == "reach":
            return f"Reach {target}"
        elif obj_type == "equip":
            return f"Equip {target}"
        elif obj_type == "purchase":
            return f"Purchase {target}"
        else:
            return f"{obj_type}: {target}"