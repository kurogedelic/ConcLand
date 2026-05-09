#!/usr/bin/env python3
"""
新システム統合パッチ
Integration Patch for New Systems

concland_mini.py に新しいシステムを統合するためのパッチファイル
"""

# 新しいインポート文の追加
NEW_IMPORTS = '''
# ========================================
# 新システムのインポート
# New system imports
# ========================================
try:
    from ui_enhancements import UIEnhancementSystem, NotificationType
    from new_game_systems import NewGameSystems
    from verbose_debug_system import IntegratedDebugSystem
    from bgm_sfx_system import AudioSystem, MusicTrack, SoundEffect
    ENHANCED_SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced systems not available: {e}")
    ENHANCED_SYSTEMS_AVAILABLE = False
'''

# ConcLandMini クラスへの追加
INIT_CODE_ADDITIONS = '''
        # ========================================
        # 新システムの初期化
        # Initialize new systems
        # ========================================
        if ENHANCED_SYSTEMS_AVAILABLE:
            # UI強化システム
            self.ui_enhancements = UIEnhancementSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.ui_enhancements.use_japanese = True

            # 新しいゲームシステム
            self.new_systems = NewGameSystems(MAP_SIZE)

            # デバッグシステム（デフォルト無効）
            self.debug_system = IntegratedDebugSystem()
            if dev_mode:
                self.debug_system.enable_debug()

            # オーディオシステム
            self.audio_system = AudioSystem()
            self.audio_system.initialize()
        else:
            self.ui_enhancements = None
            self.new_systems = None
            self.debug_system = None
            self.audio_system = None
'''

UPDATE_CODE_ADDITIONS = '''
        # ========================================
        # 新システムの更新
        # Update new systems
        # ========================================
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
'''

# 建物配置時のオーディオフック
BUILDING_AUDIO_HOOK = '''
        # オーディオフィードバック
        if self.audio_system:
            self.audio_system.trigger_hook("building_placed", cell_type.name.lower())
'''

# 通知表示の追加
NOTIFICATION_CODE = '''
        # UI通知の表示
        if self.ui_enhancements and self.message_timer > 0:
            # メッセージを通知システムにも表示
            if self.show_message:
                self.ui_enhancements.show_notification(
                    self.show_message,
                    self.show_message,  # 日本語メッセージをそのまま使用
                    NotificationType.INFO
                )
'''

def apply_patch(file_path: str = "concland_mini.py"):
    """
    パッチを適用する
    Apply patch to file
    """
    print(f"🔧 パッチ適用中: {file_path}")

    # ファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # インポート文の追加（ファイルの先頭付近）
    if "from ui_enhancements import" not in content:
        # インポートセクションを探す
        import_section_end = content.find("from title_menu_system import")
        if import_section_end > 0:
            # 該当位置までの内容を取得
            before_imports = content[:import_section_end]
            after_imports = content[import_section_end:]

            # 新しいインポートを追加
            content = before_imports + NEW_IMPORTS + after_imports
            print("  ✅ 新しいインポート文を追加")

    # ConcLandMini クラスの __init__ メソッドに初期化コードを追加
    if ENHANCED_SYSTEMS_AVAILABLE and "self.ui_enhancements = UIEnhancementSystem" not in content:
        # これは簡易的な実装。実際には __init__ メソッドを探して追加する必要があります
        print("  ⚠️  自動統合は複雑なため、手動での統合を推奨します")
        print("  📝 統合ガイドを作成しました")

        return False

    # パッチを保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  ✅ パッチ適用完了")
    return True

def create_integration_guide():
    """
    統合ガイドを作成
    Create integration guide
    """
    guide = """# 新システム統合ガイド / New Systems Integration Guide

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

"""

    with open("INTEGRATION_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(guide)

    print("  📖 統合ガイドを作成しました: INTEGRATION_GUIDE.md")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "concland_mini.py"

    create_integration_guide()

    # 安全のため、自動パッチは適用せず、ガイドのみ作成
    print("\n" + "="*60)
    print("🔧 統合ガイドを作成しました")
    print("="*60)
    print("\n次のステップ:")
    print("1. INTEGRATION_GUIDE.md を確認してください")
    print("2. 手動で concland_mini.py に統合してください")
    print("3. 統合後、python main.py でテストしてください")
    print("\nまたは:")
    print("python integration_patch.py concland_mini.py --auto")
    print("で自動パッチを試すこともできます（実験的）")
