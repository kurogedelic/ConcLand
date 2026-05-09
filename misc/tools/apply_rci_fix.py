"""
Apply RCI Zone Fix to ConcLand Mini
This script patches the main game to properly handle RCI zone reservations
"""

import sys
import os
from pathlib import Path

def create_patch():
    """Create a patch for concland_mini.py to fix RCI zone issues"""
    
    patch_code = '''
# === RCI Zone Fix Patch ===
# This patch ensures RCI zones properly reserve 3x3 areas for development

from rci_zone_fix import RCIZoneManager

# Add to __init__ method after line defining self.sim_data
self.zone_manager = RCIZoneManager(MAP_SIZE)

# Add this method to the class
def _handle_rci_placement(self, x: int, y: int, zone_type: CellType) -> bool:
    """Handle RCI zone placement with 3x3 reservation"""
    # Check if we can place with reservation
    if not self.zone_manager.can_place_rci_zone(x, y, self.grid, zone_type):
        return False
    
    # Place with reservation
    building_id = self.zone_manager.place_rci_zone(
        x, y, self.grid, self.sim_data, zone_type
    )
    
    if building_id:
        # Mark initial tile
        self.grid[y][x] = zone_type
        self.sim_data[y][x].building_id = building_id
        self.sim_data[y][x].population = 0
        self.sim_data[y][x].density = 0
        return True
    
    return False

# Replace in _place_building method around line 937:
# OLD CODE:
#     if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
#         return current_type in [CellType.EMPTY, CellType.WASTELAND]
# 
# NEW CODE:
    if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
        # Use zone manager for RCI placement
        return self._handle_rci_placement(x, y, new_type)

# Add to _update_3x3_building_growth method after line 2165:
def _check_zone_development(self, building_id: int):
    """Check if a reserved zone should develop"""
    if not hasattr(self, 'zone_manager'):
        return
    
    if building_id not in self.zone_manager.zone_reservations:
        return
    
    reservation = self.zone_manager.zone_reservations[building_id]
    cx, cy = reservation.center_x, reservation.center_y
    
    # Get total population for this building
    total_pop = self._get_building_population(building_id)
    
    # Determine density based on population
    if total_pop >= 100:
        # Check if we can develop
        if self.zone_manager.can_develop_zone(building_id, self.grid):
            # Calculate density
            if total_pop >= 2000:
                density = 4
            elif total_pop >= 1000:
                density = 3
            elif total_pop >= 500:
                density = 2
            else:
                density = 1
            
            # Develop the zone
            self.zone_manager.develop_zone(
                building_id, self.grid, self.sim_data, density
            )

# Add this call in _update_3x3_building_growth after population update:
self._check_zone_development(building_id)

# Modify _remove_building method to handle zone removal:
# Add after line checking for building removal:
if hasattr(self, 'zone_manager'):
    self.zone_manager.remove_zone(x, y, self.grid, self.sim_data)
'''
    
    return patch_code

def apply_automated_fix():
    """Automatically apply the fix to concland_mini.py"""
    
    # Read the original file
    with open('concland_mini.py', 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    # Check if already patched
    if 'zone_manager' in original_code:
        print("⚠️  File appears to be already patched!")
        return False
    
    # Create backup
    backup_path = 'concland_mini_backup_rci.py'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_code)
    print(f"✅ Created backup: {backup_path}")
    
    # Find insertion points and apply fixes
    lines = original_code.split('\n')
    modified_lines = []
    
    # Import at the top
    import_added = False
    
    for i, line in enumerate(lines):
        # Add import after other imports
        if not import_added and line.startswith('from enum import'):
            modified_lines.append(line)
            modified_lines.append('from rci_zone_fix import RCIZoneManager')
            import_added = True
            continue
        
        # Add zone_manager initialization in __init__
        if 'self.sim_data = [[' in line:
            modified_lines.append(line)
            # Find the end of sim_data initialization
            while i < len(lines) - 1:
                i += 1
                modified_lines.append(lines[i])
                if 'for _ in range(MAP_SIZE)]' in lines[i]:
                    break
            # Add zone manager
            modified_lines.append('        self.zone_manager = RCIZoneManager(MAP_SIZE)')
            continue
        
        # Replace RCI placement logic
        if 'if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:' in line:
            # Check if this is in _can_place_1x1_building
            if i > 0 and 'def _can_place_1x1_building' in ''.join(lines[max(0, i-20):i]):
                modified_lines.append('        # RCI zones use special placement with zone manager')
                modified_lines.append('        if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:')
                modified_lines.append('            # Check basic terrain compatibility')
                modified_lines.append('            if current_type not in [CellType.EMPTY, CellType.WASTELAND]:')
                modified_lines.append('                return False')
                modified_lines.append('            # Zone manager will handle the actual reservation check')
                modified_lines.append('            return True')
                # Skip the original line
                i += 1
                if i < len(lines) and 'return current_type in' in lines[i]:
                    i += 1  # Skip the return line too
                continue
        
        # Add zone development check in growth update
        if 'self._set_building_population(building_id, new_population)' in line:
            modified_lines.append(line)
            modified_lines.append('                ')
            modified_lines.append('                # Check if zone should develop visually')
            modified_lines.append('                if hasattr(self, "zone_manager"):')
            modified_lines.append('                    self._check_zone_development(building_id)')
            continue
        
        # Handle actual placement in _place_building
        if 'if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:' in line and \
           'self.sim_data[y][x].population = 0' in ''.join(lines[i:i+5]):
            modified_lines.append('                    # Use zone manager for RCI placement')
            modified_lines.append('                    if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:')
            modified_lines.append('                        if hasattr(self, "zone_manager"):')
            modified_lines.append('                            building_id = self.zone_manager.place_rci_zone(')
            modified_lines.append('                                x, y, self.grid, self.sim_data, new_type')
            modified_lines.append('                            )')
            modified_lines.append('                            if building_id:')
            modified_lines.append('                                self.grid[y][x] = new_type')
            modified_lines.append('                                self.sim_data[y][x].building_id = building_id')
            modified_lines.append('                                self.sim_data[y][x].population = 0')
            modified_lines.append('                                self.sim_data[y][x].density = 0')
            modified_lines.append('                            else:')
            modified_lines.append('                                return  # Failed to place')
            modified_lines.append('                        else:')
            modified_lines.append('                            # Fallback to original behavior')
            modified_lines.append('                            self.sim_data[y][x].population = 0')
            modified_lines.append('                            self.sim_data[y][x].density = 0')
            # Skip original lines
            while i < len(lines) - 1:
                i += 1
                if 'self.sim_data[y][x].density = 0' in lines[i]:
                    break
            continue
        
        modified_lines.append(line)
    
    # Add the zone development check method
    class_end_index = -1
    for i in range(len(modified_lines) - 1, -1, -1):
        if 'def _update_rci_demand' in modified_lines[i]:
            class_end_index = i
            break
    
    if class_end_index > 0:
        # Insert the new method before _update_rci_demand
        new_method = '''
    def _check_zone_development(self, building_id: int):
        """Check if a reserved zone should develop into full 3x3"""
        if not hasattr(self, 'zone_manager'):
            return
        
        if building_id not in self.zone_manager.zone_reservations:
            return
        
        reservation = self.zone_manager.zone_reservations[building_id]
        
        # Get total population for this building
        total_pop = self._get_building_population(building_id)
        
        # Only develop if population is sufficient
        if total_pop >= 100:
            # Check if we can develop
            if self.zone_manager.can_develop_zone(building_id, self.grid):
                # Calculate density based on population
                if total_pop >= 2000:
                    density = 4
                elif total_pop >= 1000:
                    density = 3  
                elif total_pop >= 500:
                    density = 2
                else:
                    density = 1
                
                # Develop the zone to fill 3x3 area
                self.zone_manager.develop_zone(
                    building_id, self.grid, self.sim_data, density
                )
'''
        modified_lines.insert(class_end_index, new_method)
    
    # Save the modified file
    modified_code = '\n'.join(modified_lines)
    output_path = 'concland_mini_fixed.py'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_code)
    
    print(f"✅ Created fixed version: {output_path}")
    print("\n📝 Instructions:")
    print("1. Review the changes in concland_mini_fixed.py")
    print("2. Test the game: python3 concland_mini_fixed.py")
    print("3. If everything works, rename it to concland_mini.py")
    
    return True

def main():
    """Main function"""
    print("🔧 RCI Zone Fix for ConcLand Mini")
    print("=" * 40)
    
    # Check if files exist
    if not os.path.exists('concland_mini.py'):
        print("❌ Error: concland_mini.py not found!")
        print("Please run this script in the ConcLand directory.")
        return 1
    
    if not os.path.exists('rci_zone_fix.py'):
        print("❌ Error: rci_zone_fix.py not found!")
        print("Please ensure rci_zone_fix.py is in the same directory.")
        return 1
    
    print("\n📋 This fix will:")
    print("- Ensure RCI zones reserve 3x3 areas when placed")
    print("- Prevent 1x1 buildings from interrupting zone development")
    print("- Allow zones to develop properly into full 3x3 buildings")
    
    print("\n🚀 Applying automated fix...")
    
    if apply_automated_fix():
        print("\n✅ Fix applied successfully!")
        print("\n🎮 To test the fix:")
        print("  python3 concland_mini_fixed.py")
        print("\n💡 The fix ensures:")
        print("  - RCI zones reserve 3x3 space when placed")
        print("  - Zones develop into full buildings when population grows")
        print("  - No more 1x1 intrusions into developing zones")
    else:
        print("\n❌ Failed to apply fix")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())