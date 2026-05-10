#!/usr/bin/env python3
"""
ConcLand Simplified Controls Patch

Simplifies key controls for better usability
"""

# 新しいオンスクリーンなヘルプ表示
SIMPLE_HELP_DISPLAY = """
╔══════════════════════════════════════════╗
║  🎮 操作ガイド - Hキーで閉じる              ║
╠══════════════════════════════════════════╣
║                                            ║
║ 【🎯 目的】                                 ║
║ 🏠 住宅を建てて市を発展させる            ║
║                                            ║
║ 【📍 移動】                                 ║
║ ⬆️⬇️⬅️➡️ 矢印キー か K/J/H/L              ║
║                                            ║
║ 【🏗️ 建設】                               ║
║ スペースキー または Z キー                    ║
║ → カーソル位置に建物を配置                 ║
║                                            ║
║ 【🗑️ 削除】                               ║
║ X キー                                      ║
║ → カーソル位置を削除（元に戻す）             ║
║                                            ║
║ 【🔧 ツール】                               ║
║ 数字キー 1-9 で選択:                        ║
║  1 住宅 / 2 商業 / 3 工業                   ║
║ 4 道路 / 5 鉄道 / 6 電線                     ║
║ 7 公園 / 8 公共 / 9 電力                     ║
║ 0 削除                                       ║
║                                            ║
║ 【👁 表示】                                 ║
║ V キーで表示を切替 (通常⇔汚染⇔地価⇔電力⇔交通)  ║
║                                            ║
║ 【❓ ヘルプ】                               ║
║ H キーでこのヘルプ表示/非表示                 ║
║                                            ║
║ 【🚪 終了】                               ║
║ Q キー または ESC キー                        ║
║                                            ║
║ 【💾 保存】                                 ║
║ S+O セーブ / S+I ロード                        ║
║                                            ║
╚══════════════════════════════════════════╝

💡 ヒント:
・道路沿いに住宅を配置すると発展しやすいです
・電線を引くと発展が早まります
・公園や警察があると地価が上がります
"""

def show_startup_tutorial():
    """起動時にチュートリアルを表示"""
    return """
==========================================================================
🎮 よCarbonへようこそ！ Welcome to ConcLand!
==========================================================================

🎮 はじめてプレイされる方向けに、基本操作を紹介します。

📋 やること:

1. まずは道路を作りましょう
   → 数字キーの「4」を押して「道路」を選択
   → カーソルを移動して「スペース」キーで配置

2. 住宅を作りましょう
   → 数字キーの「1」を押して「住宅」を選択
   → 道路に隣接する場所に「スペース」キーで配置

3. 電線を引きましょう
   → 数字キーの「6」を押して「電線」を選択
   → 住宅や道路に重なるように「スペース」キーで配置

4. 発電所を建てましょう
   → 数字キーの「9」を押して「発電所」を選択
   → 資金が足りない場合は、待機してから

5. 時間が経つと都市が発展します
   → 人口が増えると税収入が増えます
   → さらに多くの施設を建てられるようになります

🆘 ヘルプ:
・ゲーム中に「H」キーを押すと、いつでもこのヘルプが表示されます
・「V」キーで表示モードを切り替えて、都市の状態を確認できます

✨ それでは、楽しい都市建設を！Have fun!
==========================================================================
"""

# onscreen_help_display コード
def draw_simplified_help(screen_width, screen_height, current_tool, funds):
    """簡素化されたオンスクリーンヘルプ表示"""

    help_width = 250
    help_height = 180

    # 背景（半透明黒）
    overlay_x = (screen_width - help_width) // 2
    overlay_y = (screen_height - help_height) // 2

    # 外枠
    pyxel.rect(overlay_x, overlay_y, help_width, help_height, 0)
    pyxel.rectb(overlay_x, overlay_y, help_width, help_height, 7)

    # タイトル
    pyxel.text((screen_width - 30) // 2, overlay_y + 8, "操作ガイド", 7)

    # 内容
    y = overlay_y + 25

    # 移動
    pyxel.text(overlay_x + 10, y, "移動: ⬆️⬇️⬅️➡️", 6)
    y += 12
    pyxel.text(overlay_x + 10, y, "建物: スペース", 6)
    y += 12
    pyxel.text(overlay_x + 10, y, "削除: X", 6)
    y += 20

    # ツール一覧（簡易版）
    pyxel.text(overlay_x + 10, y, "ツール:", 6)
    y += 12

    tools = [
        ("1", "住宅", "green"),
        ("2", "商業", "blue"),
        ("3", "工業", "orange"),
        ("4", "道路", "gray"),
        ("5", "鉄道", "dark_gray"),
        ("6", "電線", "yellow"),
        ("7", "公園", "light_green"),
        ("8", "公共", "pink"),
        ("9", "電力", "purple"),
        ("0", "削除", "red"),
    ]

    for num, name, color in tools:
        tool_num = int(num)
        is_selected = (current_tool == tool_num)

        # 選択中のツールを強調
        if is_selected:
            pyxel.rect(overlay_x + 8, y - 2, help_width - 16, 12, 6)

        # 数字とツール名
        pyxel.text(overlay_x + 12, y, num, 10 if is_selected else 7)
        pyxel.text(overlay_x + 30, y, name, 10 if is_selected else 6)

        y += 11

    y += 15

    # その他機能
    pyxel.text(overlay_x + 10, y, "その他:", 6)
    y += 12
    pyxel.text(overlay_x + 12, y, "V: 表示切替", 7)
    y += 10
    pyxel.text(overlay_x + 12, y, "H: ヘルプ", 7)
    y += 10
    pyxel.text(overlay_x + 12, y, "Q: 終了", 7)
    y += 10
    pyxel.text(overlay_x + 12, y, f"資金: ¥{funds:,}", 11)

    # 終了方法
    y += 15
    pyxel.text(overlay_x + 10, y, "終了方法:", 6)
    y += 10
    pyxel.text(overlay_x + 12, y, "Q キー", 7)
    pyxel.text(overlay_x + 70, y, "または", 5)
    pyxel.text(ax(overlay_x + 90), y, "ESC", 7)

# 使用例
if __name__ == "__main__":
    print(show_startup_tutorial())

    # 簡略版キー割り当ての提案
    print("\n" + "="*70)
    print("💡 よりシンプルなキー割り当ての提案:")
    print("="*70)
    print("""
現在の問題点:
- 数字キー1-9でツール選択 → 直感的ではない
- 多くのキーを覚える必要がある

改善案:
- WASD + クリック選択（PCゲーム標準）
- マウス対応
- よ�り直感的なUI
    """)

# メインファイル用パッチの例
MAIN_FILE_PATCH = '''
# update メソッドに追加
def update(self):
    # 既存の処理...

    # Hキーでヘルプ切替
    if pyxel.btnp(pyxel.KEY_H):
        self.help_visible = not self.help_visible

    # ヘルプタイマーの更新
    if self.help_visible:
        self.help_timer -= 1
        if self.help_timer <= 0:
            self.help_visible = False

# draw メソッドに追加
def draw(self):
    # 既存の描画...

    # 簡素化されたヘルプ表示
    if self.help_visible:
        draw_simplified_help(SCREEN_WIDTH, SCREEN_HEIGHT, self.current_tool, self.funds)
'''
