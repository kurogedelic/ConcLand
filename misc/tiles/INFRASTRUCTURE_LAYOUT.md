# Infrastructure Tiles Structure

This document describes the organization of infrastructure tiles in the ConcLand project.

## Directory Structure

```
tiles/
├── road/           # 道路タイル
│   ├── alone.png
│   ├── horizontal.png
│   ├── vertical.png
│   ├── corner_ne.png
│   ├── corner_se.png
│   ├── corner_sw.png
│   ├── corner_nw.png
│   ├── t_north.png
│   ├── t_south.png
│   ├── t_east.png
│   ├── t_west.png
│   └── cross.png
├── terrain/        # 地形タイル（海岸線含む）
│   ├── coastline_1000.png  # 北のみ
│   ├── coastline_0100.png  # 東のみ
│   ├── coastline_0010.png  # 南のみ
│   ├── coastline_0001.png  # 西のみ
│   ├── coastline_1010.png  # 北南
│   ├── coastline_0101.png  # 東西
│   ├── coastline_1100.png  # 北東
│   ├── coastline_0110.png  # 東南
│   ├── coastline_0011.png  # 南西
│   ├── coastline_1001.png  # 西北
│   ├── coastline_1110.png  # 3方向（西なし）
│   ├── coastline_1101.png  # 3方向（南なし）
│   ├── coastline_1011.png  # 3方向（東なし）
│   ├── coastline_0111.png  # 3方向（北なし）
│   ├── coastline_1111.png  # 4方向全て
│   └── ...
└── rail/           # 線路タイル（将来実装）
    ├── alone.png
    ├── horizontal.png
    ├── vertical.png
    ├── corner_ne.png
    ├── corner_se.png
    ├── corner_sw.png
    ├── corner_nw.png
    ├── t_north.png
    ├── t_south.png
    ├── t_east.png
    ├── t_west.png
    └── cross.png
```

## Tile Patterns

### Road Tiles
- `alone`: 単独の道路（終端）
- `horizontal`: 横方向の直線
- `vertical`: 縦方向の直線
- `corner_[ne/se/sw/nw]`: コーナー（北東/南東/南西/北西）
- `t_[north/south/east/west]`: T字路
- `cross`: 十字路

### Coastline Tiles
海岸線パターンは4桁のバイナリコードで表現：
- 1桁目: 北に陸地があるか (1=あり, 0=なし)
- 2桁目: 東に陸地があるか
- 3桁目: 南に陸地があるか
- 4桁目: 西に陸地があるか

### Rail Tiles (将来実装)
道路と同様のパターンを持つ予定

## Usage in Code

tile_system.pyが各ディレクトリからタイルを読み込み、適切なIDで管理：
- 道路タイル: `road_[pattern]` (e.g., `road_horizontal`, `road_cross`)
- 海岸線タイル: `terrain_coastline_[code]` (e.g., `terrain_coastline_1000`)
- 線路タイル: `rail_[pattern]` (将来実装)