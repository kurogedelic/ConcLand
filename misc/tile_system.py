"""Tile loading and management system for Pyxel"""
import pyxel
import os
from PIL import Image

class TileManager:
    def __init__(self):
        self.tiles = {}
        self.tile_size = 8
        self.image_bank = 0  # Pyxelのイメージバンク0を使用
        self.tilemap_width = 256
        self.tilemap_height = 256
        self.current_x = 0
        self.current_y = 0
        
        # アニメーション情報
        self.animations = {}
    
    def _get_coastline_tiles(self):
        """海岸線タイルのリストを生成"""
        patterns = [
            '1000', '0100', '0010', '0001',  # Single sides
            '1010', '0101',  # Two sides - straight
            '1100', '0110', '0011', '1001',  # Two sides - corners
            '1110', '1101', '1011', '0111',  # Three sides
            '1111'  # Four sides
        ]
        return [f'coastline_{pattern}' for pattern in patterns]
        
    def load_all_tiles(self):
        """全てのタイルを読み込む"""
        # Pyxelの一時的なタイルマップを作成
        tilemap = Image.new('RGBA', (self.tilemap_width, self.tilemap_height), (0, 0, 0, 0))
        
        # タイルカテゴリと読み込み順序
        tile_categories = [
            ('terrain', ['grass', 'soil']),
            ('terrain', ['water_animation']),  # アニメーション
            ('terrain', self._get_coastline_tiles()),  # 海岸線タイル
            ('residential', ['empty', 'low_1', 'middle_1', 'high_1']),
            ('commercial', ['empty', 'low_1', 'middle_1', 'high_1']),
            ('industrial', ['empty', 'low_1', 'middle_1', 'high_1']),
            ('road', ['horizontal', 'vertical', 'corner_ne', 'corner_se', 
                     'corner_sw', 'corner_nw', 'cross', 't_north', 't_south',
                     't_east', 't_west', 'alone']),
            ('power', ['powerplant', 'solar', 'nuclear', 'gas']),
            ('power', ['wind_animation']),  # アニメーション
            ('agricultural', ['empty', 'field']),
            ('park', ['small_park']),
            ('public', ['shrine']),
            ('effects', ['construction_animation', 'fire_animation']),  # アニメーション
        ]
        
        for category, files in tile_categories:
            for filename in files:
                filepath = f'tiles/{category}/{filename}.png'
                if os.path.exists(filepath):
                    self._load_tile(tilemap, category, filename, filepath)
        
        # 統合されたタイルマップを保存
        tilemap.save('assets/tilemap_generated.png')
        
        # Pyxelに読み込む
        pyxel.images[self.image_bank].load(0, 0, 'assets/tilemap_generated.png')
        
        print(f"Loaded {len(self.tiles)} tiles")
        
    def _load_tile(self, tilemap, category, name, filepath):
        """個別のタイルを読み込んでタイルマップに配置"""
        tile_img = Image.open(filepath)
        width, height = tile_img.size
        
        # タイルIDを生成
        tile_id = f"{category}_{name}"
        
        # アニメーションタイルの判定
        if 'animation' in name:
            frames = width // self.tile_size
            frame_positions = []
            
            for frame in range(frames):
                # 現在の位置を確認
                if self.current_x + self.tile_size > self.tilemap_width:
                    self.current_x = 0
                    self.current_y += self.tile_size
                
                # フレームを切り出して配置
                frame_img = tile_img.crop((frame * self.tile_size, 0, 
                                         (frame + 1) * self.tile_size, self.tile_size))
                tilemap.paste(frame_img, (self.current_x, self.current_y))
                
                # フレーム位置を記録
                frame_positions.append((self.current_x, self.current_y))
                
                self.current_x += self.tile_size
            
            # アニメーション情報を保存
            self.animations[tile_id] = {
                'frames': frame_positions,
                'current_frame': 0,
                'frame_count': frames
            }
            
            # 最初のフレームをタイル位置として記録
            self.tiles[tile_id] = frame_positions[0]
            
        else:
            # 通常のタイル
            # タイルマップに収まるか確認
            if self.current_x + width > self.tilemap_width:
                self.current_x = 0
                self.current_y += max(height, self.tile_size)
            
            # タイルを配置
            tilemap.paste(tile_img, (self.current_x, self.current_y))
            
            # タイル位置を記録
            self.tiles[tile_id] = (self.current_x, self.current_y, width, height)
            
            self.current_x += width
    
    def get_tile_pos(self, tile_id):
        """タイルの位置を取得"""
        if tile_id in self.animations:
            # アニメーションの現在のフレーム
            anim = self.animations[tile_id]
            return anim['frames'][anim['current_frame']]
        return self.tiles.get(tile_id, (0, 0, 8, 8))
    
    def update_animations(self, frame_count):
        """アニメーションを更新（フレームカウントに基づいて）"""
        # 水のアニメーションは15フレームごと、その他は20フレームごと
        water_update = frame_count % 15 == 0
        other_update = frame_count % 20 == 0
        
        for anim_id, anim_data in self.animations.items():
            if 'water' in anim_id and water_update:
                anim_data['current_frame'] = (anim_data['current_frame'] + 1) % anim_data['frame_count']
            elif 'water' not in anim_id and other_update:
                anim_data['current_frame'] = (anim_data['current_frame'] + 1) % anim_data['frame_count']
    
    def draw_tile(self, tile_id, x, y, size=None):
        """タイルを描画"""
        if tile_id not in self.tiles:
            return
            
        if tile_id in self.animations:
            # アニメーションタイル
            pos = self.get_tile_pos(tile_id)
            pyxel.blt(x, y, self.image_bank, pos[0], pos[1], self.tile_size, self.tile_size, 0)
        else:
            # 通常のタイル
            pos = self.tiles[tile_id]
            if len(pos) == 2:  # 8x8タイル
                pyxel.blt(x, y, self.image_bank, pos[0], pos[1], self.tile_size, self.tile_size, 0)
            else:  # 可変サイズタイル
                pyxel.blt(x, y, self.image_bank, pos[0], pos[1], pos[2], pos[3], 0)
    
    def get_road_tile_id(self, north=False, east=False, south=False, west=False):
        """道路の接続パターンから適切なタイルIDを取得"""
        patterns = {
            (False, False, False, False): 'road_alone',
            (False, True, False, True): 'road_horizontal',
            (True, False, True, False): 'road_vertical',
            (False, True, True, False): 'road_corner_ne',
            (False, False, True, True): 'road_corner_se',
            (True, False, False, True): 'road_corner_sw',
            (True, True, False, False): 'road_corner_nw',
            (True, True, True, False): 'road_t_east',
            (True, False, True, True): 'road_t_west',
            (False, True, True, True): 'road_t_south',
            (True, True, False, True): 'road_t_north',
            (True, True, True, True): 'road_cross',
        }
        
        return patterns.get((north, east, south, west), 'road_alone')
    
    def get_building_tile_id(self, building_type, density, has_power=True):
        """建物タイプと密度からタイルIDを取得"""
        # 電力がない場合は空き地タイル
        if not has_power:
            return f"{building_type}_empty"
            
        density_map = {
            0: 'empty',  # 空地
            1: 'low_1',
            2: 'middle_1',
            3: 'high_1',
        }
        
        density_name = density_map.get(density, 'low_1')
        if density_name:
            return f"{building_type}_{density_name}"
        return None
    
    def get_coastline_tile_id(self, north, east, south, west):
        """海岸線パターンから適切なタイルIDを取得"""
        pattern = f"{int(north)}{int(east)}{int(south)}{int(west)}"
        tile_id = f"terrain_coastline_{pattern}"
        # Check if this tile exists
        if tile_id in self.tiles:
            return tile_id
        # Fall back to regular water if no coastline tile
        return 'terrain_water_animation'