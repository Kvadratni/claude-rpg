"""
Furniture management for levels
Handles spawning and managing furniture from building templates
"""

try:
    from ..entities.furniture import Furniture
except ImportError:
    from src.entities.furniture import Furniture


class FurnitureManagerMixin:
    """Mixin class for furniture management functionality"""
    
    def spawn_furniture_from_template(self, template, building_x, building_y):
        """Spawn furniture from a building template at the given position"""
        if not hasattr(template, 'furniture_positions'):
            return
        
        for furniture_pos in template.furniture_positions:
            if len(furniture_pos) >= 3:
                rel_x, rel_y, furniture_type = furniture_pos[:3]
                
                # Calculate world position
                world_x = building_x + rel_x
                world_y = building_y + rel_y
                
                # Create furniture entity
                try:
                    furniture = Furniture(world_x, world_y, furniture_type, self.asset_loader)
                    
                    # Add to level's furniture list
                    if not hasattr(self, 'furniture'):
                        self.furniture = []
                    self.furniture.append(furniture)
                    
                    print(f"Spawned {furniture_type} at ({world_x}, {world_y})")
                    
                except ValueError as e:
                    print(f"Warning: Failed to create furniture: {e}")
    
    def add_furniture(self, x, y, furniture_type):
        """Add a single piece of furniture at the specified position"""
        try:
            furniture = Furniture(x, y, furniture_type, self.asset_loader)
            
            if not hasattr(self, 'furniture'):
                self.furniture = []
            self.furniture.append(furniture)
            
            return furniture
        except ValueError as e:
            print(f"Warning: Failed to add furniture: {e}")
            return None
    
    def remove_furniture_at(self, x, y):
        """Remove furniture at the specified position"""
        if not hasattr(self, 'furniture'):
            return False
        
        for furniture in self.furniture[:]:
            if int(furniture.x) == int(x) and int(furniture.y) == int(y):
                self.furniture.remove(furniture)
                return True
        return False
    
    def get_furniture_at(self, x, y):
        """Get furniture at the specified position"""
        if not hasattr(self, 'furniture'):
            return None
        
        for furniture in self.furniture:
            if int(furniture.x) == int(x) and int(furniture.y) == int(y):
                return furniture
        return None
    
    def handle_furniture_interaction(self, player):
        """Handle player interaction with nearby furniture"""
        if not hasattr(self, 'furniture'):
            return False
        
        player_x, player_y = int(player.x), int(player.y)
        
        # Check for furniture within interaction range
        for furniture in self.furniture:
            if furniture.interactable:
                distance = ((furniture.x - player.x) ** 2 + (furniture.y - player.y) ** 2) ** 0.5
                if distance <= 1.5:  # Interaction range
                    return furniture.interact(player)
        
        return False
    
    def get_furniture_collision_at(self, x, y):
        """Check if there's furniture blocking movement at the given position"""
        if not hasattr(self, 'furniture'):
            return False
        
        for furniture in self.furniture:
            if furniture.blocks_movement:
                # Check if position overlaps with furniture bounds
                furniture_left = furniture.x - 0.5
                furniture_right = furniture.x + furniture.width - 0.5
                furniture_top = furniture.y - 0.5
                furniture_bottom = furniture.y + furniture.height - 0.5
                
                if (furniture_left <= x <= furniture_right and 
                    furniture_top <= y <= furniture_bottom):
                    return True
        
        return False