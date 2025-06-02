#!/usr/bin/env python3
from benchmark_models import GooseModelBenchmark
import json
import time

# Quick test with 2 models and 1 recipe
recipes_to_test = ["joke-of-the-day"]
models_to_test = ["goose-gpt-4o-mini", "goose-claude-3-haiku"]

print("🚀 QUICK ADVANCED BENCHMARK TEST")
print(f"📋 Testing {len(recipes_to_test)} recipe with {len(models_to_test)} models")

all_results = {}

for recipe in recipes_to_test:
    print(f"\n🧪 TESTING RECIPE: {recipe}")
    
    benchmark = GooseModelBenchmark(recipe)
    benchmark.set_models(models_to_test)
    
    results = benchmark.run_benchmark(iterations=1, timeout=30)
    
    if "error" not in results:
        all_results[recipe] = results
        benchmark.print_results(results)
    else:
        print(f"❌ Failed: {results['error']}")

print(f"\n✅ Test completed successfully!")
