"""
Quest system for the RPG with dynamic spawning support
"""

import random
from typing import Dict, List, Optional, Tuple, Any


class Quest:
    """Individual quest class with dynamic spawning support"""
    
    def __init__(self, quest_id, title, description, objectives=None, rewards=None, prerequisites=None, spawn_data=None):
        self.id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives or []  # List of objective dicts
        self.rewards = rewards or {}  # Dict of reward types and amounts
        self.prerequisites = prerequisites or []  # List of quest IDs that must be completed
        self.spawn_data = spawn_data or {}  # Data for dynamic spawning
        self.status = "available"  # available, active, completed, failed
        self.progress = {}  # Track progress for each objective
        self.spawned_entities = []  # Track entities spawned for this quest
        
        # Initialize progress tracking
        for i, objective in enumerate(self.objectives):
            self.progress[i] = {
                "completed": False,
                "current": 0,
                "target": objective.get("target", 1)
            }
    
    def can_start(self, completed_quests):
        """Check if quest can be started based on prerequisites"""
        if self.status != "available":
            return False
        
        for prereq in self.prerequisites:
            if prereq not in completed_quests:
                return False
        
        return True
    
    def start(self):
        """Start the quest"""
        if self.status == "available":
            self.status = "active"
            return True
        return False
    
    def update_progress(self, objective_type, target_name=None, amount=1):
        """Update progress for matching objectives"""
        quest_completed = False
        
        for i, objective in enumerate(self.objectives):
            if objective["type"] == objective_type:
                # Check if target matches (if specified)
                if "target" in objective and target_name:
                    if objective["target"] != target_name and objective["target"] != "any":
                        continue
                
                # Update progress
                if not self.progress[i]["completed"]:
                    self.progress[i]["current"] += amount
                    
                    # Check if objective is completed
                    if self.progress[i]["current"] >= self.progress[i]["target"]:
                        self.progress[i]["completed"] = True
                        self.progress[i]["current"] = self.progress[i]["target"]
        
        # Check if all objectives are completed
        if all(self.progress[i]["completed"] for i in range(len(self.objectives))):
            self.status = "completed"
            quest_completed = True
        
        return quest_completed
    
    def get_objective_text(self, index):
        """Get formatted text for an objective"""
        if index >= len(self.objectives):
            return ""
        
        objective = self.objectives[index]
        progress = self.progress[index]
        
        if objective["type"] == "kill":
            target = objective.get("target", "enemies")
            return f"Defeat {progress['current']}/{progress['target']} {target}"
        elif objective["type"] == "collect":
            target = objective.get("target", "items")
            return f"Collect {progress['current']}/{progress['target']} {target}"
        elif objective["type"] == "talk":
            target = objective.get("target", "NPC")
            return f"Talk to {target}"
        elif objective["type"] == "reach":
            target = objective.get("target", "location")
            return f"Reach {target}"
        elif objective["type"] == "equip":
            target = objective.get("target", "equipment")
            return f"Equip {target}"
        elif objective["type"] == "purchase":
            target = objective.get("target", "item")
            return f"Purchase {target}"
        else:
            return f"{objective['type']}: {progress['current']}/{progress['target']}"
    
    def is_completed(self):
        """Check if quest is completed"""
        return self.status == "completed"
    
    def get_spawn_requirements(self):
        """Get what needs to be spawned for this quest"""
        return self.spawn_data
    
    def add_spawned_entity(self, entity_id, entity_type, location):
        """Track a spawned entity for this quest"""
        self.spawned_entities.append({
            "id": entity_id,
            "type": entity_type,
            "location": location
        })
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "prerequisites": self.prerequisites,
            "spawn_data": self.spawn_data,
            "status": self.status,
            "progress": self.progress,
            "spawned_entities": self.spawned_entities
        }
    
    @classmethod
    def from_save_data(cls, data):
        """Create quest from save data"""
        quest = cls(
            data["id"],
            data["title"],
            data["description"],
            data["objectives"],
            data["rewards"],
            data["prerequisites"],
            data.get("spawn_data", {})
        )
        quest.status = data["status"]
        quest.progress = data["progress"]
        quest.spawned_entities = data.get("spawned_entities", [])
        return quest


class QuestManager:
    """Manages all quests in the game with dynamic spawning support"""
    
    def __init__(self, player=None, game_log=None, level=None):
        self.player = player
        self.game_log = game_log
        self.level = level  # Reference to current level for spawning
        self.quests = {}  # All available quests
        self.active_quests = {}  # Currently active quests
        self.completed_quests = set()  # IDs of completed quests
        
        # Initialize default quests
        self.initialize_quests()
    
    def set_level(self, level):
        """Set the current level reference for spawning"""
        self.level = level
    
    def initialize_quests(self):
        """Initialize the game's quest system"""
        # Main story quest
        main_quest = Quest(
            "main_story",
            "The Orc Threat",
            "The village is under threat from an Orc Chief and his minions. Defeat them to save the village.",
            objectives=[
                {"type": "kill", "target": "Goblin", "target": 5},
                {"type": "kill", "target": "Orc Chief", "target": 1}
            ],
            rewards={
                "experience": 500,
                "gold": 200,
                "item": "Hero's Sword"
            }
        )
        self.quests["main_story"] = main_quest
        
        # Tutorial quest
        tutorial_quest = Quest(
            "tutorial",
            "Getting Started",
            "Learn the basics of survival in this dangerous world.",
            objectives=[
                {"type": "collect", "target": "Health Potion", "target": 1},
                {"type": "kill", "target": "any", "target": 1}
            ],
            rewards={
                "experience": 50,
                "gold": 25
            }
        )
        self.quests["tutorial"] = tutorial_quest
        
        # Equipment quest
        equipment_quest = Quest(
            "first_equipment",
            "Arm Yourself",
            "Find proper equipment to survive the dangers ahead.",
            objectives=[
                {"type": "equip", "target": "weapon", "target": 1},
                {"type": "equip", "target": "armor", "target": 1}
            ],
            rewards={
                "experience": 75,
                "gold": 50
            },
            prerequisites=["tutorial"]
        )
        self.quests["first_equipment"] = equipment_quest
        
        # Shopping quest
        shopping_quest = Quest(
            "first_purchase",
            "Support Local Business",
            "Visit the shopkeeper and make your first purchase.",
            objectives=[
                {"type": "talk", "target": "Shopkeeper", "target": 1},
                {"type": "purchase", "target": "any", "target": 1}
            ],
            rewards={
                "experience": 25,
                "gold": 30
            }
        )
        self.quests["first_purchase"] = shopping_quest
    
    def create_dynamic_quest(self, quest_data):
        """Create a quest from AI NPC with dynamic spawning"""
        quest_id = f"dynamic_{len(self.quests)}"
        
        # Parse quest data from AI
        title = quest_data.get("title", "Unknown Quest")
        description = quest_data.get("description", "A mysterious quest...")
        objectives = quest_data.get("objectives", [])
        rewards = quest_data.get("rewards", {})
        spawn_data = quest_data.get("spawn_data", {})
        
        # Create the quest
        quest = Quest(
            quest_id,
            title,
            description,
            objectives,
            rewards,
            spawn_data=spawn_data
        )
        
        # Add to available quests
        self.quests[quest_id] = quest
        
        # Start the quest immediately (AI-generated quests are auto-accepted)
        if quest.start():
            self.active_quests[quest_id] = quest
            
            # Handle dynamic spawning
            self._handle_quest_spawning(quest)
            
            if self.game_log:
                self.game_log.add_message(f"📜 New Quest: {quest.title}", "quest")
                self.game_log.add_message(f"📝 {quest.description}", "quest")
        
        return quest_id
    
    def _handle_quest_spawning(self, quest):
        """Handle spawning entities for a quest"""
        if not self.level or not quest.spawn_data:
            return
        
        spawn_data = quest.spawn_data
        
        for spawn_info in spawn_data.get("spawns", []):
            entity_type = spawn_info.get("type")
            count = spawn_info.get("count", 1)
            direction = spawn_info.get("direction", "North")
            distance_range = spawn_info.get("distance", (20, 40))
            special_items = spawn_info.get("items", [])
            
            for _ in range(count):
                # Find spawn location
                from .ui.compass import DirectionHelper
                spawn_x, spawn_y = DirectionHelper.find_spawn_location(
                    self.player.x if self.player else 100,
                    self.player.y if self.player else 100,
                    direction,
                    distance_range,
                    (self.level.width, self.level.height) if self.level else None
                )
                
                # Spawn the entity
                spawned_entity = self._spawn_entity(entity_type, spawn_x, spawn_y, special_items)
                
                if spawned_entity:
                    quest.add_spawned_entity(spawned_entity.id if hasattr(spawned_entity, 'id') else str(id(spawned_entity)), 
                                           entity_type, (spawn_x, spawn_y))
                    
                    # Log the spawn
                    if self.game_log:
                        direction_text = f"to the {direction.lower()}"
                        self.game_log.add_message(f"🎯 {entity_type} spotted {direction_text}!", "quest")
    
    def _spawn_entity(self, entity_type, x, y, special_items=None):
        """Spawn a specific entity type at the given location"""
        if not self.level:
            return None
        
        try:
            if entity_type.lower() in ["bandit", "bandits"]:
                # Spawn a bandit enemy
                from .entities.enemy import Enemy
                bandit = Enemy(x, y, "Bandit", enemy_type="bandit", asset_loader=self.level.asset_loader)
                
                # Give special items if specified
                if special_items:
                    for item_name in special_items:
                        # Create the item and add to bandit's inventory
                        from .entities.item import Item
                        item = Item(x, y, item_name, item_type="misc", asset_loader=self.level.asset_loader)
                        if hasattr(bandit, 'inventory'):
                            bandit.inventory.append(item)
                        else:
                            bandit.inventory = [item]
                
                # Add to level
                self.level.enemies.append(bandit)
                return bandit
                
            elif entity_type.lower() in ["chest", "treasure"]:
                # Spawn a treasure chest
                from .entities.chest import Chest
                chest = Chest(x, y, asset_loader=self.level.asset_loader)
                
                # Add special items to chest
                if special_items:
                    for item_name in special_items:
                        from .entities.item import Item
                        item = Item(x, y, item_name, item_type="misc", asset_loader=self.level.asset_loader)
                        chest.add_item(item)
                
                self.level.chests.append(chest)
                return chest
                
            elif entity_type.lower() in ["item", "object"]:
                # Spawn an item directly
                if special_items:
                    from .entities.item import Item
                    item = Item(x, y, special_items[0], item_type="misc", asset_loader=self.level.asset_loader)
                    self.level.items.append(item)
                    return item
        
        except Exception as e:
            print(f"❌ [QuestManager] Failed to spawn {entity_type}: {e}")
            return None
        
        return None
    
    def get_available_quests(self):
        """Get quests that can be started"""
        available = []
        for quest in self.quests.values():
            if quest.can_start(self.completed_quests):
                available.append(quest)
        return available
    
    def start_quest(self, quest_id):
        """Start a quest"""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            if quest.start():
                self.active_quests[quest_id] = quest
                
                # Handle spawning for this quest
                self._handle_quest_spawning(quest)
                
                if self.game_log:
                    self.game_log.add_message(f"📜 Quest Started: {quest.title}", "quest")
                return True
        return False
    
    def update_quest_progress(self, event_type, target=None, amount=1):
        """Update progress for all active quests"""
        completed_quests = []
        
        for quest_id, quest in self.active_quests.items():
            if quest.update_progress(event_type, target, amount):
                # Quest completed
                completed_quests.append(quest_id)
                self.completed_quests.add(quest_id)
                
                # Give rewards
                self.give_rewards(quest)
                
                if self.game_log:
                    self.game_log.add_message(f"🎉 Quest Completed: {quest.title}", "quest")
        
        # Remove completed quests from active list
        for quest_id in completed_quests:
            del self.active_quests[quest_id]
        
        return len(completed_quests) > 0
    
    def give_rewards(self, quest):
        """Give quest rewards to player"""
        if not self.player:
            return
        
        rewards = quest.rewards
        
        if "experience" in rewards:
            self.player.gain_experience(rewards["experience"])
        
        if "gold" in rewards:
            self.player.gold += rewards["gold"]
            if self.game_log:
                self.game_log.add_message(f"💰 Received {rewards['gold']} gold!", "reward")
        
        if "item" in rewards:
            # Create and give the reward item
            try:
                from .entities.item import Item
                item = Item(self.player.x, self.player.y, rewards["item"], 
                           item_type="reward", asset_loader=self.level.asset_loader if self.level else None)
                if self.player.add_item(item):
                    if self.game_log:
                        self.game_log.add_message(f"🎁 Received {rewards['item']}!", "reward")
            except Exception as e:
                print(f"❌ [QuestManager] Failed to give reward item: {e}")
                if self.game_log:
                    self.game_log.add_message(f"🎁 Received {rewards['item']}!", "reward")
    
    def get_quest_log_text(self):
        """Get formatted text for quest log display"""
        lines = []
        
        if self.active_quests:
            lines.append("=== Active Quests ===")
            for quest in self.active_quests.values():
                lines.append(f"• {quest.title}")
                for i in range(len(quest.objectives)):
                    objective_text = quest.get_objective_text(i)
                    status = "✓" if quest.progress[i]["completed"] else "○"
                    lines.append(f"  {status} {objective_text}")
                lines.append("")
        
        available = self.get_available_quests()
        if available:
            lines.append("=== Available Quests ===")
            for quest in available:
                lines.append(f"• {quest.title}")
                lines.append(f"  {quest.description}")
                lines.append("")
        
        return lines
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "active_quests": {qid: quest.get_save_data() for qid, quest in self.active_quests.items()},
            "completed_quests": list(self.completed_quests),
            "all_quests": {qid: quest.get_save_data() for qid, quest in self.quests.items()}
        }
    
    def load_save_data(self, data):
        """Load quest data from save"""
        self.completed_quests = set(data.get("completed_quests", []))
        
        # Load all quests (including dynamic ones)
        if "all_quests" in data:
            self.quests = {}
            for qid, quest_data in data["all_quests"].items():
                self.quests[qid] = Quest.from_save_data(quest_data)
        
        # Load active quests
        self.active_quests = {}
        for qid, quest_data in data.get("active_quests", {}).items():
            if qid in self.quests:
                quest = Quest.from_save_data(quest_data)
                self.active_quests[qid] = quest