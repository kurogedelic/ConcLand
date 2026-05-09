#!/usr/bin/env python3
"""
簡易統合スクリプト
Simple Integration Script for ConcLand

新しいシステムを concland_mini.py に統合するための簡易ツール
"""

import sys
import re
from pathlib import Path

def backup_file(file_path: str):
    """ファイルのバックアップを作成"""
    backup_path = f"{file_path}.bak"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return backup_path

def add_new_imports(content: str) -> str:
    """新しいインポート文を追加"""
    # インポート文を探す
    if "from ui_enhancements import" in content:
        print("  ✅ 新しいインポート文は既に追加されています")
        return content

    # 追加位置を探す（title_menu_system の後）
    marker = "from title_menu_system import GameLauncher"
    if marker in content:
        new_imports = '''
# New Enhanced Systems
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
        content = content.replace(marker, marker + new_imports)
        print("  ✅ 新しいインポート文を追加しました")
    else:
        print("  ⚠️  マーカーが見つかりませんでした")

    return content

def add_init_code(content: str) -> str:
    """__init__ メソッドに初期化コードを追加"""
    # 既に追加されているか確認
    if "self.ui_enhancements = UIEnhancementSystem" in content:
        print("  ✅ 初期化コードは既に追加されています")
        return content

    # train_system の初期化後を探す
    marker = "self.train_system = TrainSystem(MAP_SIZE)"
    if marker in content:
        init_code = '''
        # Initialize Enhanced Systems
        if ENHANCED_SYSTEMS_AVAILABLE:
            self.ui_enhancements = UIEnhancementSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.ui_enhancements.use_japanese = True

            self.new_systems = NewGameSystems(MAP_SIZE)
            self.new_systems.population = 0
            self.new_systems.buildings_count = 0
            self.new_systems.funds = self.funds

            self.debug_system = IntegratedDebugSystem()
            if self.dev_mode:
                self.debug_system.enable_debug()

            self.audio_system = AudioSystem()
            self.audio_system.initialize()
        else:
            self.ui_enhancements = None
            self.new_systems = None
            self.debug_system = None
            self.audio_system = None
'''
        content = content.replace(marker, marker + init_code)
        print("  ✅ 初期化コードを追加しました")
    else:
        print("  ⚠️  初期化コード追加位置が見つかりませんでした")

    return content

def add_update_code(content: str) -> str:
    """update メソッドに更新コードを追加"""
    # 既に追加されているか確認
    if "self.ui_enhancements.update()" in content:
        print("  ✅ 更新コードは既に追加されています")
        return content

    # _update_traffic の後を探す
    marker = "self._update_traffic()"
    if marker in content:
        # この行の後にインデントを維持してコードを追加
        update_code = '''
        # Update Enhanced Systems
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
'''
        # マーカーの後の行を探して、その後に追加
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if marker in line:
                # インデントを取得
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                # コードを行として追加
                update_lines = update_code.strip().split('\n')
                for j, update_line in enumerate(update_lines):
                    if update_line.strip():
                        lines.insert(i + 1 + j, spaces + update_line)
                break

        content = '\n'.join(lines)
        print("  ✅ 更新コードを追加しました")
    else:
        print("  ⚠️  更新コード追加位置が見つかりませんでした")

    return content

def add_draw_code(content: str) -> str:
    """draw メソッドに描画コードを追加"""
    # 既に追加されているか確認
    if "self.ui_enhancements.draw()" in content:
        print("  ✅ 描画コードは既に追加されています")
        return content

    # _draw_ui() の後を探す
    marker = "self._draw_ui()"
    if marker in content:
        draw_code = '''
        # Draw Enhanced UI
        if ENHANCED_SYSTEMS_AVAILABLE and self.ui_enhancements:
            self.ui_enhancements.draw()
'''
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if marker in line:
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                draw_lines = draw_code.strip().split('\n')
                for j, draw_line in enumerate(draw_lines):
                    if draw_line.strip():
                        lines.insert(i + 1 + j, spaces + draw_line)
                break

        content = '\n'.join(lines)
        print("  ✅ 描画コードを追加しました")
    else:
        print("  ⚠️  描画コード追加位置が見つかりませんでした")

    return content

def add_audio_hooks(content: str) -> str:
    """建物配置時にオーディオフックを追加"""
    # 既に追加されているか確認
    if "audio_system.trigger_hook" in content:
        print("  ✅ オーディオフックは既に追加されています")
        return content

    # 建物配置のコードを探す（シンプルな例）
    # "self.grid[y][x] = new_type" の後に追加
    marker = "self.grid[y][x] = new_type"
    if marker in content:
        audio_hook = '''
        # Audio feedback
        if self.audio_system:
            self.audio_system.trigger_hook("building_placed", new_type.name.lower())
'''
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if marker in line:
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                hook_lines = audio_hook.strip().split('\n')
                for j, hook_line in enumerate(hook_lines):
                    if hook_line.strip():
                        lines.insert(i + 1 + j, spaces + hook_line)
                break

        content = '\n'.join(lines)
        print("  ✅ オーディオフックを追加しました")
    else:
        print("  ℹ️  オーディオフック追加位置が見つかりませんでした（建物配置コード）")

    return content

def add_debug_hotkeys(content: str) -> str:
    """デバッグ用ホットキーを追加"""
    # 既に追加されているか確認
    if "pyxel.btnp(pyxel.KEY_F1)" in content:
        print("  ✅ デバッグホットキーは既に追加されています")
        return content

    # キー入力処理セクションを探す（pyxel.btnp(pyxel.KEY_Q) の後あたり）
    # 簡易的に、ファイルの末尾に追加する関数を作成
    debug_hotkeys = '''
    # Debug and enhancement hotkeys
    if pyxel.btnp(pyxel.KEY_F1):
        if self.debug_system:
            self.debug_system.verbose.enabled = not self.debug_system.verbose.enabled
            self.message_timer = 60
            self.show_message = f"Debug: {'ON' if self.debug_system.verbose.enabled else 'OFF'}"

    if pyxel.btnp(pyxel.KEY_F2):
        if self.audio_system:
            if self.audio_system.music_manager.is_playing:
                self.audio_system.music_manager.stop()
                self.message_timer = 60
                self.show_message = "Music: OFF"
            else:
                self.audio_system.play_music(MusicTrack.GAMEPLAY)
                self.message_timer = 60
                self.show_message = "Music: ON"
'''

    # update メソッドの最後を探す
    # "def _update_traffic" の前あたりに追加
    marker = "def _update_traffic"
    if marker in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if marker in line:
                # デバッグホットキーを追加（インデントなし、クラスメソッドとして）
                lines.insert(i, debug_hotkeys)
                break

        content = '\n'.join(lines)
        print("  ✅ デバッグホットキーを追加しました")
    else:
        print("  ℹ️  デバッグホットキー追加位置が見つかりませんでした")

    return content

def integrate_enhanced_systems(file_path: str = "concland_mini.py"):
    """新しいシステムを統合する"""
    print(f"🔧 統合開始: {file_path}")

    # バックアップ作成
    backup_path = backup_file(file_path)
    print(f"  💾 バックアップ作成: {backup_path}")

    # ファイル読み込み
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ ファイル読み込みエラー: {e}")
        return False

    # 変更を適用
    print("  🔨 変更を適用中...")
    content = add_new_imports(content)
    content = add_init_code(content)
    content = add_update_code(content)
    content = add_draw_code(content)
    content = add_audio_hooks(content)
    content = add_debug_hotkeys(content)

    # ファイル保存
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ 統合完了！")
        return True
    except Exception as e:
        print(f"  ❌ ファイル保存エラー: {e}")
        print(f"  💡 バックアップから復元: {backup_path}")
        # バックアップから復元
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        return False

def test_integration(file_path: str = "concland_mini.py"):
    """統合をテスト"""
    print(f"\n🧪 統合テスト: {file_path}")

    try:
        # イポートテスト
        print("  📦 インポートテスト...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 新しいインポートが含まれているか確認
        checks = [
            ("ui_enhancements", "UI Enhancement System"),
            ("new_game_systems", "New Game Systems"),
            ("verbose_debug_system", "Debug System"),
            ("bgm_sfx_system", "Audio System"),
            ("ENHANCED_SYSTEMS_AVAILABLE", "Enhanced Systems Flag")
        ]

        all_passed = True
        for check, name in checks:
            if check in content:
                print(f"    ✅ {name}: OK")
            else:
                print(f"    ❌ {name}: NOT FOUND")
                all_passed = False

        # 初期化コードの確認
        if "self.ui_enhancements = UIEnhancementSystem" in content:
            print("  ✅ 初期化コード: OK")
        else:
            print("  ❌ 初期化コード: NOT FOUND")
            all_passed = False

        # 更新コードの確認
        if "self.ui_enhancements.update()" in content:
            print("  ✅ 更新コード: OK")
        else:
            print("  ❌ 更新コード: NOT FOUND")
            all_passed = False

        # 描画コードの確認
        if "self.ui_enhancements.draw()" in content:
            print("  ✅ 描画コード: OK")
        else:
            print("  ❌ 描画コード: NOT FOUND")
            all_passed = False

        if all_passed:
            print("\n  🎉 すべてのチェックに合格しました！")
            return True
        else:
            print("\n  ⚠️  一部のチェックに失敗しました")
            return False

    except Exception as e:
        print(f"  ❌ テストエラー: {e}")
        return False

if __name__ == "__main__":
    import sys

    # コマンドライン引数の処理
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "concland_mini.py"

    print("="*70)
    print("🚀 ConcLand 新システム統合ツール")
    print("="*70)
    print()

    # 統合実行
    if integrate_enhanced_systems(file_path):
        # テスト実行
        if test_integration(file_path):
            print()
            print("="*70)
            print("✅ 統合完了！次のステップ：")
            print("="*70)
            print("1. python main.py でゲームを起動してテスト")
            print("2. F1キーでデバッグモードを切替")
            print("3. F2キーで音楽をオン/オフ")
            print("4. 建物を配置して通知を確認")
            print("5. 問題がない場合はコミットしてください")
            print()
            print("問題がある場合は:")
            print(f"  mv concland_mini.py.bak concland_mini.py")
            print("でバックアップを復元できます")
        else:
            print()
            print("⚠️  テストに失敗しました。手動での統合を推奨します")
            print("📖 INTEGRATION_GUIDE.md を参照してください")
    else:
        print()
        print("❌ 統合に失敗しました。バックアップを復元しました")
        print("📖 INTEGRATION_GUIDE.md を参照して手動で統合してください")

    print()
