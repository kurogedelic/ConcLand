#!/usr/bin/env python3
"""
ConcLand Final System Check
最終動作確認とクイックスタートガイド
"""

import os
import sys
import json
from pathlib import Path

def check_system():
    """システム全体のチェック"""
    print("""
    ╔════════════════════════════════════════╗
    ║     ConcLand - Final System Check      ║
    ╚════════════════════════════════════════╝
    """)
    
    results = {
        'ready': True,
        'warnings': [],
        'recommendations': []
    }
    
    # 1. Python version check
    print("1️⃣ Python バージョン確認...")
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"  ⚠️ Python {python_version.major}.{python_version.minor} (3.8+ 推奨)")
        results['warnings'].append("Python 3.8以上を推奨")
    
    # 2. Pyxel check
    print("\n2️⃣ Pyxel 確認...")
    try:
        import pyxel
        print(f"  ✅ Pyxel インストール済み")
    except ImportError:
        print("  ❌ Pyxel未インストール")
        print("     pip install pyxel でインストール")
        results['ready'] = False
    
    # 3. Main game files
    print("\n3️⃣ ゲームファイル確認...")
    game_files = {
        'concland_mini.py': '通常版',
        'concland_mini_fixed.py': 'RCI修正版',
        'run_game.py': 'ゲームランチャー'
    }
    
    available_versions = []
    for file, name in game_files.items():
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"  ✅ {name}: {file} ({size:.1f}KB)")
            if 'mini' in file:
                available_versions.append(file)
        else:
            print(f"  ❌ {name}: {file} not found")
    
    # 4. Systems check
    print("\n4️⃣ 実装システム確認...")
    systems = [
        ('交通管理', 'traffic_system.py'),
        ('経済', 'economic_system.py'),
        ('災害', 'disaster_system.py'),
        ('サウンド', 'sound_effects_system.py'),
        ('ビジュアル', 'visual_system.py'),
        ('RCI修正', 'rci_zone_fix.py')
    ]
    
    implemented = 0
    for name, file in systems:
        if os.path.exists(file):
            print(f"  ✅ {name}")
            implemented += 1
        else:
            print(f"  ⚠️ {name} (オプション)")
    
    print(f"\n  実装率: {implemented}/{len(systems)} システム")
    
    # 5. Asset check
    print("\n5️⃣ アセット確認...")
    asset_dirs = ['assets', 'assets/tiles', 'assets/icons', 'assets/font']
    assets_ok = True
    for dir_path in asset_dirs:
        if os.path.exists(dir_path):
            file_count = len(list(Path(dir_path).glob('**/*')))
            print(f"  ✅ {dir_path}: {file_count} files")
        else:
            print(f"  ❌ {dir_path} not found")
            assets_ok = False
    
    # 6. Save files
    print("\n6️⃣ セーブデータ確認...")
    save_files = ['savegame.dat', 'terrain_100.dat']
    for save_file in save_files:
        if os.path.exists(save_file):
            size = os.path.getsize(save_file) / 1024
            print(f"  ✅ {save_file} ({size:.1f}KB)")
        else:
            print(f"  ℹ️ {save_file} なし (新規ゲーム)")
    
    # Results
    print("\n" + "="*50)
    print("📊 診断結果")
    print("="*50)
    
    if results['ready'] and available_versions:
        print("✅ ゲーム実行可能！\n")
        print("🎮 実行方法:")
        
        if 'concland_mini.py' in available_versions:
            print("  通常版:")
            print("    python3 concland_mini.py")
        
        if 'concland_mini_fixed.py' in available_versions:
            print("  RCI修正版:")
            print("    python3 concland_mini_fixed.py")
        
        if os.path.exists('run_game.py'):
            print("  ランチャー使用:")
            print("    python3 run_game.py")
        
        print("\n📝 操作方法:")
        print("  矢印キー: カーソル移動")
        print("  1-9, 0: ツール選択")
        print("  Space/Z: 配置")
        print("  X: 削除")
        print("  V: 表示モード切替")
        print("  O: セーブ")
        print("  I: ロード")
        print("  Q: 終了")
        
        if results['warnings']:
            print("\n⚠️ 警告:")
            for warning in results['warnings']:
                print(f"  - {warning}")
        
        if implemented == len(systems):
            print("\n🌟 全システム実装済み！最高のゲーム体験が可能です。")
        elif implemented >= 4:
            print("\n✨ 主要システム実装済み。充実したゲーム体験が可能です。")
        
    else:
        print("❌ 実行に必要な要件が不足しています\n")
        if not results['ready']:
            print("必要な対処:")
            print("  1. pip install pyxel でPyxelをインストール")
        if not available_versions:
            print("  2. ゲームファイルが見つかりません")
    
    # Save report
    report = {
        'timestamp': str(Path.cwd()),
        'python_version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
        'game_ready': results['ready'] and bool(available_versions),
        'available_versions': available_versions,
        'implemented_systems': implemented,
        'warnings': results['warnings']
    }
    
    with open('system_check_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n📄 詳細レポート: system_check_report.json")
    
    return results['ready'] and bool(available_versions)

def main():
    """メイン関数"""
    ready = check_system()
    
    if ready:
        print("\n" + "="*50)
        print("🚀 ConcLand 起動準備完了!")
        print("="*50)
        
        response = input("\n今すぐゲームを起動しますか？ (y/n): ")
        if response.lower() == 'y':
            import subprocess
            
            # Try to run the game
            if os.path.exists('run_game.py'):
                subprocess.run([sys.executable, 'run_game.py'])
            elif os.path.exists('concland_mini_fixed.py'):
                subprocess.run([sys.executable, 'concland_mini_fixed.py'])
            elif os.path.exists('concland_mini.py'):
                subprocess.run([sys.executable, 'concland_mini.py'])
        else:
            print("\nそれでは、準備ができたら以下のコマンドで起動してください:")
            print("  python3 concland_mini.py")
    
    return 0 if ready else 1

if __name__ == "__main__":
    sys.exit(main())