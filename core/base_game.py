"""
ベースゲームクラス
Base Game Class

ConcLandのコア機能を提供する基底クラス。
他のシステムはこのクラスを継承または拡張します。
"""

import pyxel
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import os
import sys

# 設定ファイルのインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.game_config import *


class CellType(Enum):
    """
    セルタイプの定義
    各セルが持つことができる建物・地形のタイプを定義
    """
    EMPTY = 0           # 空地
    WATER = 1           # 水
    RESIDENTIAL = 2     # 住宅ゾーン
    COMMERCIAL = 3      # 商業ゾーン
    INDUSTRIAL = 4      # 工業ゾーン
    ROAD = 5           # 道路
    RAIL = 6           # 鉄道
    WIRE = 7           # 電線
    PARK = 8           # 公園
    WASTELAND = 9      # 荒地
    # 発電所
    COAL_PLANT = 10    # 石炭発電所
    NUCLEAR_PLANT = 11 # 原子力発電所
    GAS_PLANT = 12     # ガス発電所
    OIL_PLANT = 13     # 石油発電所
    SOLAR_PLANT = 14   # 太陽光発電所
    WIND_PLANT = 15    # 風力発電所
    # 公共施設
    POLICE = 20        # 警察署
    FIRE = 21          # 消防署
    HOSPITAL = 22      # 病院
    SCHOOL = 23        # 学校
    UNIVERSITY = 24    # 大学
    LIBRARY = 25       # 図書館
    # 水道施設
    PUMP = 30          # ポンプ場
    WATER_PLANT = 31   # 浄水場
    SEWAGE_PLANT = 32  # 下水処理場
    # 交通施設
    STATION = 40       # 駅
    AIRPORT = 41       # 空港
    SEAPORT = 42       # 港
    HELIPORT = 43      # ヘリポート
    # 特殊施設
    MILITARY = 50      # 軍事基地
    PRISON = 51        # 刑務所
    SHRINE = 52        # 神社
    INCINERATOR = 53   # 焼却場
    WASTE_FACILITY = 54 # 廃棄物処理施設
    # 娯楽施設
    ONSEN = 60         # 温泉
    PACHINKO = 61      # パチンコ


@dataclass
class SimData:
    """
    シミュレーションデータクラス
    各セルが持つシミュレーション用のデータを管理
    """
    # 基本データ
    population: int = 0      # 人口
    density: int = 0         # 密度 (0-4)
    building_id: int = 0     # 建物ID（3x3建物用）
    
    # インフラ状態
    power: bool = False      # 電力供給
    water: bool = False      # 水道供給
    has_road: bool = False   # 道路接続
    has_rail: bool = False   # 鉄道接続
    
    # 環境データ
    pollution: float = 0.0   # 汚染度
    land_value: float = 100.0 # 地価
    traffic: float = 0.0     # 交通量
    crime: float = 0.0       # 犯罪率
    
    # ブリッジ用
    original_terrain: Optional['CellType'] = None  # 元の地形（橋の下）
    
    # ゾーン予約（RCI成長用）
    zone_underneath: Optional['CellType'] = None   # ゾーンの下にある建物


class BaseGame(ABC):
    """
    ベースゲーム抽象クラス
    すべてのゲームシステムが実装すべき基本インターフェース
    """
    
    def __init__(self):
        """
        ゲームの初期化
        派生クラスで必ず呼び出すこと
        """
        # マップデータ
        self.map_size = MAP_SIZE
        self.grid = [[CellType.EMPTY for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        self.sim_data = [[SimData() for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        
        # ゲーム状態
        self.funds = INITIAL_FUNDS_DEV if DEV_MODE else INITIAL_FUNDS_NORMAL
        self.total_population = 0
        self.total_employment = 0
        self.total_gdp = 0
        
        # 時間管理
        self.year = 2025
        self.month = 1
        self.day = 1
        self.frame_count = 0
        
        # カメラ・ビューポート
        self.camera_x = 0
        self.camera_y = 0
        self.viewport_width = VIEWPORT_WIDTH
        self.viewport_height = VIEWPORT_HEIGHT
        
        # デバッグ
        self.debug_mode = DEBUG_MODE
        self.dev_mode = DEV_MODE
    
    @abstractmethod
    def update(self):
        """
        ゲーム更新処理
        毎フレーム呼び出される
        """
        pass
    
    @abstractmethod
    def draw(self):
        """
        描画処理
        毎フレーム呼び出される
        """
        pass
    
    def handle_input(self):
        """
        入力処理
        キーボード・マウス入力を処理
        """
        pass
    
    def save_game(self, filename: str = SAVE_FILE) -> bool:
        """
        ゲームをセーブ
        
        Args:
            filename: セーブファイル名
            
        Returns:
            成功時True
        """
        try:
            import pickle
            save_data = {
                'grid': self.grid,
                'sim_data': self.sim_data,
                'funds': self.funds,
                'population': self.total_population,
                'year': self.year,
                'month': self.month,
                'day': self.day,
            }
            
            with open(filename, 'wb') as f:
                pickle.dump(save_data, f)
            
            print(f"✅ ゲームをセーブしました: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ セーブ失敗: {e}")
            return False
    
    def load_game(self, filename: str = SAVE_FILE) -> bool:
        """
        ゲームをロード
        
        Args:
            filename: ロードするファイル名
            
        Returns:
            成功時True
        """
        try:
            import pickle
            
            if not os.path.exists(filename):
                print(f"❌ セーブファイルが見つかりません: {filename}")
                return False
            
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            
            self.grid = save_data['grid']
            self.sim_data = save_data['sim_data']
            self.funds = save_data['funds']
            self.total_population = save_data['population']
            self.year = save_data.get('year', 2025)
            self.month = save_data.get('month', 1)
            self.day = save_data.get('day', 1)
            
            print(f"✅ ゲームをロードしました: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ ロード失敗: {e}")
            return False
    
    def get_cell(self, x: int, y: int) -> Optional[CellType]:
        """
        指定座標のセルタイプを取得
        
        Args:
            x, y: 座標
            
        Returns:
            セルタイプ、範囲外の場合None
        """
        if 0 <= x < self.map_size and 0 <= y < self.map_size:
            return self.grid[y][x]
        return None
    
    def set_cell(self, x: int, y: int, cell_type: CellType) -> bool:
        """
        指定座標にセルを設定
        
        Args:
            x, y: 座標
            cell_type: 設定するセルタイプ
            
        Returns:
            成功時True
        """
        if 0 <= x < self.map_size and 0 <= y < self.map_size:
            self.grid[y][x] = cell_type
            return True
        return False
    
    def get_sim_data(self, x: int, y: int) -> Optional[SimData]:
        """
        指定座標のシミュレーションデータを取得
        
        Args:
            x, y: 座標
            
        Returns:
            SimData、範囲外の場合None
        """
        if 0 <= x < self.map_size and 0 <= y < self.map_size:
            return self.sim_data[y][x]
        return None
    
    def count_nearby_type(self, x: int, y: int, cell_type: CellType, radius: int) -> int:
        """
        指定座標の周囲にある特定タイプのセル数をカウント
        
        Args:
            x, y: 中心座標
            cell_type: カウントするセルタイプ
            radius: 検索半径
            
        Returns:
            該当セル数
        """
        count = 0
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.map_size and 0 <= ny < self.map_size:
                    if self.grid[ny][nx] == cell_type:
                        count += 1
        return count
    
    def calculate_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        2点間の距離を計算（マンハッタン距離）
        
        Args:
            x1, y1: 始点
            x2, y2: 終点
            
        Returns:
            距離
        """
        return abs(x2 - x1) + abs(y2 - y1)
    
    def is_in_viewport(self, x: int, y: int) -> bool:
        """
        指定座標がビューポート内にあるかチェック
        
        Args:
            x, y: チェックする座標
            
        Returns:
            ビューポート内の場合True
        """
        return (self.camera_x <= x < self.camera_x + self.viewport_width and
                self.camera_y <= y < self.camera_y + self.viewport_height)
    
    def update_camera(self, dx: int, dy: int):
        """
        カメラ位置を更新
        
        Args:
            dx, dy: 移動量
        """
        self.camera_x = max(0, min(self.camera_x + dx, self.map_size - self.viewport_width))
        self.camera_y = max(0, min(self.camera_y + dy, self.map_size - self.viewport_height))