# 新システム統合ガイド / New Systems Integration Guide

## 手動統合の手順 / Manual Integration Steps

### 1. インポート文の追加 / Add Imports

`concland_mini.py` のインポートセクション（約55行目）に以下を追加：

```python
# 新システムのインポート
try:
    from ui_enhancements import UIEnhancementSystem, NotificationType
    from new_game_systems import NewGameSystems
    from verbose_debug_system import IntegratedDebugSystem
    from bgm_sfx_system import AudioSystem, MusicTrack, SoundEffect
    ENHANCED_SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced systems not available: {e}")
    ENHANCED_SYSTEMS_AVAILABLE = False
```

### 2. ConcLandMini.__init__ に初期化コードを追加

`__init__` メソッドの最後（self.train_system の初期化後あたり）に追加：

```python
# 新システムの初期化
if ENHANCED_SYSTEMS_AVAILABLE:
    # UI強化システム
    self.ui_enhancements = UIEnhancementSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    self.ui_enhancements.use_japanese = True

    # 新しいゲームシステム
    self.new_systems = NewGameSystems(MAP_SIZE)

    # デバッグシステム（デフォルト無効）
    self.debug_system = IntegratedDebugSystem()
    if self.dev_mode:
        self.debug_system.enable_debug()

    # オーディオシステム
    self.audio_system = AudioSystem()
    self.audio_system.initialize()
else:
    self.ui_enhancements = None
    self.new_systems = None
    self.debug_system = None
    self.audio_system = None
```

### 3. update メソッドに更新コードを追加

`update` メソッドの最後に追加：

```python
# 新システムの更新
if ENHANCED_SYSTEMS_AVAILABLE:
    # UI強化システムの更新
    if self.ui_enhancements:
        self.ui_enhancements.update()

    # 新しいゲームシステムの更新
    if self.new_systems:
        self.new_systems.population = self.total_population
        self.new_systems.buildings_count = sum(1 for row in self.grid for cell in row if cell != CellType.EMPTY)
        self.new_systems.funds = self.funds
        self.new_systems.update(self.grid, self.sim_data)

    # オーディオシステムの更新
    if self.audio_system:
        self.audio_system.update(1/60.0)
```

### 4. 建物配置時にオーディオフックを追加

建物を配置するコード（例：`_place_building` メソッド）に追加：

```python
# オーディオフィードバック
if self.audio_system:
    self.audio_system.trigger_hook("building_placed", cell_type.name.lower())
```

### 5. draw メソッドに描画コードを追加

`draw` メソッドの最後（`_draw_ui()` の後）に追加：

```python
# 新しいUIシステムの描画
if ENHANCED_SYSTEMS_AVAILABLE and self.ui_enhancements:
    self.ui_enhancements.draw()
```

### 6. キーボードショートカットの追加

`update` メソッドのキー入力処理セクションに追加：

```python
# デバッグモード切替
if pyxel.btnp(pyxel.KEY_F1):
    if self.debug_system:
        self.debug_system.verbose.enabled = not self.debug_system.verbose.enabled
        self.message_timer = 60
        self.show_message = "デバッグモード: " + ("ON" if self.debug_system.verbose.enabled else "OFF")

# 音楽再生切替
if pyxel.btnp(pyxel.KEY_F2):
    if self.audio_system:
        if self.audio_system.music_manager.is_playing:
            self.audio_system.music_manager.stop()
        else:
            self.audio_system.play_music(MusicTrack.GAMEPLAY)
```

## テスト / Testing

統合後、以下をテストしてください：

1. ゲームが正常に起動するか
2. 建物配置時に通知が表示されるか
3. UI強化が動作しているか
4. 新しいゲームシステム（水道、地下など）が更新されているか
5. F1キーでデバッグモードが切替わるか
6. F2キーで音楽が再生されるか

## トラブルシューティング / Troubleshooting

### インポートエラー
- 新しいシステムファイルが同じディレクトリにあるか確認
- PYTHONPATH が正しく設定されているか確認

### パフォーマンス問題
- `ENHANCED_SYSTEMS_AVAILABLE = False` に設定して無効化
- 個別のシステムを無効化して問題を特定

### 既存機能との競合
- 各システムを個別に有効/無効を切り替えてテスト
- 既存のUI描画と新しいUIが重ならないように確認

