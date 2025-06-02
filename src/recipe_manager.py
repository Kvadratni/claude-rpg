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
                    # Store both the recipe data and the file path
                    self.recipes[recipe_name] = {
                        'data': recipe_data,
                        'file_path': recipe_path
                    }
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
        
        recipe_info = self.get_recipe(recipe_name)
        if not recipe_info:
            print(f"❌ [RecipeManager] Recipe '{recipe_name}' not found")
            return f"*{recipe_name} looks confused*"
        
        try:
            # Get the recipe file path directly from loaded data
            recipe_file = recipe_info['file_path']
            print(f"✅ [RecipeManager] Found recipe file: {recipe_file}")
            
            # Set up environment
            env = os.environ.copy()
            env["GOOSE_MODEL"] = "goose-claude-4-sonnet"  # Try the working model
            print(f"🔧 [RecipeManager] Using model: {env.get('GOOSE_MODEL')}")
            
            # Let's try to actually run the subprocess with detailed logging
            print(f"🔧 [RecipeManager] Attempting to run Goose CLI subprocess...")
            
            # Run goose with the recipe and capture output to a file
            import tempfile
            import time
            
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as output_file:
                output_file_path = output_file.name
            
            print(f"🔧 [RecipeManager] Created temp output file: {output_file_path}")
            
            # Escape quotes in the message and context for shell safety
            safe_message = user_message.replace("'", "\\'").replace('"', '\\"')
            safe_context = context.replace("'", "\\'").replace('"', '\\"')
            
            cmd_str = f"goose run --recipe '{recipe_file}' --params 'message={safe_message}' --params 'context={safe_context}' --no-session"
            
            print(f"🔧 [RecipeManager] Command to execute: {cmd_str}")
            print(f"🔧 [RecipeManager] Working directory: {os.getcwd()}")
            print(f"🔧 [RecipeManager] Environment GOOSE_MODEL: {env.get('GOOSE_MODEL')}")
            
            # Test if goose command is available
            try:
                test_result = subprocess.run("which goose", shell=True, capture_output=True, text=True)
                if test_result.returncode == 0:
                    print(f"🔧 [RecipeManager] Goose CLI found at: {test_result.stdout.strip()}")
                else:
                    print(f"❌ [RecipeManager] Goose CLI not found in PATH")
                    return f"*{recipe_name} seems distracted - Goose CLI not available*"
            except Exception as e:
                print(f"❌ [RecipeManager] Error checking Goose CLI: {e}")
                return f"*{recipe_name} seems confused*"
            
            # Run the command and capture output
            print(f"🔧 [RecipeManager] Starting subprocess execution...")
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    f"{cmd_str} > '{output_file_path}' 2>&1",
                    env=env,
                    shell=True,
                    timeout=60  # Increased timeout significantly
                )
                
                execution_time = time.time() - start_time
                print(f"🔧 [RecipeManager] Subprocess completed in {execution_time:.2f}s with return code: {result.returncode}")
                
                # Give much more time for AI response to be written
                print(f"🔧 [RecipeManager] Waiting 10 seconds for AI response to be written...")
                time.sleep(10)
                
                # Read the output from the file
                try:
                    with open(output_file_path, 'r') as f:
                        stdout = f.read()
                    
                    print(f"🔧 [RecipeManager] Output file size: {len(stdout)} characters")
                    print(f"🔧 [RecipeManager] First 200 chars of output: {stdout[:200]}")
                    print(f"🔧 [RecipeManager] Last 200 chars of output: {stdout[-200:]}")
                    
                    if len(stdout) > 500:
                        print(f"🔧 [RecipeManager] Output looks substantial, attempting to parse...")
                        response = self._parse_goose_output(stdout)
                        if response and len(response.strip()) > 10:
                            print(f"✅ [RecipeManager] Successfully parsed AI response: '{response[:100]}...'")
                            cleaned_response = self._clean_response(response, recipe_name)
                            return cleaned_response
                        else:
                            print(f"⚠️  [RecipeManager] Parsed response was empty or too short")
                    else:
                        print(f"⚠️  [RecipeManager] Output too short, likely incomplete")
                    
                except Exception as e:
                    print(f"❌ [RecipeManager] Error reading output file: {e}")
                
            except subprocess.TimeoutExpired:
                print(f"⏰ [RecipeManager] Subprocess timed out after 30 seconds")
                return f"*{recipe_name} takes a long moment to consider your words*"
            except Exception as e:
                print(f"❌ [RecipeManager] Subprocess execution error: {e}")
                return f"*{recipe_name} seems momentarily distracted*"
            
            finally:
                # Clean up the temporary file
                try:
                    if os.path.exists(output_file_path):
                        os.unlink(output_file_path)
                        print(f"🔧 [RecipeManager] Cleaned up temp file: {output_file_path}")
                except Exception as e:
                    print(f"⚠️  [RecipeManager] Could not clean up temp file: {e}")
            
            # If we get here, the subprocess didn't produce a usable response
            print(f"🔧 [RecipeManager] Subprocess completed but no usable AI response found")
            print(f"🔧 [RecipeManager] Using fallback response due to subprocess output issue")
            fallback_response = f"Greetings, traveler. I am {recipe_name.replace('_', ' ').title()}."
            print(f"✅ [RecipeManager] Fallback response: '{fallback_response}'")
            return fallback_response
            
        except Exception as e:
            print(f"❌ [RecipeManager] Recipe execution error for '{recipe_name}': {e}")
            import traceback
            print(f"🔧 [RecipeManager] Full traceback:")
            traceback.print_exc()
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