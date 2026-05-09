# 🏙️ ConcLand - シティシミュレーション

ConcLandは、オリジナルのSimCity (1989)にインスパイアされたミニマルなシティシミュレーションゲームです。
Pyxelゲームエンジンを使用してPythonで実装されています。

## 🚀 クイックスタート

### 必要な環境
- Python 3.8以上
- Pyxel 2.0以上

### インストール
```bash
pip install pyxel
```

### ゲームの実行
```bash
# 標準実行
python main.py

# 拡張版（新システム有効）を試す
python3 launch_with_enhancements.py

# オリジナル版を明示的に実行
python main.py --mode original

# デバッグモードで実行
python main.py --debug
```

**新しい機能（拡張版のみ）**:
- 🎨 改善されたUI（通知、ツールチップ、フィードバック）
- 🏛️ 新しいゲームシステム（水道、地下、犯罪、火災、称号）
- 🔧 詳細なデバッグモード（CLI、LLM出力）
- 🎵 BGM/SFXシステム（プレースホルダー実装）

## 🎮 ゲームの操作

### 基本操作
- **矢印キー**: カーソル移動
- **数字キー 1-9**: ツール選択
  - 1: 住宅ゾーン
  - 2: 商業ゾーン  
  - 3: 工業ゾーン
  - 4: 道路
  - 5: 鉄道
  - 6: 電線
  - 7: 公園
  - 8: 警察署
  - 9: 消防署
- **0**: ブルドーザー（削除）
- **スペース/Z**: 建物配置
- **X**: 建物削除
- **V**: 表示モード切り替え（通常/汚染/地価/電力/交通）

### セーブ/ロード
- **O**: セーブ
- **I**: ロード
- **T**: 地形のみセーブ

### その他
- **Q**: ゲーム終了

### 拡張版の追加操作
- **F1**: デバッグモード切替（拡張版のみ）
- **F2**: 音楽再生/停止（拡張版のみ）
- **?**: キーボードショートカットヘルプ（拡張版のみ）

## 🏗️ ゲームシステム

### RCIゾーニング
- **Residential (住宅)**: 人口を提供
- **Commercial (商業)**: 雇用と税収を提供  
- **Industrial (工業)**: 雇用を提供、汚染を発生

### インフラストラクチャ
- **電力**: 発電所と送電線による電力供給
- **交通**: 道路と鉄道による輸送網
- **公共サービス**: 警察、消防、病院

### シミュレーション
- **汚染**: 工業地域から拡散、地価に影響
- **地価**: 汚染、公園、商業施設からの距離で決定
- **成長**: RCI需要バランスに基づく自動発展

## 📁 プロジェクト構造

```
ConcLand/
├── main.py                           # メイン実行ファイル
├── launch_with_enhancements.py      # 拡張ランチャー（新システム有効）
├── concland_mini.py                 # メインゲームロジック
├── enhanced_title_menu.py           # 改善版タイトルメニュー
├── ui_enhancements.py               # UI強化システム
├── new_game_systems.py              # 新しいゲームシステム
├── verbose_debug_system.py          # デバッグシステム
├── bgm_sfx_system.py                # オーディオシステム
├── config/                          # 設定ファイル
├── assets/                          # ゲームアセット（+30個の新規タイル）
├── data/                            # セーブデータ
├── misc/                            # その他のツール・テスト
├── docs/                            # ドキュメント
├── ENHANCED_SYSTEMS_GUIDE.md        # 新システム使用ガイド
├── INTEGRATION_GUIDE.md             # 統合ガイド
├── PROJECT_COMPLETION_SUMMARY.md    # プロジェクト完了サマリー
└── IMPROVEMENT_PROJECT_REPORT.md    # 詳細プロジェクト報告
```

## 🔧 開発者向け

### 新しいシステム（2026-05-10実装）
- **ui_enhancements.py** - UI強化（通知、ツールチップ、フィードバック）
- **new_game_systems.py** - 新しいゲームシステム（水道、地下、犯罪、火災、称号）
- **verbose_debug_system.py** - 詳細なデバッグシステム（CLI、LLM出力）
- **bgm_sfx_system.py** - オーディオシステム（BGM、SFX、アンビエント）
- **enhanced_title_menu.py** - 改善されたタイトルメニュー

### 既存システム
- `traffic_system.py` - 交通管理
- `economic_system.py` - 経済シミュレーション
- `disaster_system.py` - 災害システム
- `visual_system.py` - ビジュアル強化

### 設定とモジュール
- `config/game_config.py` - ゲーム設定
- `config/modules.json` - モジュール管理
- `core/module_manager.py` - 動的モジュールローディング

### 統合ツール
- `launch_with_enhancements.py` - 拡張ランチャー（新システム有効）
- `simple_integrate.py` - 簡易統合ツール
- `ENHANCED_SYSTEMS_GUIDE.md` - 新しいシステムの使用ガイド
- `INTEGRATION_GUIDE.md` - 統合ガイド（手動統合用）

### テストとツール
```bash
# プロジェクト分析
python misc/tools/organize_project_v2.py --mode analyze

# 統合テスト
python integration_test.py
```

## 📝 ライセンス

このプロジェクトはオープンソースです。

## 🤝 貢献

バグ報告や機能提案を歓迎します。

---

🎮 **楽しい都市建設を！**