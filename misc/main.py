#!/usr/bin/env python3
"""
ConcLand - 都市シミュレーションゲーム
Main entry point
"""
import sys
import os

def main():
    """メインエントリーポイント"""
    print("=================================================================")
    print("  ConcLand - 都市シミュレーション")
    print("=================================================================")
    print()
    print("【操作方法】")
    print("  移動: 矢印キー or WASD")
    print("  ツール選択: パレットをクリック")
    print("  建物配置: マップ上でクリック")
    print("  表示切替: Tab or M")
    print("  一時停止: Space")
    print("  速度変更: 1-3")
    print()
    print("【ツールショートカット】")
    print("  R: 住宅  C: 商業  I: 工業  D: 道路")
    print("  P: 発電所  A: 農業  S: 太陽光  W: 風力")
    print("  N: 原子力  G: ガス  K: 公園  J: 神社")
    print("  X: 削除")
    print()
    print("起動中...")
    print("=================================================================")
    
    # city_sim.pyを実行
    from city_sim import City
    
    try:
        city = City()
    except KeyboardInterrupt:
        print("\nゲーム終了")
        sys.exit(0)
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()