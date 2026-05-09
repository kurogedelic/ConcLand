# ConcLand ビジュアルシステムガイド 🎨

## 概要
ConcLandに実装された高度なビジュアルシステムは、プロフェッショナルなUIとデータ可視化を提供します。

## 🎨 実装されたシステム

### 1. カラーパレットシステム (`visual_system.py`)

#### 利用可能なテーマ
- **Classic** - オリジナルSimCityカラー
- **Modern** - 現代的なフラットデザイン
- **Dark** - ダークモード
- **Pastel** - パステルカラー
- **Cyberpunk** - ネオンカラー
- **Retro** - 8ビットノスタルジー
- **Vibrant** - 高コントラスト
- **Nature** - アースカラー
- **Autumn** - 秋の色彩
- **Monochrome** - グレースケール

#### 使用方法
```python
from visual_system import VisualSystem, ColorTheme

# システム初期化
visual_system = VisualSystem()

# テーマ変更
visual_system.set_theme(ColorTheme.DARK)

# 色の取得
bg_color = visual_system.palette_manager.get_color('ui_bg')
accent = visual_system.palette_manager.get_color('ui_accent')
```

### 2. 高度なウィンドウシステム (`advanced_window_system.py`)

#### 機能
- **タブ付きウィンドウ** - 複数のビューを切り替え
- **ドッキング** - ウィンドウを画面端に固定
- **リサイズ可能** - ドラッグでサイズ変更
- **最小化/最大化** - ウィンドウ状態管理
- **レイアウトプリセット** - 事前定義されたレイアウト

#### ウィンドウ作成例
```python
from advanced_window_system import WindowSystem, DockPosition

# システム初期化
window_system = WindowSystem(800, 600)

# ウィンドウ作成
main_window = window_system.create_window(
    "main", 100, 100, 400, 300, "メインウィンドウ",
    draggable=True,
    resizable=True,
    has_tabs=True
)

# タブ追加
main_window.add_tab("stats", "統計", draw_stats_content)
main_window.add_tab("settings", "設定", draw_settings_content)

# ドッキング
sidebar = window_system.create_window("sidebar", 0, 0, 200, 600, "サイドバー")
sidebar.dock(DockPosition.LEFT)
```

#### レイアウトプリセット
- **default** - 標準レイアウト
- **development** - 開発用（エディタ、コンソール、インスペクター）
- **analysis** - 分析用（チャート、データパネル）

### 3. データビジュアライゼーション (`data_visualization.py`)

#### 利用可能なチャート

##### 基本チャート
- **LineChart** - 折れ線グラフ
- **BarChart** - 棒グラフ
- **PieChart** - 円グラフ
- **RadarChart** - レーダーチャート
- **HeatMap** - ヒートマップ

##### リアルタイムチャート
- **RealTimeChart** - スクロール型リアルタイム表示
- 最大100ポイントのデータバッファ
- 自動スケーリング
- 複数系列対応

#### チャート作成例
```python
from data_visualization import LineChart, ChartConfig, DataSeries

# 設定
config = ChartConfig(
    title="人口推移",
    x_label="月",
    y_label="人口",
    show_grid=True,
    show_legend=True,
    animation=True
)

# チャート作成
chart = LineChart(10, 10, 300, 200, config)

# データ追加
population_data = DataSeries(
    "人口",
    [1000, 1500, 2000, 2800, 3500, 4200],
    color=12  # Light green
)
chart.add_series(population_data)

# 描画
chart.draw()
```

#### ダッシュボード
```python
from data_visualization import Dashboard

# ダッシュボード作成（4分割レイアウト）
dashboard = Dashboard(0, 0, 800, 600)

# 各チャートにデータ追加
dashboard.charts["population"].add_series(pop_series)
dashboard.charts["zones"].add_series(zone_series)
dashboard.charts["budget"].add_series(budget_series)

# リアルタイムデータ
dashboard.charts["realtime"].add_series("Traffic", color=10)
dashboard.charts["realtime"].add_point("Traffic", current_traffic)
```

## 🎮 ゲーム統合方法

### 1. メインゲームへの統合
```python
# concland_mini.py に追加

from visual_system import VisualSystem
from advanced_window_system import WindowSystem
from data_visualization import Dashboard

class ConcLandGame:
    def __init__(self):
        # ... 既存の初期化 ...
        
        # ビジュアルシステム初期化
        self.visual_system = VisualSystem()
        self.window_system = WindowSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dashboard = Dashboard(500, 10, 290, 280)
        
        # ウィンドウ作成
        self._create_ui_windows()
    
    def _create_ui_windows(self):
        """UIウィンドウの作成"""
        # 統計ウィンドウ
        stats_window = self.window_system.create_window(
            "stats", 10, 10, 200, 150, "都市統計"
        )
        
        # グラフウィンドウ
        graph_window = self.window_system.create_window(
            "graphs", 220, 10, 250, 150, "グラフ"
        )
    
    def update(self):
        # ... 既存の更新処理 ...
        
        # ビジュアルシステム更新
        self.visual_system.update()
        self.dashboard.update()
        
        # リアルタイムデータ更新
        if pyxel.frame_count % 30 == 0:
            self.dashboard.charts["realtime"].add_point(
                "Population", self.total_population
            )
    
    def draw(self):
        # ... 既存の描画処理 ...
        
        # ビジュアルシステム描画
        self.visual_system.draw()
        self.window_system.draw()
        self.dashboard.draw()
```

### 2. テーマ切り替え
```python
def handle_input(self):
    # テーマ切り替え（F1-F10キー）
    if pyxel.btnp(pyxel.KEY_F1):
        self.visual_system.set_theme(ColorTheme.CLASSIC)
    elif pyxel.btnp(pyxel.KEY_F2):
        self.visual_system.set_theme(ColorTheme.MODERN)
    elif pyxel.btnp(pyxel.KEY_F3):
        self.visual_system.set_theme(ColorTheme.DARK)
```

## 📊 ビジュアライゼーション例

### 都市統計ダッシュボード
```python
def create_city_dashboard(self):
    """都市統計ダッシュボード作成"""
    
    # 人口グラフ
    pop_chart = self.dashboard.charts["population"]
    pop_chart.add_series(DataSeries(
        "住宅", self.residential_pop_history, 10
    ))
    pop_chart.add_series(DataSeries(
        "商業", self.commercial_pop_history, 12
    ))
    
    # ゾーン分布
    zone_chart = self.dashboard.charts["zones"]
    zone_data = [
        self.residential_count,
        self.commercial_count,
        self.industrial_count
    ]
    zone_chart.add_series(DataSeries("ゾーン", zone_data, 11))
    
    # 予算円グラフ
    budget_chart = self.dashboard.charts["budget"]
    budget_data = [
        self.infrastructure_cost,
        self.service_cost,
        self.maintenance_cost
    ]
    budget_chart.add_series(DataSeries("予算", budget_data, 8))
```

## 🎯 パフォーマンス最適化

### メモリ使用量
- ウィンドウ: ~50KB/ウィンドウ
- チャート: ~100KB/チャート
- リアルタイムデータ: ~10KB/100ポイント

### 描画最適化
- 非表示ウィンドウはスキップ
- アニメーション完了後は静的描画
- ビューポート外のオブジェクトは描画しない

## 🔧 カスタマイズ

### カスタムテーマ作成
```python
# カスタムパレット定義
custom_palette = ColorPalette(
    name="MyTheme",
    primary=[7, 14, 10, 11],
    secondary=[8, 2, 4, 6],
    terrain=[3, 11, 10, 5, 13],
    buildings=[7, 12, 5, 8, 2],
    ui_bg=1,
    ui_fg=15,
    ui_accent=14,
    grid=5,
    selection=10,
    danger=8,
    success=11,
    warning=9,
    info=12
)

# 適用
visual_system.palette_manager.palettes[ColorTheme.CUSTOM] = custom_palette
visual_system.set_theme(ColorTheme.CUSTOM)
```

### カスタムチャート
```python
class CustomChart(Chart):
    def _draw_data(self):
        """カスタム描画ロジック"""
        # 独自の可視化実装
        pass
```

## 🐛 トラブルシューティング

### Q: ウィンドウが表示されない
A: `visible`プロパティと`z_order`を確認

### Q: チャートが更新されない
A: `update()`メソッドが呼ばれているか確認

### Q: テーマが適用されない
A: `set_theme()`後に再描画が必要

## 📈 今後の拡張予定

- **グラフエクスポート** - PNG/JSON形式で保存
- **インタラクティブチャート** - マウスホバーで詳細表示
- **アニメーション拡張** - イージング関数追加
- **3Dビジュアライゼーション** - 等角投影図
- **カスタムウィジェット** - スライダー、プログレスバーなど

---

**作成日**: 2025-08-21
**バージョン**: 1.0.0