"""
Level data management and serialization
"""

try:
    from ..entities import Entity, NPC, Enemy, Item, Chest
except ImportError:
    from ..entities import Entity, NPC, Enemy, Item, Chest


class LevelDataMixin:
    """Mixin class for level data management and serialization"""
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "name": self.name,
            "tiles": self.tiles,
            "heightmap": self.heightmap,
            "enemies": [enemy.get_save_data() for enemy in self.enemies],
            "npcs": [npc.get_save_data() for npc in self.npcs],
            "items": [item.get_save_data() for item in self.items],
            "objects": [obj.get_save_data() for obj in self.objects],
            "chests": [chest.get_save_data() for chest in self.chests],
            "camera_x": self.camera_x,
            "camera_y": self.camera_y
            # Note: Combat state is not saved as it should reset on load
        }
    
    @classmethod
    def from_save_data(cls, data, player, asset_loader, game=None):
        """Create level from save data"""
        level = cls(data["name"], player, asset_loader, game)
        level.tiles = data["tiles"]
        level.heightmap = data["heightmap"]
        level.camera_x = data["camera_x"]
        level.camera_y = data["camera_y"]
        
        # Reset combat state on load
        level.enemies_in_combat = set()
        level.combat_music_timer = 0
        
        # Recreate entities
        level.enemies = []
        for enemy_data in data["enemies"]:
            enemy = Enemy.from_save_data(enemy_data, asset_loader)
            level.enemies.append(enemy)
        
        level.npcs = []
        for npc_data in data["npcs"]:
            npc = NPC.from_save_data(npc_data, asset_loader)
            level.npcs.append(npc)
        
        level.items = []
        for item_data in data["items"]:
            item = Item.from_save_data(item_data, asset_loader)
            level.items.append(item)
        
        level.objects = []
        for obj_data in data["objects"]:
            obj = Entity.from_save_data(obj_data, asset_loader)
            level.objects.append(obj)
        
        level.chests = []
        for chest_data in data.get("chests", []):  # Use get() for backward compatibility
            chest = Chest.from_save_data(chest_data, asset_loader)
            level.chests.append(chest)
        
        return level