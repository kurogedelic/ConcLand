    def _draw_large_building(self, x: int, y: int, screen_x: int, screen_y: int, cell_type: CellType, data):
        """Draw a large building (3x3 or 4x4)"""
        
        # Determine building size for proper coloring in non-normal views
        building_width = 0
        building_height = 0
        
        # 4x4 buildings
        if cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT, 
                        CellType.OIL_PLANT, CellType.LABORATORY, CellType.SPACE]:
            building_width = 4
            building_height = 4
        # 4x3 buildings
        elif cell_type == CellType.AIRPORT:
            building_width = 4
            building_height = 3
        # 2x2 buildings
        elif cell_type == CellType.SOLAR_PLANT:
            building_width = 2
            building_height = 2
        # 3x3 buildings
        else:
            building_width = 3
            building_height = 3
        
        # In normal view mode, draw the graphics
        if self.view_mode == 0:
            # Draw the actual building graphics
            if cell_type == CellType.COAL_PLANT:
                self.tile_manager.draw_tile('coal_plant', screen_x, screen_y)
            elif cell_type == CellType.NUCLEAR_PLANT:
                self.tile_manager.draw_tile('nuclear_plant', screen_x, screen_y)
            elif cell_type == CellType.GAS_PLANT:
                self.tile_manager.draw_tile('gas', screen_x, screen_y)
            elif cell_type == CellType.OIL_PLANT:
                self.tile_manager.draw_tile('oil', screen_x, screen_y)
            elif cell_type == CellType.SOLAR_PLANT:
                self.tile_manager.draw_tile('solar', screen_x, screen_y)
            elif cell_type == CellType.LABORATORY:
                self.tile_manager.draw_tile('laboratory', screen_x, screen_y)
            elif cell_type == CellType.SPACE:
                self.tile_manager.draw_tile('space', screen_x, screen_y)
            elif cell_type == CellType.AIRPORT:
                self.tile_manager.draw_tile('airport', screen_x, screen_y)
            elif cell_type == CellType.POLICE:
                self.tile_manager.draw_tile('police', screen_x, screen_y)
            elif cell_type == CellType.FIRE:
                self.tile_manager.draw_tile('fire', screen_x, screen_y)
            elif cell_type == CellType.HOSPITAL:
                self.tile_manager.draw_tile('hospital', screen_x, screen_y)
            elif cell_type == CellType.SCHOOL:
                self.tile_manager.draw_tile('school', screen_x, screen_y)
            elif cell_type == CellType.UNIVERSITY:
                self.tile_manager.draw_tile('university', screen_x, screen_y)
            elif cell_type == CellType.SEWAGE_PLANT:
                self.tile_manager.draw_tile('sewage_plant', screen_x, screen_y)
            elif cell_type == CellType.WATER_PLANT:
                self.tile_manager.draw_tile('water_plant', screen_x, screen_y)
            elif cell_type == CellType.LIBRARY:
                self.tile_manager.draw_tile('library', screen_x, screen_y)
            elif cell_type == CellType.MILITARY:
                self.tile_manager.draw_tile('military', screen_x, screen_y)
            elif cell_type == CellType.PRISON:
                self.tile_manager.draw_tile('prison', screen_x, screen_y)
            elif cell_type == CellType.SHRINE:
                self.tile_manager.draw_tile('shrine', screen_x, screen_y)
            elif cell_type == CellType.HELIPORT:
                self.tile_manager.draw_tile('heliport', screen_x, screen_y)
            elif cell_type == CellType.SEAPORT:
                if 'seaport' in self.tile_manager.tile_images:
                    self.tile_manager.draw_tile('seaport', screen_x, screen_y)
                else:
                    self.tile_manager.draw_tile('port', screen_x, screen_y)
            elif cell_type == CellType.INCINERATOR:
                self.tile_manager.draw_tile('incinerator', screen_x, screen_y)
            elif cell_type == CellType.WASTE_FACILITY:
                self.tile_manager.draw_tile('waste', screen_x, screen_y)
            elif cell_type == CellType.ONSEN:
                self.tile_manager.draw_tile('onsen', screen_x, screen_y)
            elif cell_type == CellType.PACHINKO:
                self.tile_manager.draw_tile('pachinko', screen_x, screen_y)
                
            # Show power/water overlays for certain building types
            if cell_type in [CellType.POLICE, CellType.FIRE, CellType.HOSPITAL, CellType.SCHOOL, 
                           CellType.UNIVERSITY, CellType.LIBRARY, CellType.INCINERATOR, CellType.WASTE_FACILITY]:
                if not data.power:
                    if pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_power_overlay', overlay_x, overlay_y, transparent_color=0)
                                
            elif cell_type in [CellType.SEWAGE_PLANT, CellType.WATER_PLANT]:
                if not data.power and not data.water:
                    if pyxel.frame_count % 60 < 15:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_power_overlay', overlay_x, overlay_y, transparent_color=0)
                    elif pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_water_overlay', overlay_x, overlay_y, transparent_color=0)
                elif not data.power:
                    if pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_power_overlay', overlay_x, overlay_y, transparent_color=0)
                elif not data.water:
                    if pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_water_overlay', overlay_x, overlay_y, transparent_color=0)
        
        else:
            # For other view modes, draw colored rectangles for the entire building
            color = 0  # Default black
            
            if self.view_mode == 1:  # Pollution view
                pollution_level = data.pollution
                if pollution_level == 0:
                    color = 3  # Green
                elif pollution_level < 64:
                    color = 11  # Light green
                elif pollution_level < 128:
                    color = 10  # Yellow
                elif pollution_level < 192:
                    color = 9   # Orange
                else:
                    color = 8   # Red
                    
            elif self.view_mode == 2:  # Land value view
                land_value = data.land_value
                if land_value < 64:
                    color = 1   # Dark
                elif land_value < 128:
                    color = 2   # Purple
                elif land_value < 192:
                    color = 12  # Light blue
                else:
                    color = 7   # White
                    
            elif self.view_mode == 3:  # Power view
                # Power plants always show as cyan
                if cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT, 
                                CellType.OIL_PLANT, CellType.WIND_PLANT, CellType.SOLAR_PLANT]:
                    color = 12  # Cyan for power sources
                else:
                    color = 11 if data.power else 8  # Green if powered, red if not
                    
            elif self.view_mode == 4:  # Traffic view
                traffic_level = data.traffic
                if traffic_level == 0:
                    color = 1   # Dark
                elif traffic_level < 25:
                    color = 3   # Green
                elif traffic_level < 75:
                    color = 10  # Yellow
                elif traffic_level < 150:
                    color = 9   # Orange
                else:
                    color = 8   # Red
                    
            elif self.view_mode == 5:  # Water view
                # Water plants show as cyan
                if cell_type in [CellType.WATER_PLANT, CellType.SEWAGE_PLANT, CellType.PUMP]:
                    color = 12  # Cyan for water sources
                else:
                    color = 12 if data.water else 8  # Light blue if water, red if not
            
            # Draw the colored rectangle for the entire building
            pyxel.rect(screen_x, screen_y, building_width * 8, building_height * 8, color)