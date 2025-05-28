"""
Quest system for the RPG
"""

class Quest:
    """Individual quest class"""
    
    def __init__(self, quest_id, title, description, objectives=None, rewards=None, prerequisites=None):
        self.id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives or []  # List of objective dicts
        self.rewards = rewards or {}  # Dict of reward types and amounts
        self.prerequisites = prerequisites or []  # List of quest IDs that must be completed
        self.status = "available"  # available, active, completed, failed
        self.progress = {}  # Track progress for each objective
        
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
                    if objective["target"] != target_name:
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
        else:
            return f"{objective['type']}: {progress['current']}/{progress['target']}"
    
    def is_completed(self):
        """Check if quest is completed"""
        return self.status == "completed"
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "prerequisites": self.prerequisites,
            "status": self.status,
            "progress": self.progress
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
            data["prerequisites"]
        )
        quest.status = data["status"]
        quest.progress = data["progress"]
        return quest


class QuestManager:
    """Manages all quests in the game"""
    
    def __init__(self, player=None, game_log=None):
        self.player = player
        self.game_log = game_log
        self.quests = {}  # All available quests
        self.active_quests = {}  # Currently active quests
        self.completed_quests = set()  # IDs of completed quests
        
        # Initialize default quests
        self.initialize_quests()
    
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
                if self.game_log:
                    self.game_log.add_message(f"Quest Started: {quest.title}", "quest")
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
                    self.game_log.add_message(f"Quest Completed: {quest.title}", "quest")
        
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
                self.game_log.add_message(f"Received {rewards['gold']} gold!", "reward")
        
        if "item" in rewards:
            # This would need to be implemented to create and give specific items
            if self.game_log:
                self.game_log.add_message(f"Received {rewards['item']}!", "reward")
    
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
            "completed_quests": list(self.completed_quests)
        }
    
    def load_save_data(self, data):
        """Load quest data from save"""
        self.completed_quests = set(data.get("completed_quests", []))
        
        self.active_quests = {}
        for qid, quest_data in data.get("active_quests", {}).items():
            if qid in self.quests:
                quest = Quest.from_save_data(quest_data)
                self.active_quests[qid] = quest