"""
Entity update and management logic
"""

import random
try:
    from ..entities import Item
except ImportError:
    from ..entities import Item


class EntityManagerMixin:
    """Mixin class for entity management functionality"""
    
    def update_entities(self):
        """Update all entities in the level"""
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self, self.player)
            
            # Track combat state for music
            enemy_in_combat = enemy.state in ["chasing", "attacking"]
            enemy_id = id(enemy)  # Use object id as unique identifier
            
            if enemy_in_combat:
                if enemy_id not in self.enemies_in_combat:
                    self.enemies_in_combat.add(enemy_id)
                    # Start combat music if this is the first enemy to enter combat
                    if len(self.enemies_in_combat) == 1:
                        audio = getattr(self.asset_loader, 'audio_manager', None)
                        if audio:
                            audio.start_combat_music()
            else:
                if enemy_id in self.enemies_in_combat:
                    self.enemies_in_combat.discard(enemy_id)
            
            # Check if enemy is dead
            if enemy.health <= 0:
                self._handle_enemy_death(enemy, enemy_id)
        
        # Handle combat music transitions
        self._handle_combat_music()
        
        # Update NPCs
        for npc in self.npcs:
            npc.update((self.player.x, self.player.y), self)
        
        # Update items
        for item in self.items:
            item.update(self)
    
    def _handle_enemy_death(self, enemy, enemy_id):
        """Handle enemy death and loot generation"""
        # Remove from combat tracking if dead
        if enemy_id in self.enemies_in_combat:
            self.enemies_in_combat.discard(enemy_id)
        
        # Update quest progress for enemy kills
        if hasattr(self.player, 'game') and hasattr(self.player.game, 'quest_manager'):
            quest_manager = self.player.game.quest_manager
            quest_manager.update_quest_progress("kill", enemy.name)
            quest_manager.update_quest_progress("kill", "any")  # For generic kill quests
        
        self.enemies.remove(enemy)
        self.player.gain_experience(enemy.experience)
        
        # Generate loot drops
        self._generate_enemy_loot(enemy)
    
    def _generate_enemy_loot(self, enemy):
        """Generate loot drops from defeated enemy"""
        # Improved loot drops - more frequent and varied
        drop_chance = 0.9 if enemy.is_boss else 0.8  # 90% for bosses, 80% for regular enemies
        if random.random() < drop_chance:
            # Multiple possible drops for bosses
            num_drops = 2 if enemy.is_boss else 1
            
            for _ in range(num_drops):
                item_type = random.choice(["consumable", "weapon", "armor", "misc"])
                item = self._create_loot_item(enemy, item_type)
                
                if item:
                    self.items.append(item)
                    
                    # Offset multiple drops slightly
                    if num_drops > 1:
                        item.x += random.uniform(-0.5, 0.5)
                        item.y += random.uniform(-0.5, 0.5)
    
    def _create_loot_item(self, enemy, item_type):
        """Create a specific type of loot item"""
        if item_type == "consumable":
            return self._create_consumable_loot(enemy)
        elif item_type == "weapon":
            return self._create_weapon_loot(enemy)
        elif item_type == "armor":
            return self._create_armor_loot(enemy)
        elif item_type == "misc":
            return self._create_misc_loot(enemy)
        return None
    
    def _create_consumable_loot(self, enemy):
        """Create consumable loot item"""
        potion_types = ["Health Potion", "Stamina Potion", "Mana Potion", "Antidote", "Strength Potion"]
        potion_type = random.choice(potion_types)
        
        if potion_type == "Health Potion":
            return Item(enemy.x, enemy.y, "Health Potion", item_type="consumable", 
                      effect={"health": 50}, asset_loader=self.asset_loader)
        elif potion_type == "Stamina Potion":
            return Item(enemy.x, enemy.y, "Stamina Potion", item_type="consumable", 
                      effect={"stamina": 30}, asset_loader=self.asset_loader)
        elif potion_type == "Mana Potion":
            return Item(enemy.x, enemy.y, "Mana Potion", item_type="consumable", 
                      effect={"mana": 40}, asset_loader=self.asset_loader)
        elif potion_type == "Antidote":
            return Item(enemy.x, enemy.y, "Antidote", item_type="consumable", 
                      effect={"cure_poison": True}, asset_loader=self.asset_loader)
        else:  # Strength Potion
            return Item(enemy.x, enemy.y, "Strength Potion", item_type="consumable", 
                      effect={"damage_boost": 10, "duration": 60}, asset_loader=self.asset_loader)
    
    def _create_weapon_loot(self, enemy):
        """Create weapon loot item"""
        weapon_names = ["Iron Sword", "Steel Axe", "Bronze Mace", "Silver Dagger", "War Hammer", 
                      "Magic Bow", "Crystal Staff", "Throwing Knife", "Crossbow"]
        weapon_name = random.choice(weapon_names)
        damage_bonus = (10 if enemy.is_boss else 5) + random.randint(0, 10)
        return Item(enemy.x, enemy.y, weapon_name, item_type="weapon", 
                  effect={"damage": damage_bonus}, asset_loader=self.asset_loader)
    
    def _create_armor_loot(self, enemy):
        """Create armor loot item"""
        armor_names = ["Leather Armor", "Chain Mail", "Plate Armor", "Studded Leather", "Scale Mail",
                     "Dragon Scale Armor", "Mage Robes", "Royal Armor"]
        armor_name = random.choice(armor_names)
        defense_bonus = (8 if enemy.is_boss else 4) + random.randint(0, 8)
        return Item(enemy.x, enemy.y, armor_name, item_type="armor", 
                  effect={"defense": defense_bonus}, asset_loader=self.asset_loader)
    
    def _create_misc_loot(self, enemy):
        """Create miscellaneous loot item"""
        misc_items = [
            ("Gold Ring", {"magic_resistance": 5}),
            ("Magic Scroll", {"spell_power": 15}),
            ("Crystal Gem", {"value": 100})
        ]
        item_name, effect = random.choice(misc_items)
        return Item(enemy.x, enemy.y, item_name, item_type="misc", 
                  effect=effect, asset_loader=self.asset_loader)
    
    def _handle_combat_music(self):
        """Handle combat music transitions"""
        if len(self.enemies_in_combat) == 0:
            # No enemies in combat, start timer to end combat music
            self.combat_music_timer += 1
            if self.combat_music_timer >= 180:  # 3 seconds at 60 FPS
                audio = getattr(self.asset_loader, 'audio_manager', None)
                if audio and audio.is_combat_music_active():
                    audio.end_combat_music()
                self.combat_music_timer = 0
        else:
            # Reset timer if combat is active
            self.combat_music_timer = 0