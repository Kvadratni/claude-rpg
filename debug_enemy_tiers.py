#!/usr/bin/env python3
"""
Quick test to verify enemy tier selection logic
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Test the distance calculation logic
def test_distance_logic():
    # Simulate the current broken logic
    settlement_safe_zones = []  # Empty like in world generator
    
    def distance_to_nearest_settlement_broken(x, y, zones):
        if not zones:
            return float('inf')  # This is the bug!
        return 30.0  # Would return reasonable distance if zones existed
    
    def distance_to_nearest_settlement_fixed(x, y, zones):
        if not zones:
            return 30.0  # Default to tier 1 range when no settlements
        return 30.0
    
    # Test both versions
    dist_broken = distance_to_nearest_settlement_broken(10, 10, settlement_safe_zones)
    dist_fixed = distance_to_nearest_settlement_fixed(10, 10, settlement_safe_zones)
    
    print(f"Broken logic distance: {dist_broken}")
    print(f"Fixed logic distance: {dist_fixed}")
    
    # Tier selection logic
    def select_tier(distance):
        if distance < 60:
            return 'tier_1', "Beginner"
        elif distance < 120:
            return 'tier_2', "Intermediate"
        else:
            return 'tier_3', "Advanced"
    
    tier_broken, name_broken = select_tier(dist_broken)
    tier_fixed, name_fixed = select_tier(dist_fixed)
    
    print(f"Broken logic tier: {tier_broken} ({name_broken})")
    print(f"Fixed logic tier: {tier_fixed} ({name_fixed})")

if __name__ == "__main__":
    test_distance_logic()
