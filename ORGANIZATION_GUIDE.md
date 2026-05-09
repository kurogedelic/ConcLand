# ConcLand プロジェクト整理ガイド 📂

## 現在の状況

プロジェクトは大規模に成長し、整理が必要な状態です：
- **32個のPythonファイル**がルートディレクトリに散在
- **10個の主要システム**が実装完了
- **200以上のアセットファイル**

## 整理ツール

### `organize_project.py`
プロジェクト全体を自動整理するツールを作成しました。

#### 使用方法

1. **ドライラン（確認のみ）**
```bash
python3 organize_project.py
```
実際にファイルを移動せず、何が行われるか確認できます。

2. **実行（ファイル移動）**
```bash
python3 organize_project.py --execute
```
実際にファイルを整理された構造に移動します。

## 整理後の構造

```
ConcLand/
├── core/               # コアゲームファイル
│   ├── concland_mini.py
│   ├── image_tile_system.py
│   ├── diagonal_coastline_system.py
│   └── terrain_generator.py
│
├── systems/            # ゲームシステム
│   ├── traffic_system.py
│   ├── economic_system.py
│   ├── disaster_system.py
│   ├── difficulty_system.py
│   ├── tutorial_system.py
│   ├── sound_effects_system.py
│   ├── goals_challenges_system.py
│   ├── title_menu_system.py
│   ├── train_system.py
│   └── advanced_ui.py
│
├── fixes/              # バグ修正・パッチ
│   ├── rci_zone_fix.py
│   ├── apply_rci_fix.py
│   └── fix_cars_overlay.py
│
├── tools/              # ユーティリティツール
│   ├── convert_*.py    # 変換ツール
│   ├── create_*.py     # 作成ツール
│   ├── generate_*.py   # 生成ツール
│   ├── debug_*.py      # デバッグツール
│   └── test_*.py       # テストツール
│
├── tests/              # 統合テスト
│   └── integration_test.py
│
├── backups/            # バックアップ
│   ├── concland_mini_backup_rci.py
│   └── concland_mini_fixed.py
│
├── data/               # データファイル
│   ├── saves/          # セーブファイル
│   ├── terrain/        # 地形データ
│   └── config/         # 設定ファイル
│
├── docs/               # ドキュメント
│   ├── API_REFERENCE.md
│   ├── GAME_ARCHITECTURE.md
│   ├── SOUND_EFFECTS_GUIDE.md
│   └── その他のガイド
│
├── assets/             # アセット（既に整理済み）
│   ├── tiles/
│   ├── icons/
│   └── font/
│
└── misc/               # その他（既に整理済み）
    ├── micropolis/
    └── old_versions/
```

## 整理後の実行方法

### 方法1: メインエントリで実行（推奨）
```bash
# 通常起動
python3 main.py
```

### 方法2: 直接実行
```bash
# 整理前
python3 concland_mini.py

# 整理後
python3 core/concland_mini.py
```

### 方法3: インポート修正
整理後、インポートパスの調整が必要な場合：

```python
# システムパスに追加
import sys
sys.path.append('.')
sys.path.append('./systems')
sys.path.append('./core')
```

## 利点

### 1. **構造の明確化**
- ファイルの役割が一目瞭然
- 新規開発者も理解しやすい

### 2. **メンテナンス性向上**
- バグ修正とコアコードの分離
- システムごとの独立性

### 3. **開発効率化**
- 必要なファイルを素早く見つけられる
- 関連ファイルがグループ化

### 4. **バージョン管理改善**
- 変更の影響範囲が明確
- コンフリクトの減少

## 注意事項

### インポートパス
整理後、一部のインポートパスの調整が必要になる場合があります：

```python
# 整理前
from rci_zone_fix import RCIZoneManager

# 整理後
from fixes.rci_zone_fix import RCIZoneManager
# または
sys.path.append('./fixes')
from rci_zone_fix import RCIZoneManager
```

### セーブデータ
- セーブデータは`data/saves/`に移動されます
- ゲームは自動的に新しい場所を検索します

### 実行可能性
- `main.py` を実行すれば起動します
- 手動実行時はパスに注意

## クリーンアップ

### 一時ファイル削除
```bash
# cleanup.shスクリプト実行
./cleanup.sh

# または手動で
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".DS_Store" -delete
```

## トラブルシューティング

### Q: ゲームが起動しない
A: `python3 main.py` を使用するか、`python3 core/concland_mini.py` を実行

### Q: インポートエラー
A: システムパスに必要なディレクトリを追加

### Q: セーブデータが見つからない
A: `data/saves/`ディレクトリを確認

### Q: 元に戻したい
A: バックアップから復元可能

## まとめ

プロジェクト整理により：
- ✅ 開発効率の向上
- ✅ コードの保守性改善
- ✅ チーム開発の容易化
- ✅ 将来の拡張性確保

整理を実行する準備ができたら：
```bash
python3 organize_project.py --execute
```

---

作成日: 2025-08-21
最終更新: 2025-08-21
