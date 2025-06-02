#!/usr/bin/env python3
"""
AI Model Benchmarking Script for Goose CLI
Tests different AI models with existing recipes and measures response times.
"""

import subprocess
import time
import os
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

class GooseModelBenchmark:
    def __init__(self, recipe_name: str = "joke-of-the-day"):
        self.recipe_name = recipe_name
        self.results = []
        
        # Default models to test (commonly available ones)
        self.models = [
            "goose-claude-4-sonnet",
            "goose-gpt-4o", 
            "goose-gpt-4o-mini",
            "goose-claude-3-5-sonnet",
            "goose-claude-3-haiku"
        ]
    
    def set_models(self, models: List[str]):
        """Set custom list of models to test"""
        self.models = models
    
    def set_recipe(self, recipe_name: str):
        """Set the recipe to use for testing"""
        self.recipe_name = recipe_name
    
    def validate_recipe(self) -> bool:
        """Validate that the recipe exists and can be loaded"""
        try:
            result = subprocess.run(
                ["goose", "run", "--recipe", self.recipe_name, "--explain"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                print(f"✅ Recipe validated: {self.recipe_name}")
                return True
            else:
                print(f"❌ Recipe validation failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Recipe validation timed out")
            return False
        except Exception as e:
            print(f"❌ Error validating recipe: {e}")
            return False
    
    def test_model(self, model_name: str, timeout: int = 45) -> Tuple[bool, float, str]:
        """
        Test a single model and return (success, response_time, response_text)
        """
        print(f"🧪 Testing model: {model_name}")
        
        # Set up environment with the model
        env = os.environ.copy()
        env["GOOSE_MODEL"] = model_name
        
        start_time = time.time()
        
        try:
            # Run goose with the recipe
            cmd = [
                "goose", "run", 
                "--recipe", self.recipe_name,
                "--no-session"
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if result.returncode == 0:
                # Extract the actual response (filter out system messages)
                response_text = self._extract_response(result.stdout)
                print(f"✅ {model_name}: {response_time:.2f}s")
                return True, response_time, response_text
            else:
                print(f"❌ {model_name} failed: {result.stderr}")
                return False, response_time, result.stderr
                
        except subprocess.TimeoutExpired:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"⏰ {model_name} timed out after {timeout}s")
            return False, response_time, "TIMEOUT"
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"❌ {model_name} error: {e}")
            return False, response_time, str(e)
    
    def _extract_response(self, output: str) -> str:
        """Extract the actual AI response from goose output"""
        lines = output.strip().split('\n')
        response_lines = []
        
        # Skip initial setup lines and extract the actual content
        skip_patterns = [
            r'📦 Looking for recipe',
            r'github\.com',
            r'✓ Logged in',
            r'- Active account',
            r'- Git operations',
            r'- Token',
            r'Files downloaded',
            r'⬇️  Retrieved recipe',
            r'Loading recipe:',
            r'Description:',
            r'Parameters used',
            r'running without session',
            r'working directory:'
        ]
        
        for line in lines:
            # Skip empty lines and system messages
            if not line.strip():
                continue
                
            # Check if line matches any skip pattern
            should_skip = any(re.search(pattern, line) for pattern in skip_patterns)
            if should_skip:
                continue
                
            # Remove ANSI color codes
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            if clean_line.strip():
                response_lines.append(clean_line.strip())
        
        return '\n'.join(response_lines) if response_lines else output.strip()
    
    def run_benchmark(self, iterations: int = 1, timeout: int = 45) -> Dict:
        """
        Run the benchmark for all models
        """
        print("🚀 Starting AI Model Benchmark")
        print(f"📝 Recipe: {self.recipe_name}")
        print(f"🔄 Iterations per model: {iterations}")
        print(f"⏱️  Timeout: {timeout}s")
        print("-" * 60)
        
        if not self.validate_recipe():
            return {"error": "Recipe validation failed"}
        
        benchmark_results = {
            "recipe_name": self.recipe_name,
            "iterations": iterations,
            "timeout": timeout,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {}
        }
        
        for model in self.models:
            model_results = {
                "success_count": 0,
                "total_time": 0,
                "average_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "responses": [],
                "errors": []
            }
            
            print(f"\n🎯 Testing {model} ({iterations} iteration{'s' if iterations > 1 else ''}):")
            
            for i in range(iterations):
                if iterations > 1:
                    print(f"  Iteration {i+1}/{iterations}")
                
                success, response_time, response_text = self.test_model(model, timeout)
                
                if success:
                    model_results["success_count"] += 1
                    model_results["total_time"] += response_time
                    model_results["min_time"] = min(model_results["min_time"], response_time)
                    model_results["max_time"] = max(model_results["max_time"], response_time)
                    model_results["responses"].append(response_text)
                else:
                    model_results["errors"].append(response_text)
            
            # Calculate averages
            if model_results["success_count"] > 0:
                model_results["average_time"] = model_results["total_time"] / model_results["success_count"]
                if model_results["min_time"] == float('inf'):
                    model_results["min_time"] = 0
            else:
                model_results["min_time"] = 0
            
            benchmark_results["models"][model] = model_results
        
        return benchmark_results
    
    def print_results(self, results: Dict):
        """Print formatted benchmark results"""
        print("\n" + "="*70)
        print("🏆 BENCHMARK RESULTS")
        print("="*70)
        print(f"📝 Recipe: {results['recipe_name']}")
        print(f"🕒 Timestamp: {results['timestamp']}")
        
        # Sort models by average response time (fastest first)
        successful_models = []
        for model, data in results["models"].items():
            if data["success_count"] > 0:
                successful_models.append((model, data["average_time"], data))
        
        successful_models.sort(key=lambda x: x[1])  # Sort by average time
        
        if successful_models:
            print(f"\n📊 Ranking (by average response time):")
            print(f"{'Rank':<4} {'Model':<30} {'Avg Time':<10} {'Success Rate':<12} {'Min/Max'}")
            print("-" * 70)
            
            for i, (model, avg_time, data) in enumerate(successful_models, 1):
                success_rate = (data["success_count"] / results["iterations"]) * 100
                min_max = f"{data['min_time']:.1f}s/{data['max_time']:.1f}s" if data["success_count"] > 1 else "N/A"
                print(f"{i:<4} {model:<30} {avg_time:>6.2f}s    {success_rate:>6.1f}%      {min_max}")
            
            # Show performance comparison
            if len(successful_models) > 1:
                fastest_time = successful_models[0][1]
                print(f"\n⚡ Performance comparison (vs fastest):")
                for i, (model, avg_time, data) in enumerate(successful_models, 1):
                    if i == 1:
                        print(f"   🥇 {model}: baseline (fastest)")
                    else:
                        slowdown = (avg_time / fastest_time - 1) * 100
                        print(f"   {i:2d}. {model}: +{slowdown:.1f}% slower")
        
        # Show failed models
        failed_models = [model for model, data in results["models"].items() if data["success_count"] == 0]
        if failed_models:
            print(f"\n❌ Failed models:")
            for model in failed_models:
                errors = results["models"][model]["errors"]
                error_summary = errors[0][:50] + "..." if errors and len(errors[0]) > 50 else (errors[0] if errors else "Unknown error")
                print(f"   - {model}: {error_summary}")
        
        # Show sample responses from fastest model
        if successful_models:
            fastest_model, _, fastest_data = successful_models[0]
            print(f"\n💬 Sample response from fastest model ({fastest_model}):")
            if fastest_data["responses"]:
                response = fastest_data["responses"][0]
                # Show first few lines of response
                response_lines = response.split('\n')[:3]
                for line in response_lines:
                    print(f"   {line}")
                if len(fastest_data["responses"][0].split('\n')) > 3:
                    print("   ...")
    
    def save_results(self, results: Dict, filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function to run the benchmark"""
    # Available recipes you can test with:
    available_recipes = [
        "joke-of-the-day",
        "tech-health", 
        "make-read-me",
        "analyse-pr",
        "fix-pr"
    ]
    
    # Initialize benchmark with a simple recipe
    benchmark = GooseModelBenchmark("joke-of-the-day")
    
    # You can customize the models to test here
    # Common model names (some might not be available in your setup):
    test_models = [
        "goose-claude-4-sonnet",
        "goose-gpt-4o",
        "goose-gpt-4o-mini", 
        "goose-claude-3-5-sonnet",
        "goose-claude-3-haiku"
    ]
    
    benchmark.set_models(test_models)
    
    print("🤖 AI Model Benchmarking Tool")
    print(f"📋 Available recipes: {', '.join(available_recipes)}")
    print(f"🎯 Testing models: {', '.join(test_models)}")
    print()
    
    # Run the benchmark
    iterations = 1  # Increase for more accurate averages (but takes longer)
    timeout = 45    # Timeout per model test in seconds
    
    results = benchmark.run_benchmark(iterations=iterations, timeout=timeout)
    
    if "error" not in results:
        benchmark.print_results(results)
        benchmark.save_results(results)
        
        # Quick summary
        successful_count = sum(1 for data in results["models"].values() if data["success_count"] > 0)
        total_count = len(results["models"])
        print(f"\n📈 Summary: {successful_count}/{total_count} models completed successfully")
        
    else:
        print(f"❌ Benchmark failed: {results['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
