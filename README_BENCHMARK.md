# AI Model Benchmarking Tool for Goose CLI

This tool allows you to benchmark different AI models using Goose CLI recipes to see which one responds fastest.

## Files

- `benchmark_models.py` - Main benchmarking script
- `advanced_benchmark.py` - Tests multiple recipes at once
- `quick_test.py` - Simple test with 2 models

## Usage

### Basic Benchmark
```bash
python3 benchmark_models.py
```

This will test all default models with the "joke-of-the-day" recipe.

### Advanced Benchmark (Multiple Recipes)
```bash
python3 advanced_benchmark.py
```

This tests multiple recipes with all models for comprehensive analysis.

### Customize Models
Edit the script and modify the `test_models` list:
```python
test_models = [
    "goose-claude-4-sonnet",
    "goose-gpt-4o-mini", 
    "goose-claude-3-haiku"
    # Add your models here
]
```

### Customize Recipe
```python
benchmark = GooseModelBenchmark("your-recipe-name")
```

## Available Recipes
- `joke-of-the-day` - Simple joke generation
- `make-read-me` - README file generation
- `tech-health` - Technical health analysis
- `analyse-pr` - Pull request analysis
- `fix-pr` - Pull request fixing

## Environment Variables
The script automatically sets `GOOSE_MODEL` for each test. You can also set:
- `GOOSE_PROVIDER` - AI provider (default: databricks)
- Other goose configuration variables

## Output
- Console output with rankings and timing
- JSON file with detailed results
- Performance comparison analysis

## Example Output
```
🏆 BENCHMARK RESULTS
Rank Model                    Avg Time   Success Rate
1    goose-gpt-4o-mini         1.92s     100.0%
2    goose-claude-3-haiku      1.98s     100.0%
3    goose-gpt-4o              3.45s     100.0%
```
