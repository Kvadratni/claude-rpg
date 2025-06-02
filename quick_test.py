#!/usr/bin/env python3
from benchmark_models import GooseModelBenchmark

# Quick test with just 2 models
benchmark = GooseModelBenchmark("joke-of-the-day")
benchmark.set_models([
    "goose-claude-4-sonnet",
    "goose-gpt-4o-mini"
])

results = benchmark.run_benchmark(iterations=1, timeout=30)
if "error" not in results:
    benchmark.print_results(results)
else:
    print(f"Error: {results['error']}")
