# ConcLand プロジェクト構造 / Project Structure

## 📁 推奨ディレクトリ構成 / Recommended Directory Structure

```
ConcLand/
│
├── 📄 README.md                    # プロジェクト概要
├── 📄 CLAUDE.md                    # Claude Code用ガイド
├── 📄 PROJECT_STRUCTURE.md        # このファイル
│
├── 🎮 concland_mini.py            # メインゲームファイル
├── 🎮 main.py                     # エントリーポイント
│
├── 📁 core/                       # コアシステム
│   ├── base_game.py               # 基底ゲームクラス
│   ├── module_manager.py          # モジュール管理システム
│   └── __init__.py
│
├── 📁 config/                     # 設定ファイル
│   ├── game_config.py             # ゲーム設定
│   ├── modules.json               # モジュール設定
│   └── user_settings.json         # ユーザー設定
│
├── 📁 systems/                    # ゲームシステム
│   ├── traffic_system.py          # 交通システム
│   ├── economic_system.py         # 経済システム
│   ├── disaster_system.py         # 災害システム
│   ├── sound_effects_system.py    # サウンドシステム
│   ├── visual_system.py           # ビジュアルシステム
│   ├── train_system.py            # 鉄道システム
│   ├── tutorial_system.py         # チュートリアル
│   ├── difficulty_system.py       # 難易度管理
│   ├── goals_challenges_system.py # 目標・チャレンジ
│   └── __init__.py
│
├── 📁 ui/                         # UIコンポーネント
│   ├── advanced_ui.py             # 高度なUI
│   ├── advanced_window_system.py  # ウィンドウシステム
│   ├── data_visualization.py      # データ可視化
│   ├── title_menu_system.py       # タイトル・メニュー
│   └── __init__.py
│
├── 📁 world/                      # ワールド生成
│   ├── terrain_generator.py       # 地形生成
│   ├── diagonal_coastline_system.py # 海岸線処理
│   ├── image_tile_system.py       # タイル描画システム
│   └── __init__.py
│
├── 📁 assets/                     # ゲームアセット
│   ├── tiles/                     # タイル画像
│   ├── icons/                     # アイコン画像
│   ├── font/                      # フォントファイル
│   └── sounds/                    # サウンドファイル（将来）
│
├── 📁 data/                       # ゲームデータ
│   ├── economy/                   # 経済データ
│   │   └── resources.json
│   ├── saves/                     # セーブデータ
│   │   ├── savegame.dat
│   │   └── terrain_100.dat
│   └── scenarios/                 # シナリオデータ（将来）
│
├── 📁 docs/                       # ドキュメント
│   ├── API_REFERENCE.md           # API リファレンス
│   ├── GAME_ARCHITECTURE.md       # ゲームアーキテクチャ
│   ├── guides/                    # 各種ガイド
│   └── tutorials/                 # チュートリアル文書
│
├── 📁 tests/                      # テストファイル
│   ├── integration_test.py        # 統合テスト
│   ├── test_systems.py            # システムテスト
│   └── test_reports/              # テストレポート
│
├── 📁 tools/                      # 開発ツール
│   ├── organize_project.py        # プロジェクト整理
│   ├── create_clean_map_100.py    # マップ生成
│   └── debug_tools/               # デバッグツール
│
└── 📁 misc/                       # その他のファイル
    ├── old_versions/              # 旧バージョン
    ├── experiments/               # 実験的コード
    └── references/                # 参考資料

```

## 🔧 モジュール化の原則 / Modularization Principles

### 1. 単一責任の原則 (Single Responsibility)
各モジュールは一つの明確な責任を持つ：
- `traffic_system.py` → 交通管理のみ
- `economic_system.py` → 経済システムのみ
- `disaster_system.py` → 災害シミュレーションのみ

### 2. 依存関係の管理 (Dependency Management)
```python
# module_manager.pyで依存関係を定義
DEPENDENCIES = {
    "advanced_window_system": ["visual_system"],
    "data_visualization": ["visual_system"],
    "tutorial_system": [],
}
```

### 3. インターフェースの統一 (Unified Interface)
```python
class GameSystem(ABC):
    """すべてのゲームシステムの基底クラス"""
    
    @abstractmethod
    def initialize(self, game_instance):
        """初期化"""
        pass
    
    @abstractmethod
    def update(self, *args, **kwargs):
        """更新処理"""
        pass
    
    @abstractmethod
    def draw(self, *args, **kwargs):
        """描画処理"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """クリーンアップ"""
        pass
```

## 📦 パッケージ化の提案 / Package Structure Proposal

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="concland",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyxel>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'concland=concland.main:run',
        ],
    },
)
```

## 🔄 移行計画 / Migration Plan

### Phase 1: 現状整理 (Current State)
- [x] ファイルリストの作成
- [x] 依存関係の分析
- [ ] 不要ファイルの特定

### Phase 2: ディレクトリ再構成 (Directory Restructure)
- [ ] systemsフォルダへの移動
- [ ] uiフォルダへの移動
- [ ] worldフォルダの作成

### Phase 3: インポート修正 (Import Updates)
- [ ] 相対インポートの修正
- [ ] パスの更新
- [ ] テストの実行

### Phase 4: クリーンアップ (Cleanup)
- [ ] miscへの旧ファイル移動
- [ ] 不要ファイルの削除
- [ ] ドキュメントの更新

## 🎯 改善の優先順位 / Improvement Priorities

### 高優先度 (High Priority)
1. **コメントの追加** - すべての主要関数にdocstring
2. **型ヒントの追加** - Pythonの型システムを活用
3. **設定の外部化** - ハードコードされた値を設定ファイルへ

### 中優先度 (Medium Priority)
1. **エラーハンドリング** - try-except節の追加
2. **ロギングシステム** - デバッグ用のログ機能
3. **単体テスト** - 各モジュールのテスト作成

### 低優先度 (Low Priority)
1. **パフォーマンス最適化** - プロファイリングと最適化
2. **国際化** - 多言語サポート
3. **プラグインシステム** - 外部モジュール対応

## 📝 コーディング規約 / Coding Standards

```python
"""
モジュールの説明
Module description

このモジュールの詳細な説明
Detailed description of this module
"""

from typing import Optional, List, Dict, Any
import logging

# ロガーの設定
logger = logging.getLogger(__name__)


class ExampleClass:
    """
    クラスの説明
    Class description
    """
    
    def __init__(self, param: str) -> None:
        """
        初期化メソッド
        
        Args:
            param: パラメータの説明
        """
        self.param = param
    
    def example_method(self, value: int) -> Optional[str]:
        """
        メソッドの説明
        
        Args:
            value: 引数の説明
            
        Returns:
            戻り値の説明
            
        Raises:
            ValueError: エラーの説明
        """
        if value < 0:
            raise ValueError("値は正の数である必要があります")
        
        return str(value) if value > 0 else None
```

## 🚀 次のステップ / Next Steps

1. **自動整理スクリプトの実行**
   ```bash
   python organize_project.py --mode restructure
   ```

2. **インポートの更新**
   ```bash
   python organize_project.py --mode update-imports
   ```

3. **テストの実行**
   ```bash
   python -m pytest tests/
   ```

4. **ドキュメント生成**
   ```bash
   python generate_docs.py
   ```

この構造により、ConcLandは保守性が高く、拡張しやすいプロジェクトになります。
