"""
Base Menu Class - Common functionality for all menus
"""

import pygame
import math
import random

class BaseMenu:
    """Base class for all menu types with common functionality"""
    
    def __init__(self, game):
        self.game = game
        self.asset_loader = game.asset_loader
        
        # Get audio manager for music control
        self.audio_manager = getattr(self.asset_loader, 'audio_manager', None)
        
        # Load fonts
        try:
            self.title_font = pygame.font.Font(None, 96)
            self.menu_font = pygame.font.Font(None, 48)
            self.subtitle_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
        except:
            self.title_font = pygame.font.Font(None, 96)
            self.menu_font = pygame.font.Font(None, 48)
            self.subtitle_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
        
        # Load background image
        self.background_image = self.asset_loader.get_image("menu_background")
        if self.background_image:
            print("Menu background loaded successfully!")
        else:
            print("Menu background not found, using procedural background")
        
        # Enhanced color palette
        self.colors = {
            'bg_dark': (15, 15, 25),
            'bg_medium': (25, 25, 40),
            'title_gold': (255, 215, 0),
            'title_shadow': (180, 150, 0),
            'menu_normal': (200, 200, 220),
            'menu_hover': (255, 255, 255),
            'menu_selected': (255, 215, 0),
            'accent_blue': (100, 150, 255),
            'accent_purple': (150, 100, 255),
            'particle_color': (255, 255, 150),
            'border_color': (100, 100, 150)
        }
        
        # Animation variables
        self.time = 0
        self.title_pulse = 0
        self.menu_hover_time = []
        
        # Particle system for background
        self.particles = []
        self.init_particles()
        
        # Background elements
        self.background_stars = []
        self.init_background_stars()
        
        # Mouse support
        self.mouse_hover = -1
        self.menu_rects = []
    
    def init_particles(self):
        """Initialize floating particles for background atmosphere"""
        self.particles = []
        for _ in range(15):
            particle = {
                'x': random.randint(0, 1200),
                'y': random.randint(0, 800),
                'speed_x': random.uniform(-0.5, 0.5),
                'speed_y': random.uniform(-0.8, -0.2),
                'size': random.randint(2, 4),
                'alpha': random.randint(50, 150),
                'pulse_speed': random.uniform(0.02, 0.05)
            }
            self.particles.append(particle)
    
    def init_background_stars(self):
        """Initialize background stars"""
        self.background_stars = []
        for _ in range(50):
            star = {
                'x': random.randint(0, 1200),
                'y': random.randint(0, 800),
                'brightness': random.randint(30, 100),
                'twinkle_speed': random.uniform(0.01, 0.03)
            }
            self.background_stars.append(star)
    
    def update_particles(self):
        """Update particle positions and properties"""
        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            # Pulse effect
            particle['alpha'] += math.sin(self.time * particle['pulse_speed']) * 2
            particle['alpha'] = max(30, min(150, particle['alpha']))
            
            # Reset particles that go off screen
            if particle['y'] < -10:
                particle['y'] = 810
                particle['x'] = random.randint(0, 1200)
            if particle['x'] < -10:
                particle['x'] = 1210
            elif particle['x'] > 1210:
                particle['x'] = -10
    
    def update_background_stars(self):
        """Update background star twinkling"""
        for star in self.background_stars:
            star['brightness'] += math.sin(self.time * star['twinkle_speed']) * 3
            star['brightness'] = max(20, min(100, star['brightness']))
    
    def update(self):
        """Update menu animations"""
        self.time += 0.1
        self.title_pulse = (math.sin(self.time * 0.1) + 1) * 0.5
        self.update_particles()
        self.update_background_stars()
        
        # Update hover time for menu items
        for i in range(len(self.menu_hover_time)):
            if i == self.mouse_hover:
                self.menu_hover_time[i] = min(1.0, self.menu_hover_time[i] + 0.1)
            else:
                self.menu_hover_time[i] = max(0.0, self.menu_hover_time[i] - 0.05)
    
    def render_gradient_background(self, screen, width, height):
        """Render gradient background"""
        if self.background_image:
            # Scale background image to fit screen
            scaled_bg = pygame.transform.scale(self.background_image, (width, height))
            screen.blit(scaled_bg, (0, 0))
            
            # Add subtle overlay for better text readability
            overlay = pygame.Surface((width, height))
            overlay.set_alpha(100)
            overlay.fill(self.colors['bg_dark'])
            screen.blit(overlay, (0, 0))
        else:
            # Procedural gradient background
            for y in range(height):
                ratio = y / height
                r = int(self.colors['bg_dark'][0] + (self.colors['bg_medium'][0] - self.colors['bg_dark'][0]) * ratio)
                g = int(self.colors['bg_dark'][1] + (self.colors['bg_medium'][1] - self.colors['bg_dark'][1]) * ratio)
                b = int(self.colors['bg_dark'][2] + (self.colors['bg_medium'][2] - self.colors['bg_dark'][2]) * ratio)
                pygame.draw.line(screen, (r, g, b), (0, y), (width, y))
    
    def render_background_stars(self, screen):
        """Render twinkling background stars"""
        for star in self.background_stars:
            color = (star['brightness'], star['brightness'], star['brightness'])
            pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), 1)
    
    def render_particles(self, screen):
        """Render floating particles"""
        for particle in self.particles:
            color = (*self.colors['particle_color'], int(particle['alpha']))
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
            screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def start_menu_music(self):
        """Start playing menu music"""
        if self.audio_manager:
            current_music = self.audio_manager.get_current_music()
            if current_music != 'menu':
                self.audio_manager.play_music('menu', loop=True, fade_in_ms=1000)
    
    def start_game_music(self):
        """Start playing game music"""
        if self.audio_manager:
            current_music = self.audio_manager.get_current_music()
            if current_music != 'game':
                self.audio_manager.play_music('game', loop=True, fade_in_ms=1000)
    
    def update_mouse_hover(self, mouse_x, mouse_y):
        """Update which menu item the mouse is hovering over"""
        self.mouse_hover = -1
        for i, rect in enumerate(self.menu_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                self.mouse_hover = i
                break
    
    def render_instructions(self, screen, width, height, instruction_text):
        """Render instructions with better styling"""
        # Background for instructions
        instruction_surface = self.small_font.render(instruction_text, True, self.colors['menu_normal'])
        instruction_rect = instruction_surface.get_rect(center=(width // 2, height - 40))
        
        # Semi-transparent background
        bg_rect = instruction_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*self.colors['bg_dark'], 180))
        screen.blit(bg_surface, bg_rect)
        
        # Border
        pygame.draw.rect(screen, self.colors['border_color'], bg_rect, 1)
        
        screen.blit(instruction_surface, instruction_rect)
