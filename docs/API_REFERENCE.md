# ConcLand API リファレンス

## 📖 概要
このドキュメントは、ConcLandの全システムAPIの詳細仕様を記載しています。

## 🎮 GameLauncher API

### クラス: `GameLauncher`
メインゲームランチャーと状態管理

#### メソッド

##### `__init__()`
```python
def __init__(self) -> None
```
ゲームランチャーを初期化し、Pyxelを起動

##### `_handle_quick_start()`
```python
def _handle_quick_start(self) -> None
```
ユーザー設定に基づいてクイックスタートを処理

**設定オプション:**
- `skip_title_screen`: タイトル画面をスキップ
- `auto_load_last_save`: 最後のセーブを自動ロード
- `quick_start_mode`: "continue" | "new" | "menu"

## 🏙️ ConcLandGame API

### クラス: `ConcLandGame`
メインゲームエンジン

#### プロパティ
| 名前 | 型 | 説明 |
|------|-----|------|
| `grid` | `List[List[CellType]]` | マップグリッド |
| `sim_data` | `List[List[SimData]]` | シミュレーションデータ |
| `total_population` | `int` | 総人口 |
| `funds` | `int` | 資金 |
| `current_tool` | `Tool` | 現在選択中のツール |

#### メソッド

##### `update()`
```python
def update(self) -> None
```
ゲーム状態を更新（毎フレーム呼び出し）

##### `draw()`
```python
def draw(self) -> None
```
ゲーム画面を描画

##### `place_building(x, y, building_type)`
```python
def place_building(x: int, y: int, building_type: str) -> bool
```
指定位置に建物を配置

**パラメータ:**
- `x`: X座標（タイル単位）
- `y`: Y座標（タイル単位）
- `building_type`: 建物タイプ

**戻り値:** 配置成功時 `True`

##### `save_game(filename)`
```python
def save_game(filename: str = "savegame.dat") -> bool
```
ゲームをセーブ

##### `load_game(filename)`
```python
def load_game(filename: str = "savegame.dat") -> bool
```
ゲームをロード

## 🚦 TrafficSystem API

### クラス: `AdvancedTrafficSystem`
高度な交通管理システム

#### メソッド

##### `spawn_bus(route_id)`
```python
def spawn_bus(route_id: str) -> bool
```
指定路線にバスを配置

**パラメータ:**
- `route_id`: 路線ID（"route_1", "route_2"等）

**戻り値:** 配置成功時 `True`

##### `add_traffic_light(x, y)`
```python
def add_traffic_light(x: int, y: int) -> bool
```
信号機を追加

##### `find_path(start_x, start_y, end_x, end_y, grid)`
```python
def find_path(
    start_x: int, start_y: int, 
    end_x: int, end_y: int, 
    grid: List[List[CellType]]
) -> List[Tuple[int, int]]
```
A*アルゴリズムで最適経路を探索

**戻り値:** 経路座標のリスト

##### `get_traffic_status()`
```python
def get_traffic_status(self) -> Dict[str, Any]
```
交通システムの状態を取得

**戻り値:**
```python
{
    "total_buses": int,
    "active_routes": int,
    "total_passengers": int,
    "waiting_passengers": int,
    "average_congestion": float,
    "bottlenecks": int,
    "traffic_lights": int
}
```

## 💰 EconomicSystem API

### クラス: `ConcLandEconomicSystem`
経済管理システム

#### メソッド

##### `activate_policy(policy_id)`
```python
def activate_policy(policy_id: str) -> bool
```
経済政策を実行

**利用可能な政策:**
| ID | 名称 | 効果 | コスト | 期間 |
|----|------|------|--------|------|
| `industrial_boost` | 工業開発促進 | 生産+25% | ¥5,000 | 12ヶ月 |
| `tax_incentive` | 事業税優遇 | 商業成長+40% | ¥3,000 | 6ヶ月 |
| `housing_subsidy` | 住宅助成 | 住宅成長+35% | ¥4,000 | 8ヶ月 |
| `education_investment` | 教育投資 | 生産性+15% | ¥6,000 | 24ヶ月 |
| `infrastructure_program` | インフラ整備 | 建設速度+30% | ¥8,000 | 18ヶ月 |

##### `set_tax_rates(residential, commercial, industrial)`
```python
def set_tax_rates(
    residential: float, 
    commercial: float, 
    industrial: float
) -> None
```
税率を設定（0.01～0.25の範囲）

##### `get_economic_status()`
```python
def get_economic_status(self) -> Dict[str, Any]
```
経済状態を取得

**戻り値:**
```python
{
    "funds": int,
    "monthly_revenue": int,
    "monthly_expenses": int,
    "gdp": float,
    "unemployment": float,
    "inflation": float,
    "trade_balance": int,
    "productivity": float,
    "current_season": str,
    "current_era": str,
    "active_policies": int
}
```

## 🌊 DisasterSystem API

### クラス: `DisasterSystem`
災害管理システム

#### メソッド

##### `trigger_disaster(disaster_type, severity, center_x, center_y)`
```python
def trigger_disaster(
    disaster_type: DisasterType,
    severity: DisasterSeverity,
    center_x: int,
    center_y: int
) -> None
```
災害を発生させる

**災害タイプ:**
- `DisasterType.EARTHQUAKE`: 地震
- `DisasterType.FIRE`: 火災
- `DisasterType.TYPHOON`: 台風
- `DisasterType.TSUNAMI`: 津波
- `DisasterType.FLOOD`: 洪水
- `DisasterType.VOLCANIC`: 火山噴火

**重要度:**
- `DisasterSeverity.MINOR`: 軽微
- `DisasterSeverity.MODERATE`: 中程度
- `DisasterSeverity.MAJOR`: 重大
- `DisasterSeverity.CATASTROPHIC`: 壊滅的

##### `register_emergency_service(x, y, service_type)`
```python
def register_emergency_service(
    x: int, 
    y: int, 
    service_type: str
) -> None
```
緊急サービス施設を登録

**サービスタイプ:**
- `"FIRE"`: 消防署
- `"POLICE"`: 警察署
- `"HOSPITAL"`: 病院

## 📊 AdvancedUI API

### クラス: `AdvancedUI`
高度なUIシステム

#### メソッド

##### `set_panel(panel)`
```python
def set_panel(panel: UIPanel) -> None
```
表示パネルを切り替え

**パネルタイプ:**
- `UIPanel.MAIN_GAME`: メインゲーム
- `UIPanel.STATISTICS`: 統計
- `UIPanel.ECONOMY`: 経済
- `UIPanel.TRAFFIC`: 交通
- `UIPanel.DISASTERS`: 災害
- `UIPanel.POLICIES`: 政策

##### `show_notification(message, duration)`
```python
def show_notification(
    message: str, 
    duration: int = 180
) -> None
```
通知を表示

##### `update(game_data)`
```python
def update(game_data: Dict[str, Any]) -> None
```
UIデータを更新

**必要なデータ:**
```python
{
    "population": int,
    "funds": int,
    "gdp": float,
    "traffic_system": Dict,
    "disaster_system": Dict,
    "resources": Dict,
    "res_demand": int,
    "com_demand": int,
    "ind_demand": int
}
```

## 🎵 SoundSystem API (実装予定)

### クラス: `SoundManager`
サウンド管理システム

#### メソッド

##### `play_bgm(track_name)`
```python
def play_bgm(track_name: str, loop: bool = True) -> None
```
BGMを再生

##### `play_sfx(effect_name)`
```python
def play_sfx(effect_name: str, volume: float = 1.0) -> None
```
効果音を再生

##### `set_volume(bgm_volume, sfx_volume)`
```python
def set_volume(
    bgm_volume: float, 
    sfx_volume: float
) -> None
```
音量を設定（0.0～1.0）

## 🏆 AchievementSystem API (実装予定)

### クラス: `AchievementManager`
実績管理システム

#### メソッド

##### `unlock_achievement(achievement_id)`
```python
def unlock_achievement(achievement_id: str) -> bool
```
実績を解除

##### `get_achievement_progress()`
```python
def get_achievement_progress(self) -> Dict[str, Any]
```
実績進捗を取得

## 📝 SaveData構造

### セーブデータフォーマット
```python
{
    "version": "1.0.0",
    "metadata": {
        "city_name": str,
        "save_date": str,  # ISO format
        "play_time": int,  # seconds
        "population": int,
        "funds": int,
        "screenshot": bytes  # Optional PNG data
    },
    "game_state": {
        "grid": List[List[int]],  # CellType values
        "sim_data": List[List[Dict]],  # SimData serialized
        "camera_x": int,
        "camera_y": int,
        "year": int,
        "month": int,
        "day": int,
        "total_population": int,
        "total_employment": int,
        "funds": int
    },
    "systems": {
        "traffic": {
            "buses": List[Dict],
            "traffic_lights": List[Dict],
            "bus_stops": List[Dict]
        },
        "economic": {
            "resources": Dict[str, float],
            "prices": Dict[str, float],
            "active_policies": List[str],
            "tax_rates": Dict[str, float]
        },
        "disaster": {
            "active_disasters": List[Dict],
            "emergency_services": List[Dict],
            "total_damage": int
        }
    },
    "statistics": {
        "total_buildings": int,
        "max_population": int,
        "total_revenue": int,
        "disasters_survived": int,
        "play_time": int
    }
}
```

## 🎮 入力処理

### キーボードマッピング
| キー | 通常モード | メニューモード |
|------|------------|----------------|
| `Arrow Keys` | カーソル移動 | メニュー選択 |
| `Enter/Space` | 建物配置 | 決定 |
| `Escape` | メニュー表示 | 戻る |
| `1-9` | ツール選択 | - |
| `0` | ブルドーザー | - |
| `S` | 統計画面 | - |
| `E` | 経済画面 | - |
| `T` | 交通画面 | - |
| `D` | 災害画面 | - |
| `P` | 政策画面 | - |
| `O` | セーブ | - |
| `I` | ロード | - |
| `V` | 表示モード切替 | - |
| `Q` | 終了 | - |

## 🔄 イベントシステム

### イベントタイプ
```python
class EventType(Enum):
    BUILDING_PLACED = "building_placed"
    BUILDING_REMOVED = "building_removed"
    DISASTER_STARTED = "disaster_started"
    DISASTER_ENDED = "disaster_ended"
    POLICY_ACTIVATED = "policy_activated"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    MILESTONE_REACHED = "milestone_reached"
```

### イベントリスナー登録
```python
def register_event_listener(
    event_type: EventType, 
    callback: Callable
) -> None:
    """イベントリスナーを登録"""
    pass

def emit_event(
    event_type: EventType, 
    data: Dict[str, Any]
) -> None:
    """イベントを発火"""
    pass
```

## 🔧 設定API

### UserSettings
```python
class UserSettings:
    def get(key: str, default: Any = None) -> Any:
        """設定値を取得"""
        
    def set(key: str, value: Any) -> None:
        """設定値を保存"""
        
    def reset_to_defaults() -> None:
        """デフォルト設定に戻す"""
```

### 設定項目
| キー | 型 | デフォルト | 説明 |
|------|-----|------------|------|
| `auto_load_last_save` | bool | False | 最後のセーブを自動ロード |
| `skip_title_screen` | bool | False | タイトル画面をスキップ |
| `quick_start_mode` | str | "continue" | クイックスタートモード |
| `language` | str | "japanese" | 言語設定 |
| `difficulty` | str | "normal" | 難易度 |
| `auto_save` | bool | True | オートセーブ有効 |
| `auto_save_interval` | int | 300 | オートセーブ間隔（秒） |
| `show_hints` | bool | True | ヒント表示 |
| `fullscreen` | bool | False | フルスクリーン |
| `music_volume` | int | 70 | BGM音量（0-100） |
| `sfx_volume` | int | 80 | SE音量（0-100） |

## エラーコード

| コード | 説明 | 対処法 |
|--------|------|--------|
| `E001` | セーブファイルが見つからない | ファイルパスを確認 |
| `E002` | セーブデータが破損 | バックアップから復元 |
| `E003` | メモリ不足 | 他のアプリを終了 |
| `E004` | Pyxel初期化失敗 | グラフィックドライバ更新 |
| `E005` | リソースファイル不足 | ゲーム再インストール |

---

最終更新: 2025-08-19
バージョン: 1.0.0-alpha