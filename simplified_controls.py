"""
簡素化された操作システム
Simplified Control System for ConcLand

キー操作をわかりやすく、直感的に改善
"""

class SimplifiedControls:
    """簡素化された操作体系"""

    # 基本操作の簡素化
    BASIC_CONTROLS = """
🎮 わ曲な操作ガイド / Simple Controls Guide

====================================
│ 基本 │ Basic Controls
====================================

移動 / Movement:
  ⬆️⬇️⬅️➡️  カーソル移動 / Move cursor

建設 / Building:
  スペース または Zキー
  カーソル位置に建物を配置
  Space or Z key
  Place building at cursor

削除 / Demolish:
  X キー
  カーソル位置を削除
  X key
  Remove at cursor

キャンセル / Cancel:
  ESC キー
  操作をキャンセル
  ESC key
  Cancel current action

====================================
│ メニュー │ Menu Controls
====================================

ツール選択 / Tool Selection:
  1-9 の数字キーでツールを選択
  1: 住宅 / Residential
  2: 商業 / Commercial
  3: 工業 / Industrial
  4: 道路 / Road
  5: 鉄道 / Rail
  6: 電線 / Wire
  7: 公園 / Park
  8: 発物 / Building (警察・消防など)
  9: 発物 / Building (発電所など)

  0: 削除 / Bulldozer

表示切替 / View Modes:
  V キーで以下を切替
  1. 通常 / Normal View
  2. 汚染 / Pollution
  3. 地価 / Land Value
  4. 電力 / Power Grid
  5. 交通 / Traffic

====================================
│ システム │ System Controls
====================================

セーブ / Save:
  S + O = セーブ (S to Save)
  / Save game

ロード / Load:
  S + I = ロード (S + I to Load)
  / Load game

終了 / Quit:
  Q キー / Q key
  / Quit game

====================================
│ 🎯 新しい簡単操作（拡張版）│
====================================

より直感的な操作のために、以下の改善を実装:

1. マウスクリック対応
2. ツールホイール表示
3. オンスクリーンなヘルプ
4. 操作のアニメーション
"""

    # 改善されたキー割り当て
    IMPROVED_CONTROLS = {
        # 基本操作
        "MOVE_UP": {"keys": ["UP", "K"], "jp": "上", "en": "Up"},
        "MOVE_DOWN": {"keys": ["DOWN", "J"], "jp": "下", "en": "Down"},
        "MOVE_LEFT": {"keys": ["LEFT", "H"], "jp": "左", "en": "Left"},
        "MOVE_RIGHT": {"keys": ["RIGHT", "L"], "jp": "右", "en": "Right"},

        # アクション
        "BUILD": {"keys": ["SPACE", "Z", "ENTER"], "jp": "配置", "en": "Build"},
        "DEMOLISH": {"keys": ["X", "DELETE", "BACKSPACE"], "jp": "削除", "en": "Demolish"},
        "CANCEL": {"keys": ["ESCAPE"], "jp": "キャンセル", "en": "Cancel"},

        # ツール選択（より直感的に）
        "TOOL_RESEDENTIAL": {"keys": ["1"], "jp": "住宅 (1)", "en": "Residential (1)"},
        "TOOL_COMMERCIAL": {"keys": ["2"], "jp": "商業 (2)", "en": "Commercial (2)"},
        "TOOL_INDUSTRIAL": {"keys": ["3"], "jp": "工業 (3)", "en": "Industrial (3)"},
        "TOOL_ROAD": {"keys": ["4"], "jp": "道路 (4)", "en": "Road (4)"},
        "TOOL_RAIL": {"keys": ["5"], "jp": "鉄道 (5)", "en": "Rail (5)"},
        "TOOL_WIRE": {"keys": ["6"], "jp": "電線 (6)", "en": "Wire (6)"},
        "TOOL_PARK": {"keys": ["7"], "jp": "公園 (7)", "en": "Park (7)"},
        "TOOL_SERVICE": {"keys": ["8"], "jp": "公共(8)", "en": "Service (8)"},
        "TOOL_POWER": {"keys": ["9"], "jp": "発電所(9)", "en": "Power (9)"},
        "TOOL_BULLDOZE": {"keys": ["0"], "jp": "削除(0)", "en": "Bulldoze (0)"},

        # 表示切替
        "VIEW_CYCLE": {"keys": ["V"], "jp": "表示切替", "en": "Cycle views"},

        # システム
        "SAVE": {"keys": ["S", "O"], "jp": "セーブ (S+O)", "en": "Save (S+O)"},
        "LOAD": {"keys": ["S", "I"], "jp": "ロード (S+I)", "en": "Load (S+I)"},
        "QUIT": {"keys": ["Q"], "jp": "終了", "en": "Quit"},
    }

    # 簡略版コントロール（初心者向け）
    BEGINNER_CONTROLS = """
🎮 初心者向け操作ガイド / Beginner's Guide

＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
│  基本操作 │ │ Basic Controls
＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

📍 移動
    ⬆️⬇️⬅️➡️  矢印キー または K/J/H/L
    移動したい方向のキーを押す

🏗️ 建物を置く
    スペース または Z
    カーソルの場所に建物が建ちます

🗑️ 建物を壊す
    X
    カーソルの場所の建物が壊れます

🔧 ツールを選ぶ
    数字キー 1-9
    1=住宅  2=商業  3=工業
    4=道路  5=鉄道  6=電線
    7=公園  8=公共建物  9=発電所
    0=削除ツール

👁 表示を変える
    V キー
    普通 → 汚染 → 地価 → 電力 → 交通
    の順に変わります

💾 セーブ・ロード
    S + O でセーブ
    S + I でロード

🚪 終了
    Q キー
"""

    # ヘルプ表示の改善案
    ONSCREEN_HELP = """
┌─────────────────────────────┐
│  🏙️ ConcLand 操作ガイド  │
├─────────────────────────────┤
│ ←→: 移動                   │
│                            │
│ スペース: 建物               │
│ X: 削除                     │
│                            │
│ [1]住宅 [2]商業 [3]工業    │
│ [4]道路 [5]鉄道 [6]電線      │
│ [7]公園 [8]公共 [9]電力      │
│ [0]削除                     │
│                            │
│ V: 表示切替                  │
│ Q: 終了                     │
└─────────────────────────────┘
"""

class SimplifiedUIHelper:
    """簡素化UIヘルパー"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.show_help = False
        self.help_timer = 0

    def toggle_help(self):
        """ヘルプ表示を切替"""
        self.show_help = not self.show_help
        self.help_timer = 300  # 5秒間表示

    def update(self):
        """更新処理"""
        if self.help_timer > 0:
            self.help_timer -= 1
            if self.help_timer == 0:
                self.show_help = False

    def draw(self, current_tool: int, funds: int, use_japanese: bool = True):
        """ヘルプを描画"""
        if not self.show_help:
            return

        # 背景（半透明）
        overlay_x = (self.screen_width - 300) // 2
        overlay_y = (self.screen_height - 200) // 2

        # 外枠
        pyxel.rect(overlay_x, overlay_y, 300, 200, 0)
        pyxel.rectb(overlay_x, overlay_y, 300, 200, 7)

        # タイトル
        if use_japanese:
            title = "🎮 操作ガイド"
        else:
            title = "🎮 Controls Guide"
        title_x = (self.screen_width - len(title) * 4) // 2
        pyxel.text(title_x, overlay_y + 10, title, 7)

        # 操作説明
        y_offset = 35

        # 基本操作
        pyxel.text(overlay_x + 15, overlay_y + y_offset, "基本操作:", 6)
        y_offset += 15
        pyxel.text(overlay_x + 20, overlay_y + y_offset, "⬆️⬇️⬅️➡️ 移動", 7)
        y_offset += 12
        pyxel.text(overlay_x + 20, overlay_y + y_offset, "スペース 建物配置", 7)
        y_offset += 12
        pyxel.text(overlay_x + 20, overlay_y + y_offset, "X 削除", 7)
        y_offset += 20

        # ツール一覧
        pyxel.text(overlay_x + 15, overlay_y + y_offset, "ツール:", 6)
        y_offset += 15

        tools = [
            ("1", "住宅", "R"),
            ("2", "商業", "C"),
            ("3", "工業", "I"),
            ("4", "道路", "Road"),
            ("5", "鉄道", "Rail"),
            ("6", "電線", "Wire"),
            ("7", "公園", "Park"),
            ("8", "公共", "Svc"),
            ("9", "電力", "Pwr"),
            ("0", "削除", "Bull"),
        ]

        for num, name_jp, name_en in tools:
            # 現在のツールをハイライト
            is_selected = (current_tool == int(num)) if num.isdigit() else False

            color = 10 if is_selected else 7
            tool_text = f"{num}:{name_jp}"
            pyxel.text(overlay_x + 20, overlay_y + y_offset, tool_text, color)
            y_offset += 10

        y_offset += 15
        pyxel.text(overlay_x + 15, overlay_y + y_offset, "その他:", 6)
        y_offset += 15
        pyxel.text(overlay_x + 20, overlay_y + y_offset, "V 表示切替", 7)
        y_offset += 10
        pyxel.text(overlay_x + 20, overlay_y + y_offset, "H ヘルプ表示/非表示", 7)
        y_offset += 10
        pyxel.text(overlay_x + 20, overlay_y + y_offset, "Q 終了", 7)
        y_offset += 15

        # 資金表示
        pyxel.text(overlay_x + 15, overlay_y + y_offset, f"資金: ¥{funds:,}", 11)

        # 終了ヒント
        if self.help_timer > 60:  # 最後の1秒間だけ表示
            pyxel.text(overlay_x + 15, overlay_y + y_offset + 10, "H キーで閉じる", 5)

    def show_toast(self, message_jp: str, message_en: str = "", duration: int = 120):
        """トースト通知を表示（簡易版）"""
        # 実装は別途
        pass

class EnhancedInputSystem:
    """改善された入力システム"""

    def __init__(self):
        self.current_tool = 1
        self.previous_tool = 1
        self.tool_confirm_mode = False
        self.help_auto_show = False

        # マウス/タッチ対応（将来的な実装のためのプレースホルダー）
        self.mouse_enabled = False
        self.mouse_x = 0
        self.mouse_y = 0

    def handle_key(self, key, key_name):
        """キー入力を処理"""
        # 移動
        if key in [pyxel.KEY_UP, pyxel.K_UP]:
            return {"action": "move_up"}
        elif key in [pyxel.KEY_DOWN, pyxel.K_DOWN]:
            return {"action": "move_down"}
        elif key in [pyxel.KEY_LEFT, pyxel.K_LEFT]:
            return {"action": "move_left"}
        elif key in [pyxel.KEY_RIGHT, pyxel.K_RIGHT]:
            return {"action": "move_right"}

        # アクション
        elif key in [pyxel.KEY_SPACE, pyxel.K_RETURN]:
            return {"action": "build"}
        elif key in [pyxel.KEY_X, pyxel.K_DELETE]:
            return {"action": "demolish"}
        elif key == pyxel.KEY_ESCAPE:
            return {"action": "cancel"}

        # ツール選択
        elif key in [pyxel.KEY_1, pyxel.KEY_KP_1]:
            return {"action": "select_tool", "tool": 1}
        elif key in [pyxel.KEY_2, pyxel.KEY_KP_2]:
            return {"action": "select_tool", "tool": 2}
        elif key in [pyxel.KEY_3, pyxel.KEY_KP_3]:
            return {"action": "select_tool", "tool": 3}
        elif key in [pyxel.KEY_4, pyxel.KEY_KP_4]:
            return {"action": "select_tool", "tool": 4}
        elif key in [pyxel.KEY_5, pyxel.KEY_KP_5]:
            return {"action": "select_tool", "tool": 5}
        elif key in [pyxel.KEY_6, pyxel.KEY_KP_6]:
            return {"action": "select_tool", "tool": 6}
        elif key in [pyxel.KEY_7, pyxel.KEY_KP_7]:
            return {"action": "select_tool", "tool": 7}
        elif key in [pyxel.KEY_8, pyxel.KEY_KP_8]:
            return {"action": "select_tool", "tool": 8}
        elif key in [pyxel.KEY_9, pyxel.KEY_KP_9]:
            return {"action": "select_tool", "tool": 9}
        elif key in [pyxel.KEY_0, pyxel.KEY_KP_0]:
            return {"action": "select_tool", "tool": 0}

        # 表示切替
        elif key == pyxel.KEY_V:
            return {"action": "cycle_view"}

        # システム
        elif key in [pyxel.KEY_S, pyxel.KEY_O]:
            return {"action": "save"}
        elif key in [pyxel.KEY_S, pyxel.KEY_I]:
            return {"action": "load"}
        elif key == pyxel.KEY_Q:
            return {"action": "quit"}

        # ヘルプ
        elif key == pyxel.KEY_H:
            return {"action": "toggle_help"}

        return None

def create_simple_tutorial():
    """初心者向けチュートリアルを作成"""
    tutorial = """# 初心者向けチュートリアル
# Beginner's Tutorial for ConcLand

## 🎮 最初の一歩 / First Steps

### 1. 画面を見る
起動すると、緑色の画面が見えます。これがあなたの都市の土地です。

### 2. 道路を作る
- 数字キーの `4` を押して「道路」ツールを選択
- ⬆️⬇️⬅️➡️ キーでカーソルを移動
- スペースキーを押して道路を配置

### 3. 住宅ゾーンを作る
- 数字キーの `1` を押して「住宅」ツールを選択
- 道路の隣にスペースキーで住宅を配置
- これで人々が住み始めます

### 4. 電力を引く
- 数字キーの `8` を押して「電線」ツールを選択
- 住宅や道路から電線を引く
- 発電所が必要です（まだ建ててない場合は資金を貯めるまで待機）

### 5. 発物を見守る
- 時間が経つと、住宅が発展します
- 人口が増えると、税収入が増えます

## 💡 上達のヒント / Advanced Tips

### 計画を立てる
- 住宅 → 商業 → 工業のバランスが重要
- 公園や警察署を設置すると周辺の地価が上がります
- 工業は汚染を発生源とするため、住宅から離して配置

### 効率よく資金を使う
- 最初は道路と住宅に集中
- 電力網を早めに整備
- 公共サービスは資金に余裕ができてから

### 情報を確認する
- V キーで表示を切り替えて確認
- 汚染が少ないほど地価が上がります
- 交通が滞っていると商業が発展しません

## 🆘 トラブルシューティング

### 資金が足りない
- 住宅の成長を待って税収入を増やす
- 道路やインフラを壊して無駄な出費を減らす

### 人口が増えない
- 商業や工業のバランスを確認
- 電力が届いているか確認
- 住宅地価が低すぎないか確認

### 火害が発生した
- 消防署を配置して火災リスクを下げる
- 警察署を配置して犯罪を減らす

---

もっと詳しいガイドが必要ですか？
"""
    return tutorial

def generate_quick_reference_card():
    """クイックリファレンスカードを作成"""
    card = """
╔══════════════════════════════════════════╗
║     🏙️ ConcLand クイック操作カード            ║
╠══════════════════════════════════════════╣
║                                            ║
║ 【移動】                                     ║
║  ⬆️ 上 / ⬇️ 下 / ⬅️ 左 / ➡️ 右             ║
║  または K / J / H / L キーでもOK                ║
║                                            ║
║ 【建設】                                     ║
║  スペースキー または Z キー                   ║
║  → カーソル位置に建物を配置                 ║
║                                            ║
║ 【削除】                                     ║
║  X キー                                      ║
║  → カーソル位置を削除                         ║
║                                            ║
║ 【ツール選択】                               ║
║  1 住宅 / 2 商業 / 3 工業                   ║
║  4 道路 / 5 鉄道 / 6 電線                     ║
║ 7 公園 / 8 公共 / 9 電力                     ║
║  0 削除                                     ║
║                                            ║
║ 【表示切替】                                 ║
║  V キー                                     ║
║  → 通常 → 汚染 → 地価 → 電力 → 交通     ║
║                                            ║
║ 【システム】                                 ║
║  H ヘルプ表示・非表示                        ║
║  Q 終了 / ESC キャンセル                       ║
║                                            ║
║ 【保存】                                     ║
║  S + O セーブ  /  S + I ロード               ║
║                                            ║
╚══════════════════════════════════════════╝
"""
    return card

# 実用例
if __name__ == "__main__":
    print("="*70)
    print("🎮 ConcLand 簡素化された操作ガイド")
    print("="*70)
    print()

    # チ�prog_to/explanatory">チュートリアル表示
    print(create_simple_tutorial())

    print()
    print("="*70)
    print("💡 ヒント: ゲーム内で H キーを押すとヘルプが表示されます")
    print("="*70)
