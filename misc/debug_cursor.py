#!/usr/bin/env python3
"""Debug cursor issue"""

from enum import Enum

class ItemMode(Enum):
    BULLDOZE = 0
    RESIDENTIAL = 1
    COMMERCIAL = 2
    INDUSTRIAL = 3
    ROAD = 4
    RAIL = 5
    WIRE = 6
    PARK = 7
    COAL_PLANT = 8
    NUCLEAR_PLANT = 9
    POLICE = 10

# Test the condition
current_item = ItemMode.COAL_PLANT
print(f"current_item = {current_item}")
print(f"current_item.value = {current_item.value}")
print(f"ItemMode.COAL_PLANT = {ItemMode.COAL_PLANT}")
print(f"ItemMode.NUCLEAR_PLANT = {ItemMode.NUCLEAR_PLANT}")

# Test the condition
if current_item in [ItemMode.COAL_PLANT, ItemMode.NUCLEAR_PLANT]:
    print("✓ Condition matches - should be 4x4 cursor")
else:
    print("✗ Condition doesn't match - will be 3x3 or 1x1 cursor")

# Also test POLICE
current_item = ItemMode.POLICE
print(f"\nTesting POLICE: {current_item}")
if current_item == ItemMode.POLICE:
    print("✓ Police matches - should be 3x3 cursor")