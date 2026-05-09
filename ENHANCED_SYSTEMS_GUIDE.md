# 新しいシステムの統合と使用方法
# Integration and Usage Guide for New Systems

## 🚀 クイックスタート / Quick Start

### 方法1: 拡張ランチャーを使用（推奨）
```bash
python3 launch_with_enhancements.py
```
この方法は、既存のコードを変更せずに新しいシステムを有効化します。

### 方法2: 標準起動（新システム無効）
```bash
python3 main.py
```
既存のゲームプレイにはこちらをお使いください。

## 📦 新しいシステムの概要

### 1. UI強化システム (ui_enhancements.py)
- **通知システム**: 建物配置時などの自動通知
- **ツールチップ**: カーソル位置の情報表示
- **フィードバックエフェクト**: アクション時の視覚的フィードバック
- **キーボードショートカットヘルプ**: ?キーでヘルプ表示

### 2. 新しいゲームシステム (new_game_systems.py)
- **水道供給システム**: 水源、配管、カバレッジ計算
- **地下開発システム**: 地下鉄駅、掘削レベル
- **犯罪システム**: 犯罪率シミュレーション
- **火災システム**: 火災リスク評価
- **都市称号システム**: 5段階称号と実績

### 3. デバッグシステム (verbose_debug_system.py)
- **詳細ログ**: 5段階ログレベル
- **CLIモード**: 10種類のコマンド
- **LLMフレンドリー出力**: 構造化データエクスポート

### 4. オーディオシステム (bgm_sfx_system.py)
- **効果音**: 22種類のSFX
- **音楽**: 6種類のBGMトラック
- **アンビエント**: 環境音
- **オーディオフック**: 8種類のイベントフック

## 🎮 拡張ランチャーの機能

### 自動統合
- 新しいシステムを自動的に初期化
- オリジナルの `update()` と `draw()` をラップ
- エラーが発生しても続行（フォールバック）

### ホットキー
- **F1**: デバッグモードのオン/オフ
- **F2**: 音楽の再生/停止

## 📝 手動統合を行う場合

既存のコードを直接変更する場合は、以下の手順で行います。

### ステップ1: インポート文の追加
`concland_mini.py` の約55行目あたりに追加：

```python
# New Enhanced Systems
try:
    from ui_enhancements import UIEnhancementSystem, NotificationType
    from new_game_systems import NewGameSystems
    from verbose_debug_system import IntegratedDebugSystem
    from bgm_sfx_system import AudioSystem, MusicTrack, SoundEffect
    ENHANCED_SYSTEMS_AVAILABLE = True
except ImportError:
    ENHANCED_SYSTEMS_AVAILABLE = False
```

### ステップ2: 初期化コードの追加
`ConcLandMini.__init__()` の最後に追加：

```python
if ENHANCED_SYSTEMS_AVAILABLE:
    self.ui_enhancements = UIEnhancementSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    self.new_systems = NewGameSystems(MAP_SIZE)
    self.debug_system = IntegratedDebugSystem()
    self.audio_system = AudioSystem()
    self.audio_system.initialize()
else:
    self.ui_enhancements = None
    self.new_systems = None
    self.debug_system = None
    self.audio_system = None
```

### ステップ3: 更新コードの追加
`ConcLandMini.update()` の最後に追加：

```python
if ENHANCED_SYSTEMS_AVAILABLE:
    if self.ui_enhancements:
        self.ui_enhancements.update()
    
    if self.new_systems:
        self.new_systems.population = self.total_population
        self.new_systems.buildings_count = sum(1 for row in self.grid for cell in row if cell != CellType.EMPTY)
        self.new_systems.funds = self.funds
        self.new_systems.update(self.grid, self.sim_data)
    
    if self.audio_system:
        self.audio_system.update(1/60.0)
```

### ステップ4: 描画コードの追加
`ConcLandMini.draw()` の `_draw_ui()` 呼び出しの後に追加：

```python
if ENHANCED_SYSTEMS_AVAILABLE and self.ui_enhancements:
    self.ui_enhancements.draw()
```

## 🧪 テスト方法

### 基本テスト
```bash
python3 launch_with_enhancements.py
```

### 詳細テスト
1. ゲームが正常に起動するか
2. 建物を配置してみる
3. F1キーでデバッグモードを切替
4. F2キーで音楽を再生

## 🔧 トラブルシューティング

### インポートエラー
```bash
# 新しいシステムファイルが同じディレクトリにあるか確認
ls -la ui_enhancements.py new_game_systems.py verbose_debug_system.py bgm_sfx_system.py
```

### パフォーマンス問題
新しいシステムが重い場合は、`launch_with_enhancements.py` で該当システムの初期化をコメントアウトしてください。

### 既存機能との競合
拡張ランチャーを使えば、既存のコードを変更せずに新しいシステムを試せます。

## 📚 関連ドキュメント

- `PROJECT_COMPLETION_SUMMARY.md`: プロジェクト完了サマリー
- `IMPROVEMENT_PROJECT_REPORT.md`: 詳細な技術レポート
- `INTEGRATION_GUIDE.md`: 統合ガイド（手動統合用）

## 💡 ベストプラクティス

1. **開発中**: 拡張ランチャーを使用（コード変更不要）
2. **本番**: 手動統合後に `main.py` を更新
3. **デバッグ**: 拡張ランチャーのF1モードを使用
4. **テスト**: 各システムを個別に有効/無効を切り替えてテスト
