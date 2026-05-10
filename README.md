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
- **矢印キー**: カーソル移動（K/J/H/Lでも可能）
- **スペース/Z**: 建物配置
- **X**: 建物削除

### ツール選択（QWERTY配列で直感的に）
- **Q**: 住宅ゾーン
- **W**: 商業ゾーン
- **E**: 工業ゾーン
- **R**: 道路
- **T**: 鉄道・駅（繰り返しで切替）
- **Y**: 公園（繰り返しで切替）
- **U**: 電線
- **I**: 発電所（繰り返しで切替）
- **O**: 港湾施設（繰り返しで切替）
- **P**: 公共施設（繰り返しで切替）
- **A**: 農業
- **バックスラッシュ(\)**: ブルドーザー（削除）

### 便利な機能
- **H**: 操作ガイドの表示/非表示（ゲーム中いつでも確認可能）
- **V**: 表示モード切り替え（通常/汚染/地価/電力/交通）
- **B**: ツールパレット表示（全ツール一覧から選択）

### 詳細UIパネル
- **S**: 統計パネル
- **E**: 経済パネル
- **T**: 交通パネル
- **D**: 災害パネル
- **P**: 政策パネル

### その他
- **M**: RCI統合チェック
- **N**: セーブ（2回押しで確定）
- **ESC**: UIパネルを閉じる（ゲームは終了しません）

### ゲームの終了方法
- ゲームを終了するには、ゲームウィンドウの閉じるボタン（×）をクリックしてください
- ESCキーではゲームは終了しません（UIパネルを閉じるのみ）

### ヘルプシステム
ゲーム中に「H」キーを押すと、いつでも簡素化された操作ガイドが表示されます。初回起動時には自動的にチュートリアルが表示されます。

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