#!/usr/bin/env python3
"""
Test runner for procedural generation system
"""

import sys
import os
import subprocess

def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("Procedural Generation Test Suite")
    print("="*60)
    
    # Define test files in order of complexity
    test_files = [
        "tests/test_procedural_biomes.py",
        "tests/test_settlement_placement.py", 
        "tests/test_enhanced_buildings.py",
        "tests/test_settlement_fixes.py",
        "tests/test_desert_placement.py"
    ]
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            if run_test(test_file):
                passed += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print('='*60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())