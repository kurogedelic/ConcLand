#!/usr/bin/env python3
"""
不足しているタイルの仮スプライトを生成
Generate placeholder sprites for missing tiles
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# 設定 / Configuration
TILE_SIZE = 8
OUTPUT_DIR = Path("/Volumes/SSD/ConcLand/assets/tiles")
PALETTE_IMAGE = Path("/Volumes/SSD/ConcLand/assets/palette256_magenta.png")

# カラーパレット（256色）を定義
# 基本色は既存タイルから抽出
COLORS = {
    'transparent': (255, 0, 255),  # Magenta for transparency
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'green': (34, 139, 34),      # Forest green
    'dark_green': (0, 100, 0),
    'light_green': (144, 238, 144),
    'blue': (30, 144, 255),      # Sky blue
    'dark_blue': (0, 0, 139),
    'light_blue': (135, 206, 250),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'light_gray': (192, 192, 192),
    'brown': (139, 69, 19),
    'yellow': (255, 215, 0),
    'orange': (255, 140, 0),
    'red': (220, 20, 60),
    'dark_red': (139, 0, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
}

def create_tile(color_map):
    """
    8x8タイルを作成
    Create 8x8 tile

    Args:
        color_map: 8x8のカラーマップ（色名またはRGBAタプルのリスト）

    Returns:
        PIL.Image object
    """
    img = Image.new('P', (TILE_SIZE, TILE_SIZE))
    pixels = []

    # パレットを設定
    palette = []
    for color in COLORS.values():
        palette.extend(color)
    # 残りを透明で埋める
    while len(palette) < 256 * 3:
        palette.extend(COLORS['transparent'])
    img.putpalette(palette)

    # ピクセルを描画
    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            if isinstance(color_map[y][x], str):
                color = COLORS[color_map[y][x]]
            else:
                color = color_map[y][x]
            # カラーインデックスを探す
            color_idx = list(COLORS.values()).index(color) if color in list(COLORS.values()) else 0
            img.putpixel((x, y), color_idx)

    return img

def save_tile(img, category, name):
    """
    タイルを保存
    Save tile to file

    Args:
        img: PIL.Image object
        category: カテゴリディレクトリ名
        name: ファイル名（.pngなし）
    """
    output_path = OUTPUT_DIR / category
    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / f"{name}.png"

    # 透明色をマゼンタに設定
    img.save(file_path, 'PNG')
    print(f"✅ Generated: {file_path}")

def generate_road_tiles():
    """道路タイルを生成（基本形）"""
    # 基本道路（灰色）
    road = [
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
        ['light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray'],
        ['light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray'],
        ['light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray'],
        ['light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray', 'light_gray'],
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
    ]
    img = create_tile(road)
    save_tile(img, 'road', 'road')

def generate_rail_tiles():
    """鉄道タイルを生成"""
    rail = [
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
        ['green', 'green', 'brown', 'brown', 'brown', 'brown', 'green', 'green'],
        ['green', 'green', 'brown', 'gray', 'gray', 'brown', 'green', 'green'],
        ['green', 'green', 'brown', 'gray', 'gray', 'brown', 'green', 'green'],
        ['green', 'green', 'brown', 'gray', 'gray', 'brown', 'green', 'green'],
        ['green', 'green', 'brown', 'gray', 'gray', 'brown', 'green', 'green'],
        ['green', 'green', 'brown', 'brown', 'brown', 'brown', 'green', 'green'],
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
    ]
    img = create_tile(rail)
    save_tile(img, 'rail', 'rail')

def generate_wire_tiles():
    """電線タイルを生成"""
    wire = [
        ['light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green'],
        ['light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green'],
        ['light_green', 'light_green', 'black', 'black', 'black', 'black', 'light_green', 'light_green'],
        ['light_green', 'light_green', 'black', 'black', 'black', 'black', 'light_green', 'light_green'],
        ['light_green', 'light_green', 'black', 'black', 'black', 'black', 'light_green', 'light_green'],
        ['light_green', 'light_green', 'black', 'black', 'black', 'black', 'light_green', 'light_green'],
        ['light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green'],
        ['light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green'],
    ]
    img = create_tile(wire)
    save_tile(img, 'overlay/wire', 'wire')

def generate_zone_tiles():
    """RCIゾーンタイルを生成"""
    # 住宅（緑系）
    for i, (base, roof) in enumerate([('green', 'red'), ('dark_green', 'dark_red'), ('light_green', 'orange'), ('brown', 'yellow')]):
        res = [
            [base, base, base, base, base, base, base, base],
            [base, base, base, base, base, base, base, base],
            [base, base, roof, roof, roof, roof, base, base],
            [base, base, roof, 'white', 'white', roof, base, base],
            [base, base, roof, 'white', 'white', roof, base, base],
            [base, base, roof, roof, roof, roof, base, base],
            [base, base, base, base, base, base, base, base],
            [base, base, base, base, base, base, base, base],
        ]
        img = create_tile(res)
        save_tile(img, 'residential', f'residential_{i+1}' if i > 0 else 'residential')

    # 商業（青系）
    for i, base in enumerate(['blue', 'dark_blue', 'light_blue', 'purple']):
        com = [
            [base, base, base, base, base, base, base, base],
            [base, base, 'white', 'white', 'white', 'white', base, base],
            [base, base, 'white', 'blue', 'blue', 'white', base, base],
            [base, base, 'white', 'blue', 'blue', 'white', base, base],
            [base, base, 'white', 'blue', 'blue', 'white', base, base],
            [base, base, 'white', 'white', 'white', 'white', base, base],
            [base, base, base, base, base, base, base, base],
            [base, base, base, base, base, base, base, base],
        ]
        img = create_tile(com)
        save_tile(img, 'commercial', f'commercial_{i+1}' if i > 0 else 'commercial')

    # 工業（茶・オレンジ系）
    for i, base in enumerate(['orange', 'brown', 'yellow', 'gray']):
        ind = [
            [base, base, base, base, base, base, base, base],
            [base, base, 'gray', 'gray', 'gray', 'gray', base, base],
            [base, base, 'gray', 'black', 'black', 'gray', base, base],
            [base, base, 'gray', 'black', 'black', 'gray', base, base],
            [base, base, 'gray', 'black', 'black', 'gray', base, base],
            [base, base, 'gray', 'gray', 'gray', 'gray', base, base],
            [base, base, base, base, base, base, base, base],
            [base, base, base, base, base, base, base, base],
        ]
        img = create_tile(ind)
        save_tile(img, 'industrial', f'industrial_{i+1}' if i > 0 else 'industrial')

def generate_park_tiles():
    """公園タイルを生成"""
    # 小公園
    park = [
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
        ['green', 'dark_green', 'dark_green', 'green', 'green', 'dark_green', 'dark_green', 'green'],
        ['green', 'dark_green', 'brown', 'brown', 'brown', 'brown', 'dark_green', 'green'],
        ['green', 'green', 'brown', 'green', 'green', 'brown', 'green', 'green'],
        ['green', 'green', 'brown', 'green', 'green', 'brown', 'green', 'green'],
        ['green', 'dark_green', 'brown', 'brown', 'brown', 'brown', 'dark_green', 'green'],
        ['green', 'dark_green', 'dark_green', 'green', 'green', 'dark_green', 'dark_green', 'green'],
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
    ]
    img = create_tile(park)
    save_tile(img, 'park', 'park')

    # 中公園
    park_middle = [
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
        ['green', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'green'],
        ['green', 'blue', 'brown', 'brown', 'brown', 'brown', 'blue', 'green'],
        ['green', 'blue', 'brown', 'yellow', 'yellow', 'brown', 'blue', 'green'],
        ['green', 'blue', 'brown', 'yellow', 'yellow', 'brown', 'blue', 'green'],
        ['green', 'blue', 'brown', 'brown', 'brown', 'brown', 'blue', 'green'],
        ['green', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'green'],
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
    ]
    img = create_tile(park_middle)
    save_tile(img, 'park', 'park_middle')

    # 大公園（24x24、複数タイルで構成）
    park_big = [
        ['dark_green', 'dark_green', 'dark_green', 'green', 'green', 'green', 'green', 'dark_green'],
        ['dark_green', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'dark_green'],
        ['dark_green', 'blue', 'brown', 'brown', 'brown', 'brown', 'blue', 'dark_green'],
        ['green', 'blue', 'brown', 'yellow', 'yellow', 'brown', 'blue', 'green'],
        ['green', 'blue', 'brown', 'yellow', 'yellow', 'brown', 'blue', 'green'],
        ['dark_green', 'blue', 'brown', 'brown', 'brown', 'brown', 'blue', 'dark_green'],
        ['dark_green', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'dark_green'],
        ['dark_green', 'dark_green', 'dark_green', 'green', 'green', 'green', 'green', 'dark_green'],
    ]
    img = create_tile(park_big)
    save_tile(img, 'park', 'park_big')

def generate_utility_tiles():
    """ユーティリティタイルを生成"""
    # 下水処理場
    sewage = [
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
        ['gray', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'gray'],
        ['gray', 'brown', 'blue', 'blue', 'blue', 'blue', 'brown', 'gray'],
        ['gray', 'brown', 'blue', 'blue', 'blue', 'blue', 'brown', 'gray'],
        ['gray', 'brown', 'blue', 'blue', 'blue', 'blue', 'brown', 'gray'],
        ['gray', 'brown', 'blue', 'blue', 'blue', 'blue', 'brown', 'gray'],
        ['gray', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'gray'],
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
    ]
    img = create_tile(sewage)
    save_tile(img, 'public', 'sewage_plant')

    # 浄水場
    water_plant = [
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
        ['blue', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'blue'],
        ['blue', 'gray', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'gray', 'blue'],
        ['blue', 'gray', 'light_blue', 'white', 'white', 'light_blue', 'gray', 'blue'],
        ['blue', 'gray', 'light_blue', 'white', 'white', 'light_blue', 'gray', 'blue'],
        ['blue', 'gray', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'gray', 'blue'],
        ['blue', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'blue'],
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
    ]
    img = create_tile(water_plant)
    save_tile(img, 'public', 'water_plant')

    # ポンプ
    pump = [
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
        ['green', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'green'],
        ['green', 'gray', 'blue', 'blue', 'blue', 'gray', 'gray', 'green'],
        ['green', 'gray', 'blue', 'red', 'blue', 'gray', 'gray', 'green'],
        ['green', 'gray', 'blue', 'blue', 'blue', 'gray', 'gray', 'green'],
        ['green', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'green'],
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
        ['green', 'green', 'green', 'green', 'green', 'green', 'green', 'green'],
    ]
    img = create_tile(pump)
    save_tile(img, 'water', 'pump')

    # ゴミ処理施設
    waste = [
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
        ['gray', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'gray'],
        ['gray', 'brown', 'black', 'black', 'black', 'black', 'brown', 'gray'],
        ['gray', 'brown', 'black', 'gray', 'gray', 'black', 'brown', 'gray'],
        ['gray', 'brown', 'black', 'gray', 'gray', 'black', 'brown', 'gray'],
        ['gray', 'brown', 'black', 'black', 'black', 'black', 'brown', 'gray'],
        ['gray', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'gray'],
        ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
    ]
    img = create_tile(waste)
    save_tile(img, 'public', 'waste_facility')

def generate_power_tiles():
    """発電所タイルを生成"""
    # 風力発電
    wind = [
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
        ['light_blue', 'white', 'white', 'white', 'white', 'white', 'white', 'light_blue'],
        ['light_blue', 'white', 'gray', 'gray', 'gray', 'gray', 'white', 'light_blue'],
        ['light_blue', 'white', 'gray', 'white', 'white', 'gray', 'white', 'light_blue'],
        ['light_blue', 'white', 'gray', 'white', 'white', 'gray', 'white', 'light_blue'],
        ['light_blue', 'white', 'gray', 'gray', 'gray', 'gray', 'white', 'light_blue'],
        ['light_blue', 'white', 'white', 'white', 'white', 'white', 'white', 'light_blue'],
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
    ]
    img = create_tile(wind)
    save_tile(img, 'power', 'wind')

def generate_agricultural_tiles():
    """農業タイルを生成"""
    ag = [
        ['yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow'],
        ['yellow', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'yellow'],
        ['yellow', 'light_green', 'brown', 'brown', 'brown', 'brown', 'light_green', 'yellow'],
        ['yellow', 'light_green', 'brown', 'light_green', 'light_green', 'brown', 'light_green', 'yellow'],
        ['yellow', 'light_green', 'brown', 'light_green', 'light_green', 'brown', 'light_green', 'yellow'],
        ['yellow', 'light_green', 'brown', 'brown', 'brown', 'brown', 'light_green', 'yellow'],
        ['yellow', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'light_green', 'yellow'],
        ['yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow'],
    ]
    img = create_tile(ag)
    save_tile(img, 'agricultural', 'agricultural')

def generate_transport_tiles():
    """交通タイル（飛行機・船・地下鉄）を生成"""
    # 飛行機（白、銀色）
    airplane = [
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
        ['light_blue', 'light_blue', 'white', 'white', 'white', 'white', 'light_blue', 'light_blue'],
        ['light_blue', 'white', 'white', 'gray', 'gray', 'white', 'white', 'light_blue'],
        ['light_blue', 'white', 'white', 'gray', 'gray', 'white', 'white', 'light_blue'],
        ['light_blue', 'white', 'white', 'white', 'white', 'white', 'white', 'light_blue'],
        ['light_blue', 'light_blue', 'white', 'white', 'white', 'white', 'light_blue', 'light_blue'],
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
    ]
    img = create_tile(airplane)
    save_tile(img, 'special', 'airplane')

    # ヘリコプター
    helicopter = [
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
        ['light_blue', 'white', 'white', 'white', 'white', 'white', 'white', 'light_blue'],
        ['light_blue', 'white', 'gray', 'gray', 'gray', 'gray', 'white', 'light_blue'],
        ['light_blue', 'light_blue', 'white', 'gray', 'gray', 'white', 'light_blue', 'light_blue'],
        ['light_blue', 'light_blue', 'light_blue', 'white', 'white', 'light_blue', 'light_blue', 'light_blue'],
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
        ['light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue', 'light_blue'],
    ]
    img = create_tile(helicopter)
    save_tile(img, 'special', 'helicopter')

    # 船
    ship = [
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
        ['blue', 'white', 'white', 'gray', 'gray', 'white', 'white', 'blue'],
        ['blue', 'white', 'gray', 'red', 'red', 'gray', 'white', 'blue'],
        ['blue', 'white', 'gray', 'red', 'red', 'gray', 'white', 'blue'],
        ['blue', 'white', 'white', 'gray', 'gray', 'white', 'white', 'blue'],
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
    ]
    img = create_tile(ship)
    save_tile(img, 'water', 'ship')

    # 地下鉄
    subway = [
        ['brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown'],
        ['brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown'],
        ['brown', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'brown'],
        ['brown', 'gray', 'white', 'white', 'white', 'white', 'gray', 'brown'],
        ['brown', 'gray', 'white', 'yellow', 'yellow', 'white', 'gray', 'brown'],
        ['brown', 'gray', 'white', 'yellow', 'yellow', 'white', 'gray', 'brown'],
        ['brown', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'brown'],
        ['brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown'],
    ]
    img = create_tile(subway)
    save_tile(img, 'special', 'subway')

    # 地下鉄マーク（Mマーク）
    metro = [
        ['brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown'],
        ['brown', 'white', 'white', 'white', 'white', 'white', 'white', 'brown'],
        ['brown', 'white', 'red', 'red', 'red', 'red', 'white', 'brown'],
        ['brown', 'white', 'red', 'white', 'white', 'red', 'white', 'brown'],
        ['brown', 'white', 'red', 'white', 'white', 'red', 'white', 'brown'],
        ['brown', 'white', 'red', 'red', 'red', 'red', 'white', 'brown'],
        ['brown', 'white', 'white', 'white', 'white', 'white', 'white', 'brown'],
        ['brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown', 'brown'],
    ]
    img = create_tile(metro)
    save_tile(img, 'special', 'metro')

    # 海港（拡張版）
    seaport = [
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
        ['blue', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'blue'],
        ['blue', 'gray', 'brown', 'brown', 'brown', 'brown', 'gray', 'blue'],
        ['blue', 'gray', 'brown', 'red', 'red', 'brown', 'gray', 'blue'],
        ['blue', 'gray', 'brown', 'red', 'red', 'brown', 'gray', 'blue'],
        ['blue', 'gray', 'brown', 'brown', 'brown', 'brown', 'gray', 'blue'],
        ['blue', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'blue'],
        ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue'],
    ]
    img = create_tile(seaport)
    save_tile(img, 'port', 'seaport')

def main():
    """メイン関数"""
    print("=" * 60)
    print("🎨 不足タイル生成ツール / Missing Tile Generator")
    print("=" * 60)
    print()

    generated = 0

    # 基本インフラ
    print("📍 基本インフラ / Basic Infrastructure")
    generate_road_tiles()
    generate_rail_tiles()
    generate_wire_tiles()
    generated += 3

    # RCIゾーン
    print("\n🏠 RCIゾーン / RCI Zones")
    generate_zone_tiles()
    generated += 12  # residential(4) + commercial(4) + industrial(4)

    # 公園
    print("\n🌳 公園 / Parks")
    generate_park_tiles()
    generated += 3

    # ユーティリティ
    print("\n⚡ ユーティリティ / Utilities")
    generate_utility_tiles()
    generated += 4

    # 発電所
    print("\n💡 発電所 / Power Plants")
    generate_power_tiles()
    generated += 1

    # 農業
    print("\n🌾 農業 / Agriculture")
    generate_agricultural_tiles()
    generated += 1

    # 交通
    print("\✈️ 交通 / Transport")
    generate_transport_tiles()
    generated += 6

    print()
    print("=" * 60)
    print(f"✅ 生成完了：{generated}個のタイルを生成しました")
    print("=" * 60)

if __name__ == "__main__":
    main()
