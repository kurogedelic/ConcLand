# ConcLand Mini 最小限ファイル分析

## 必須ファイル（絶対に必要）

### 1. メインプログラム
- **concland_mini.py** - メインゲームファイル (1089行)
- **concland_tile_system.py** - PNGタイル管理システム

### 2. フォントシステム
- **assets/font/bdfrenderer.py** - BDFフォントレンダラー
- **assets/font/umplus_j10r.bdf** - 日本語フォント（推奨）
- **assets/font/umplus_j12r.bdf** - 日本語フォント（代替）

### 3. タイルアセット（いずれか1つ）
- **assets/concland_tiles_16x16.png** - 生成された16x16タイルマップ
- **assets/concland_tiles_indexed.png** - インデックスカラー版（推奨）
- **assets/concland_tiles_rgb.png** - RGB版（代替）

### 4. 256色パレット（オプション）
- **assets/palette256.png** - 256色拡張パレット

## 削除可能ファイル（大容量・不要）

### デバッグ・テスト関連
```
basic_png_test.py
correct_png_test.py
debug_concland.py  
debug_tile_draw.py
fixed_tile_test.py
quick_test.py
simple_png_viewer.py
test_png_display.py
test_short.py
```

### バックアップ・世代管理
```
backup/ (フォルダ全体)
city_sim.py (元ファイル)
city_sim_backup.py
concland_mini_backup.py
```

### 過去プロジェクト関連
```
micropolis/ (フォルダ全体)
core/
ui/
tools/
systems/
tile_system.py (旧版)
tile_definitions.py
voronoi_terrain.py
config.py
utils.py
main.py
```

### アセット生成スクリプト
```
generate_16x16_tilemap.py
generate_mini_assets.py
convert_png_for_pyxel.py
```

### 個別タイル（統合済み）
```
tiles/ (フォルダ全体)
```

### 使用されていないアセット
```
assets/building_sprites.png
assets/tilemap_generated.png
assets/tiles_16x16.png (小さすぎる)
assets/tool_icons.png
assets/ui_icons.png
assets/ui_panels.png
```

### ドキュメント類
```
README.md
README_MICROPOLIS.md
PYXEL_PNG_GUIDE.md
docs/
data/
concland_debug.log
```

## 最小限構成

### ファイル構造
```
ConcLand_Mini/
├── concland_mini.py
├── concland_tile_system.py
├── assets/
│   ├── font/
│   │   ├── bdfrenderer.py
│   │   └── umplus_j10r.bdf
│   ├── concland_tiles_indexed.png
│   └── palette256.png
└── CLAUDE.md (プロジェクト情報)
```

### 総サイズ予想
- concland_mini.py: ~50KB
- concland_tile_system.py: ~10KB  
- bdfrenderer.py: ~5KB
- umplus_j10r.bdf: ~200KB
- concland_tiles_indexed.png: ~5KB
- palette256.png: ~1KB
- **合計: 約271KB** (元の数GBから大幅削減)

## インポート依存関係チェック

### concland_mini.py の依存
```python
import pyxel                    # 外部ライブラリ
import random                   # 標準ライブラリ  
import sys, os                  # 標準ライブラリ
from enum import Enum           # 標準ライブラリ
from dataclasses import dataclass # 標準ライブラリ
from typing import List, Tuple, Optional # 標準ライブラリ
from concland_tile_system import ConcLandTileManager # ローカル
from font.bdfrenderer import BDFRenderer # ローカル
```

### concland_tile_system.py の依存
```python
import pyxel                    # 外部ライブラリ
import os                       # 標準ライブラリ
from typing import Dict, Tuple, Optional # 標準ライブラリ
```

### font/bdfrenderer.py の依存
```python
import pyxel                    # 外部ライブラリ
```

## 実行環境要件

### 必要なPythonパッケージ
```bash
pip install pyxel
```

### 実行コマンド
```bash
python concland_mini.py
```

## クリーンアップスクリプト

不要ファイルを削除するスクリプトも作成可能：
```bash
# バックアップフォルダ削除
rm -rf backup/
rm -rf micropolis/
rm -rf core/ ui/ tools/ systems/

# テストファイル削除
rm *test*.py debug*.py

# 不要アセット削除
rm assets/building_sprites.png
rm assets/tilemap_generated.png
rm -rf tiles/
```

## 動作確認

最小限構成での動作確認が必要：
1. PNG読み込み成功
2. 日本語フォント表示
3. ゲーム操作正常
4. シミュレーション動作