#!/usr/bin/env python3
"""
ConcLand ランチャー（新システム対応版）
ConcLand Launcher with New Systems Support

統合を変更せず、ラッパー経由で新しいシステムを有効化します
"""

import sys
import os

# 現在のディレクトリをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("="*70)
print("🚀 ConcLand Enhanced Launcher")
print("="*70)
print()

# 新しいシステムのチェック
print("🔍 新しいシステムをチェック中...")
systems_available = True
try:
    from ui_enhancements import UIEnhancementSystem, NotificationType
    from new_game_systems import NewGameSystems
    from verbose_debug_system import IntegratedDebugSystem
    from bgm_sfx_system import AudioSystem, MusicTrack, SoundEffect
    print("✅ すべての新しいシステムが利用可能です")
except ImportError as e:
    print(f"⚠️  一部のシステムが利用できません: {e}")
    systems_available = False
    print("   標準モードで起動します")

print()

# 通常通り起動
try:
    import pyxel
    from concland_mini import ConcLandMini

    # ゲームインスタンス作成
    print("🎮 ゲームを初期化中...")
    game = ConcLandMini()

    # 新しいシステムが利用可能な場合、追加の初期化
    if systems_available:
        print("🔧 新しいシステムを初期化中...")
        try:
            # UI強化システム
            game.ui_enhancements = UIEnhancementSystem(320, 288)
            game.ui_enhancements.use_japanese = True
            print("  ✅ UI Enhancement System")

            # 新しいゲームシステム
            game.new_systems = NewGameSystems(100)
            game.new_systems.population = game.total_population
            game.new_systems.buildings_count = 0
            game.new_systems.funds = game.funds
            print("  ✅ New Game Systems")

            # デバッグシステム（デフォルト無効）
            game.debug_system = IntegratedDebugSystem()
            if game.dev_mode:
                game.debug_system.enable_debug()
            print("  ✅ Debug System (ready)")

            # オーディオシステム
            game.audio_system = AudioSystem()
            game.audio_system.initialize()
            print("  ✅ Audio System")

            print("✅ 新しいシステムの初期化完了")

        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            print("   標準モードで続行します")

    print()
    print("🎮 ゲームを起動します...")
    print("💡 ヒント:")
    print("  - Q: 終了")
    print("  - F1: デバッグモード切替（デバッグシステムがある場合）")
    print("  - F2: 音楽切替（オーディオシステムがある場合）")
    print()

    # オリジナルの update メソッドをラップ
    original_update = game.update
    def enhanced_update():
        # オリジナルの更新
        original_update()

        # 新しいシステムの更新
        if systems_available and hasattr(game, 'ui_enhancements'):
            try:
                # UI強化システムの更新
                if game.ui_enhancements:
                    game.ui_enhancements.update()

                # 新しいゲームシステムの更新
                if hasattr(game, 'new_systems') and game.new_systems:
                    game.new_systems.population = game.total_population
                    game.new_systems.buildings_count = sum(1 for row in game.grid for cell in row if cell != 0 if hasattr(game, 'grid') else 0)
                    game.new_systems.funds = game.funds
                    game.new_systems.update(game.grid if hasattr(game, 'grid') else None, game.sim_data if hasattr(game, 'sim_data') else None)

                # オーディオシステムの更新
                if hasattr(game, 'audio_system') and game.audio_system:
                    game.audio_system.update(1/60.0)

            except Exception as e:
                # エラーを表示しても続行
                pass

    # オリジナルの draw メソッドをラップ
    original_draw = game.draw
    def enhanced_draw():
        # オリジナルの描画
        original_draw()

        # 新しいUIシステムの描画
        if systems_available and hasattr(game, 'ui_enhancements') and game.ui_enhancements:
            try:
                game.ui_enhancements.draw()
            except:
                pass

    # ゲーム実行
    pyxel.run(enhanced_update, enhanced_draw)

except KeyboardInterrupt:
    print("\\n👋 ゲームを終了しました")
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
