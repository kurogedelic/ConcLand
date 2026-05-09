#!/usr/bin/env python3
"""
Check which assets are not being used in the game
"""

import os
from individual_tile_system import IndividualTileSystem

# Get all PNG files in assets/tiles
all_assets = []
for root, dirs, files in os.walk('assets/tiles'):
    for file in files:
        if file.endswith('.png'):
            path = os.path.join(root, file)
            all_assets.append(path)

# Get currently used assets
tile_system = IndividualTileSystem()
used_assets = set(tile_system.tile_files.values())

# Find unused assets
unused_assets = []
for asset in all_assets:
    if asset not in used_assets:
        unused_assets.append(asset)

print("🔍 Asset Usage Analysis")
print("=" * 50)
print(f"Total assets available: {len(all_assets)}")
print(f"Assets currently used: {len(used_assets)}")
print(f"Unused assets: {len(unused_assets)}")

if unused_assets:
    print("\n❌ Unused Assets:")
    # Group by category
    categories = {}
    for asset in sorted(unused_assets):
        category = asset.split('/')[2]  # Get category from path
        if category not in categories:
            categories[category] = []
        categories[category].append(asset)
    
    for category, assets in sorted(categories.items()):
        print(f"\n  {category.upper()}:")
        for asset in assets:
            filename = os.path.basename(asset)
            print(f"    - {filename}")

# Also check for missing functionality
print("\n📋 Missing Game Features for Available Assets:")
missing_features = {
    'agricultural': "Farm/field system not implemented",
    'effects': "Construction/fire animations not used",
    'wind_animation.png': "Wind power not implemented", 
    'empty.png': "Empty lot tiles not used",
    'rail t-junctions': "Rail T-junctions not implemented",
}

for feature, desc in missing_features.items():
    print(f"  - {feature}: {desc}")