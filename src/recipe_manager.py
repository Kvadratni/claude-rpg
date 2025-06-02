"""
Goose Recipe Manager for AI NPCs
Loads and manages YAML recipe files for different NPC types
"""

import os
import yaml
import subprocess
import tempfile
from typing import Dict, Optional

class GooseRecipeManager:
    """Manages Goose recipes for different NPC types"""
    
    def __init__(self, recipes_dir: str = "recipes"):
        print(f"🔧 [RecipeManager] Initializing with recipes_dir: {recipes_dir}")
        self.recipes_dir = recipes_dir
        self.recipes = {}
        self.load_recipes()
        print(f"🔧 [RecipeManager] Initialization complete, loaded {len(self.recipes)} recipes")
    
    def load_recipes(self):
        """Load all recipe files from the recipes directory"""
        print(f"🔧 [RecipeManager] Loading recipes from: {self.recipes_dir}")
        if not os.path.exists(self.recipes_dir):
            print(f"⚠️  [RecipeManager] Recipes directory '{self.recipes_dir}' not found")
            return
        
        recipe_files = [f for f in os.listdir(self.recipes_dir) if f.endswith('.yaml') or f.endswith('.yml')]
        print(f"🔧 [RecipeManager] Found {len(recipe_files)} recipe files: {recipe_files}")
        
        for filename in recipe_files:
            recipe_path = os.path.join(self.recipes_dir, filename)
            print(f"🔧 [RecipeManager] Loading recipe file: {filename}")
            try:
                with open(recipe_path, 'r') as f:
                    recipe_data = yaml.safe_load(f)
                
                recipe_name = recipe_data.get('title', '').lower().replace(' ', '_').replace('_npc', '')
                if recipe_name:
                    self.recipes[recipe_name] = recipe_data
                    print(f"✅ [RecipeManager] Loaded recipe: {recipe_name} from {filename}")
                else:
                    print(f"⚠️  [RecipeManager] Recipe file {filename} missing title field")
                    
            except Exception as e:
                print(f"❌ [RecipeManager] Error loading recipe {filename}: {e}")
    
    def get_recipe(self, recipe_name: str) -> Optional[Dict]:
        """Get a specific recipe by name"""
        return self.recipes.get(recipe_name)
    
    def list_recipes(self) -> list:
        """List all available recipe names"""
        return list(self.recipes.keys())
    
    def get_npc_recipe(self, npc_name: str) -> Optional[str]:
        """Map NPC names to recipe names"""
        print(f"🔧 [RecipeManager] Looking for recipe for NPC: '{npc_name}'")
        
        # Mapping from NPC names to recipe names
        npc_to_recipe = {
            "Village Elder": "village_elder",
            "Elder": "village_elder",
            "Master Merchant": "master_merchant",
            "Merchant": "master_merchant",
            "Shopkeeper": "master_merchant",
            "Guard Captain": "guard_captain",
            "Guard": "guard_captain",
            "Captain": "guard_captain",
            "Tavern Keeper": "tavern_keeper",
            "Innkeeper": "tavern_keeper",
            "Barkeeper": "tavern_keeper",
            "Blacksmith": "blacksmith",
            "Smith": "blacksmith",
            "Weaponsmith": "blacksmith",
            "Healer": "healer",
            "Cleric": "healer",
            "Herbalist": "healer",
        }
        
        # Try exact match first
        if npc_name in npc_to_recipe:
            recipe_name = npc_to_recipe[npc_name]
            print(f"✅ [RecipeManager] Found exact match: '{npc_name}' -> '{recipe_name}'")
            return recipe_name
        
        # Try partial matches
        for npc_key, recipe_name in npc_to_recipe.items():
            if npc_key.lower() in npc_name.lower() or npc_name.lower() in npc_key.lower():
                print(f"✅ [RecipeManager] Found partial match: '{npc_name}' -> '{recipe_name}' (via '{npc_key}')")
                return recipe_name
        
        print(f"❌ [RecipeManager] No recipe found for NPC: '{npc_name}'")
        print(f"🔧 [RecipeManager] Available recipes: {list(self.recipes.keys())}")
        return None
    
    def run_recipe(self, recipe_name: str, user_message: str, context: str = "") -> str:
        """Run a Goose recipe with the given message and context"""
        print(f"🔧 [RecipeManager] Running recipe '{recipe_name}' with message: '{user_message[:50]}...'")
        print(f"🔧 [RecipeManager] Context: '{context}'")
        
        recipe = self.get_recipe(recipe_name)
        if not recipe:
            print(f"❌ [RecipeManager] Recipe '{recipe_name}' not found")
            return f"*{recipe_name} looks confused*"
        
        try:
            # Use goose run with the recipe file directly
            recipe_file = None
            print(f"🔧 [RecipeManager] Searching for recipe file for '{recipe_name}'")
            
            for filename in os.listdir(self.recipes_dir):
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    recipe_path = os.path.join(self.recipes_dir, filename)
                    with open(recipe_path, 'r') as f:
                        recipe_data = yaml.safe_load(f)
                    
                    title = recipe_data.get('title', '').lower().replace(' ', '_').replace('_npc', '')
                    if title == recipe_name:
                        recipe_file = recipe_path
                        print(f"✅ [RecipeManager] Found recipe file: {recipe_file}")
                        break
            
            if not recipe_file:
                print(f"❌ [RecipeManager] Recipe file not found for '{recipe_name}'")
                return f"*{recipe_name} seems distracted*"
            
            # Set up environment
            env = os.environ.copy()
            env["GOOSE_MODEL"] = "goose-gpt-4o-mini"
            print(f"🔧 [RecipeManager] Using model: {env.get('GOOSE_MODEL')}")
            
            # Run goose with the recipe and capture output to a file
            import tempfile
            import time
            
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as output_file:
                output_file_path = output_file.name
            
            cmd_str = f"goose run --recipe {recipe_file} --params 'message={user_message}' --params 'context={context}' --no-session > {output_file_path} 2>&1 &"
            
            print(f"🔧 [RecipeManager] Executing command: {cmd_str}")
            
            # Run the command in background
            subprocess.run(cmd_str, env=env, shell=True)
            
            # Wait for the process to complete and output to be written
            max_wait = 60  # Maximum wait time in seconds
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                
                # Check if file has content and if it looks complete
                try:
                    with open(output_file_path, 'r') as f:
                        content = f.read()
                    
                    # If we have content and it doesn't end with a system message, it might be complete
                    if content and len(content) > 500:  # More than just the loading message
                        # Check if it has an AI response (look for content after "working directory:")
                        if "working directory:" in content:
                            lines_after_wd = content.split("working directory:")[-1].strip()
                            if lines_after_wd and len(lines_after_wd) > 50:
                                print(f"🔧 [RecipeManager] Found complete response after {wait_time}s")
                                break
                except:
                    pass
            
            # Read the final output from the file
            try:
                with open(output_file_path, 'r') as f:
                    stdout = f.read()
                returncode = 0  # Assume success if we got here
                
                print(f"🔧 [RecipeManager] Command completed, waited {wait_time}s")
                print(f"🔧 [RecipeManager] stdout length: {len(stdout)}")
                
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(output_file_path)
                except:
                    pass
            
            if returncode == 0:
                print(f"🔧 [RecipeManager] Raw output length: {len(stdout)} chars")
                response = self._parse_goose_output(stdout)
                print(f"🔧 [RecipeManager] Parsed response: '{response[:100]}...'")
                cleaned_response = self._clean_response(response, recipe_name)
                print(f"✅ [RecipeManager] Final response: '{cleaned_response}'")
                return cleaned_response
            else:
                print(f"❌ [RecipeManager] Goose error for recipe '{recipe_name}': return code {returncode}")
                return f"*{recipe_name} takes a moment to think*"
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ [RecipeManager] Timeout expired for recipe '{recipe_name}'")
            return f"*{recipe_name} takes a long moment to consider your words*"
        except Exception as e:
            print(f"❌ [RecipeManager] Recipe execution error for '{recipe_name}': {e}")
            return f"*{recipe_name} seems momentarily distracted*"
    
    def _parse_goose_output(self, output: str) -> str:
        """Parse Goose CLI output to extract the AI response"""
        import re
        
        print(f"🔧 [RecipeManager] Raw goose output:\n{output}")
        
        # Remove all ANSI color codes first
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        lines = clean_output.strip().split('\n')
        response_lines = []
        
        # Skip system messages and find the actual AI response
        skip_patterns = [
            r'Loading recipe:',
            r'Description:',
            r'Parameters used to load this recipe:',
            r'recipe_dir \(built-in\):',
            r'running without session',
            r'working directory:',
            r'provider:',
            r'model:',
            r'logging to',
            r'context:',
            r'message:'
        ]
        
        # Look for the actual AI response content
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any skip pattern
            should_skip = any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns)
            if should_skip:
                continue
            
            # Skip action text (lines that start and end with *)
            if line.startswith('*') and line.endswith('*'):
                continue
                
            # This looks like actual AI response content
            if line and len(line) > 5:
                response_lines.append(line)
        
        response = ' '.join(response_lines) if response_lines else ""
        print(f"🔧 [RecipeManager] Extracted response: '{response}'")
        return response
    
    def _clean_response(self, response: str, recipe_name: str) -> str:
        """Clean up AI response to be more NPC-like"""
        import re
        
        if not response or len(response.strip()) < 3:
            return f"Greetings, I am {recipe_name.replace('_', ' ').title()}."
        
        # Remove common artifacts
        response = response.strip()
        response = re.sub(r'\*.*?\*', '', response)  # Remove action text
        response = re.sub(r'\[.*?\]', '', response)  # Remove bracketed text
        
        # Remove AI-like phrases
        ai_phrases = [
            "As an AI", "I'm an AI", "I cannot", "I don't have the ability",
            "I'm not able to", "I can't actually", "In this game", "As your"
        ]
        
        for phrase in ai_phrases:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        response = response.strip()
        
        # Ensure it's not empty after cleaning
        if not response or len(response) < 5:
            return f"Greetings, traveler. I am {recipe_name.replace('_', ' ').title()}."
        
        # Ensure it ends with punctuation
        if not response.endswith(('.', '!', '?')):
            response += "."
        
        return response


# Enhanced integration class that uses recipes
class RecipeBasedGooseIntegration:
    """Goose integration that uses recipe files for NPC personalities"""
    
    def __init__(self, npc_name: str, recipes_dir: str = "recipes"):
        print(f"🔧 [RecipeIntegration] Initializing for NPC: '{npc_name}' with recipes_dir: '{recipes_dir}'")
        self.npc_name = npc_name
        self.conversation_history = []
        self.recipe_manager = GooseRecipeManager(recipes_dir)
        self.recipe_name = self.recipe_manager.get_npc_recipe(npc_name)
        
        if self.recipe_name:
            print(f"✅ [RecipeIntegration] {npc_name} using recipe: {self.recipe_name}")
        else:
            print(f"⚠️  [RecipeIntegration] No recipe found for {npc_name}, available recipes: {self.recipe_manager.list_recipes()}")
    
    def send_message(self, message: str, context: str = "") -> str:
        """Send message using the appropriate recipe"""
        print(f"🔧 [RecipeIntegration] send_message called for {self.npc_name}")
        print(f"🔧 [RecipeIntegration] Message: '{message}', Context: '{context}'")
        
        if not self.recipe_name:
            print(f"❌ [RecipeIntegration] No recipe available for {self.npc_name}")
            return f"*{self.npc_name} nods thoughtfully*"
        
        try:
            print(f"🔧 [RecipeIntegration] Calling recipe_manager.run_recipe for {self.recipe_name}")
            response = self.recipe_manager.run_recipe(self.recipe_name, message, context)
            self.conversation_history.append({"player": message, "npc": response})
            print(f"✅ [RecipeIntegration] Successfully got response for {self.npc_name}: '{response[:50]}...'")
            return response
        except Exception as e:
            print(f"❌ [RecipeIntegration] Recipe integration error for {self.npc_name}: {e}")
            return f"*{self.npc_name} seems momentarily confused*"
    
    def get_available_recipes(self) -> list:
        """Get list of all available recipes"""
        return self.recipe_manager.list_recipes()