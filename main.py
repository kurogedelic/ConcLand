#!/usr/bin/env python3
"""
ConcLand メイン実行ファイル
ConcLand Main Entry Point

モジュラー化されたConcLandシティシミュレーションゲームのメインエントリーポイント。
Main entry point for the modularized ConcLand city simulation game.

使用方法 / Usage:
    python main.py [options]

オプション / Options:
    --mode original    オリジナル版を実行 / Run original version
    --mode modular     モジュラー版を実行（デフォルト） / Run modular version (default)
    --debug           デバッグモードで実行 / Run in debug mode
    --config FILE     設定ファイルを指定 / Specify config file
"""

import sys
import os
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def main():
    """
    メイン関数
    Main function
    """
    parser = argparse.ArgumentParser(
        description="ConcLand シティシミュレーションゲーム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例 / Examples:
    python main.py                    # モジュラー版を実行
    python main.py --mode original    # オリジナル版を実行
    python main.py --debug           # デバッグモードで実行
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["original", "modular"],
        default="modular",
        help="実行モード: original（オリジナル版）、modular（モジュラー版、デフォルト）"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="デバッグモードで実行"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="設定ファイルのパス"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🎮 ConcLand シティシミュレーション")
    print("=" * 50)
    
    try:
        if args.mode == "original":
            print("📄 オリジナル版を起動中...")
            from concland_mini import ConcLandMini
            game = ConcLandMini()
            
        elif args.mode == "modular":
            print("🔧 モジュラー版を起動中...")
            # モジュラー版は後で実装予定
            print("⚠️ モジュラー版は開発中です。オリジナル版を実行します。")
            from concland_mini import ConcLandMini
            game = ConcLandMini()
            
            # デバッグモードの設定
            if args.debug:
                if hasattr(game, 'config'):
                    game.config['debug_mode'] = True
                print("🐛 デバッグモードが有効です")
            
            # カスタム設定ファイル
            if args.config:
                config_path = Path(args.config)
                if config_path.exists():
                    print(f"⚙️ 設定ファイルを読み込み: {config_path}")
                    # TODO: 設定ファイルの読み込み処理
                else:
                    print(f"⚠️ 設定ファイルが見つかりません: {config_path}")
        
        # ゲームを実行
        if hasattr(game, 'run'):
            game.run()
        else:
            # オリジナル版の場合
            import pyxel
            pyxel.run(game.update, game.draw)
            
    except ImportError as e:
        print(f"❌ モジュールのインポートエラー: {e}")
        print("必要なファイルが見つからない可能性があります。")
        return 1
        
    except KeyboardInterrupt:
        print("\n👋 ゲームを終了します")
        return 0
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())