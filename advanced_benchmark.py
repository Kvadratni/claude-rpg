#!/usr/bin/env python3
"""
Advanced AI Model Benchmarking Script for Goose CLI
Tests multiple recipes with different models and provides comprehensive analysis.
"""

from benchmark_models import GooseModelBenchmark
import json
import time
import sys

def run_comprehensive_benchmark():
    """Run benchmarks across multiple recipes"""
    
    # Recipes to test (you can modify this list)
    recipes_to_test = [
        "joke-of-the-day",
        "make-read-me"
    ]
    
    # Models to test (you can modify this list)
    models_to_test = [
        "goose-gpt-4o-mini",
        "goose-claude-3-haiku", 
        "goose-gpt-4o",
        "goose-claude-3-5-sonnet",
        "goose-claude-4-sonnet"
    ]
    
    print("🚀 COMPREHENSIVE AI MODEL BENCHMARK")
    print("="*60)
    print(f"📋 Testing {len(recipes_to_test)} recipes with {len(models_to_test)} models")
    print(f"🎯 Recipes: {', '.join(recipes_to_test)}")
    print(f"🤖 Models: {', '.join(models_to_test)}")
    print()
    
    all_results = {}
    
    for recipe in recipes_to_test:
        print(f"\n🧪 TESTING RECIPE: {recipe}")
        print("-" * 50)
        
        benchmark = GooseModelBenchmark(recipe)
        benchmark.set_models(models_to_test)
        
        results = benchmark.run_benchmark(iterations=1, timeout=45)
        
        if "error" not in results:
            all_results[recipe] = results
            benchmark.print_results(results)
        else:
            print(f"❌ Failed to test recipe {recipe}: {results['error']}")
            all_results[recipe] = {"error": results["error"]}
    
    # Save comprehensive results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"comprehensive_benchmark_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "="*70)
    print("🏆 COMPREHENSIVE BENCHMARK SUMMARY")
    print("="*70)
    
    # Calculate overall performance across all recipes
    model_performance = {}
    
    for recipe, results in all_results.items():
        if "error" in results:
            continue
            
        for model, data in results["models"].items():
            if data["success_count"] > 0:
                if model not in model_performance:
                    model_performance[model] = {
                        "total_time": 0,
                        "total_tests": 0,
                        "successful_recipes": []
                    }
                model_performance[model]["total_time"] += data["average_time"]
                model_performance[model]["total_tests"] += 1
                model_performance[model]["successful_recipes"].append(recipe)
    
    # Calculate average performance across all recipes
    overall_ranking = []
    for model, perf in model_performance.items():
        if perf["total_tests"] > 0:
            avg_time = perf["total_time"] / perf["total_tests"]
            overall_ranking.append((model, avg_time, perf))
    
    overall_ranking.sort(key=lambda x: x[1])  # Sort by average time
    
    if overall_ranking:
        print(f"\n📊 Overall Model Ranking (average across all recipes):")
        print(f"{'Rank':<4} {'Model':<30} {'Avg Time':<10} {'Success Rate'}")
        print("-" * 60)
        
        for i, (model, avg_time, perf) in enumerate(overall_ranking, 1):
            success_rate = (perf["total_tests"] / len(recipes_to_test)) * 100
            print(f"{i:<4} {model:<30} {avg_time:>6.2f}s    {success_rate:>6.1f}%")
        
        print(f"\n🥇 Winner: {overall_ranking[0][0]} (average {overall_ranking[0][1]:.2f}s)")
        
        if len(overall_ranking) > 1:
            fastest_time = overall_ranking[0][1]
            print(f"\n⚡ Performance gaps:")
            for i, (model, avg_time, perf) in enumerate(overall_ranking[1:], 2):
                gap = (avg_time / fastest_time - 1) * 100
                print(f"   {i}. {model}: +{gap:.1f}% slower than winner")
    
    print(f"\n💾 Comprehensive results saved to: {filename}")
    return all_results

if __name__ == "__main__":
    run_comprehensive_benchmark()
