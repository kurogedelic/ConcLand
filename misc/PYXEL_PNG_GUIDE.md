# Pyxel PNG画像読み込み・表示ガイド

## 基本的な使用方法

### 1. 画像読み込み
```python
# 基本構文
pyxel.images[0].load(0, 0, "image.png")
# または
pyxel.image(0).load(0, 0, "image.png")

# 引数説明:
# - 第1引数 (x): 256x256バッファ内のX座標オフセット
# - 第2引数 (y): 256x256バッファ内のY座標オフセット  
# - 第3引数: 画像ファイルパス
```

### 2. 画像表示
```python
# blt関数を使用
pyxel.blt(x, y, img, u, v, w, h, [colkey])

# 引数説明:
# - x, y: 画面上の描画位置
# - img: 画像バンク番号 (0-2)
# - u, v: 画像バンク内の切り出し開始位置
# - w, h: 切り出しサイズ
# - colkey: 透明色 (省略可能)
```

## 制限事項

### 画像仕様
- **対応形式**: PNG形式のみ
- **最大サイズ**: 256x256ピクセル
- **画像バンク数**: 3つまで (0, 1, 2)
- **タイルマップ**: 8つまで

### 色制限
- 標準: 16色パレット自動変換
- 拡張: 256色パレット対応 (特別な設定が必要)

## よくある問題と解決方法

### 1. 画像が表示されない
**原因A: ファイルパス問題**
```python
# ❌ 相対パスは環境によって失敗する
pyxel.images[0].load(0, 0, "assets/tile.png")

# ✅ 絶対パスを使用
import os
abs_path = os.path.abspath("assets/tile.png")
pyxel.images[0].load(0, 0, abs_path)
```

**原因B: 画像バンク範囲外**
```python
# ❌ バンク3以上は存在しない
pyxel.images[3].load(0, 0, "image.png")  # エラー

# ✅ バンク0-2のみ使用
pyxel.images[0].load(0, 0, "image.png")  # OK
```

**原因C: 座標範囲外**
```python
# ❌ 256x256を超える座標
pyxel.images[0].load(300, 300, "image.png")  # 範囲外

# ✅ 0-255の範囲内
pyxel.images[0].load(0, 0, "image.png")  # OK
```

### 2. VSCodeデバッグモードでの問題
VSCodeでデバッグ実行すると`pyxel.image().load()`が失敗する既知の問題

**解決方法:**
```python
import os

def load_image_safe(bank, x, y, filename):
    """VSCode対応の安全な画像読み込み"""
    try:
        # 相対パスを試す
        pyxel.images[bank].load(x, y, filename)
        print(f"Loaded: {filename}")
        return True
    except FileNotFoundError:
        # 絶対パスに変換して再試行
        abs_path = os.path.abspath(filename)
        try:
            pyxel.images[bank].load(x, y, abs_path)
            print(f"Loaded with absolute path: {abs_path}")
            return True
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            return False
```

### 3. 256色拡張パレット使用時
```python
# 256色パレットを先に読み込み
if os.path.exists("assets/palette256.png"):
    pyxel.images[1].load(0, 0, "assets/palette256.png", incl_colors=True)

# その後、通常の画像読み込み
pyxel.images[0].load(0, 0, "assets/tilemap.png")
```

## デバッグ方法

### 1. 読み込み確認
```python
def check_image_loaded(bank):
    """画像バンクにデータが読み込まれているか確認"""
    try:
        # ピクセルを読み取って確認
        pixel = pyxel.images[bank].pget(0, 0)
        print(f"Image bank {bank} pixel (0,0): {pixel}")
        return pixel is not None
    except:
        print(f"Image bank {bank} is empty or invalid")
        return False
```

### 2. 画像内容確認
```python
def debug_image_content(bank, size=32):
    """画像バンクの内容をサンプル表示"""
    print(f"--- Image Bank {bank} Content ---")
    for y in range(0, size, 8):
        for x in range(0, size, 8):
            try:
                pixel = pyxel.images[bank].pget(x, y)
                print(f"({x:2},{y:2}): {pixel:2}", end=" ")
            except:
                print(f"({x:2},{y:2}): ??", end=" ")
        print()
```

## ベストプラクティス

### 1. 画像管理クラス
```python
class ImageManager:
    def __init__(self):
        self.loaded_images = {}
    
    def load_image(self, name, bank, x, y, filename):
        """名前付きで画像を管理"""
        if load_image_safe(bank, x, y, filename):
            self.loaded_images[name] = {
                'bank': bank, 'x': x, 'y': y, 
                'filename': filename
            }
            return True
        return False
    
    def draw_image(self, name, screen_x, screen_y, w=16, h=16):
        """名前で画像を描画"""
        if name in self.loaded_images:
            img = self.loaded_images[name]
            pyxel.blt(screen_x, screen_y, img['bank'], 
                     img['x'], img['y'], w, h, 0)
```

### 2. タイルシステム
```python
class TileSystem:
    def __init__(self, tilemap_path, tile_size=16):
        self.tile_size = tile_size
        self.tiles = {}
        self.load_tilemap(tilemap_path)
    
    def load_tilemap(self, path):
        """タイルマップを読み込み"""
        if load_image_safe(0, 0, 0, path):
            # タイル位置を定義
            self.define_tiles()
            return True
        return False
    
    def draw_tile(self, tile_id, x, y):
        """タイルID指定で描画"""
        if tile_id in self.tiles:
            pos = self.tiles[tile_id]
            pyxel.blt(x, y, 0, pos[0], pos[1], 
                     self.tile_size, self.tile_size, 0)
```

## 注意事項

1. **画像形式**: PNG以外は事前変換が必要
2. **ファイルパス**: 可能な限り絶対パスを使用
3. **バンク管理**: 0-2の範囲内で計画的に使用
4. **メモリ制限**: 256x256×3枚の制限を考慮した設計
5. **デバッグ環境**: VSCodeなどでは特別な対応が必要

---

**参考資料**:
- [Pyxel公式ドキュメント (日本語)](https://github.com/kitao/pyxel/blob/main/docs/README.ja.md)
- [VSCodeデバッグ問題の対処法](https://qiita.com/2dgames_jp/items/4c8070decf685e8f9698)