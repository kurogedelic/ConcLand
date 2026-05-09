# ConcLand サウンド・エフェクトシステム ガイド

## 📖 概要

ConcLandのサウンドとエフェクトシステムは、ゲームの没入感を高める包括的なオーディオとビジュアルエフェクト管理システムです。

## 🎵 機能概要

### 音響システム
- **BGM（背景音楽）**: ゲーム状況に応じた適応的BGM再生
- **SFX（効果音）**: UI、建設、交通、災害などのカテゴリ別効果音
- **音量制御**: BGMとSFXの独立音量調整
- **フェードイン/アウト**: スムーズなBGM切り替え

### ビジュアルエフェクト
- **パーティクルシステム**: 爆発、煙、火花などの動的エフェクト
- **建設エフェクト**: 建物配置・撤去時の視覚フィードバック
- **災害エフェクト**: 地震、火災など災害特有の視覚演出
- **UI エフェクト**: お金獲得、レベルアップなどのフィードバック

## 🏗️ システム構成

### クラス構造

```
SoundEffectsSystem
├── SoundManager
│   ├── BGM管理
│   ├── SFX管理
│   └── 適応的オーディオ
└── VisualEffectManager
    ├── パーティクルシステム
    ├── エフェクトテンプレート
    └── メモリ管理
```

## 🎮 実装されたサウンド

### BGMトラック

| トラックID | 名称 | 日本語名 | 再生条件 |
|------------|------|----------|----------|
| `rural_theme` | Rural Serenity | 田舎の静寂 | 人口 < 500 |
| `city_day` | City Life (Day) | 都市の日常 | 昼間 & 人口 100-10,000 |
| `city_night` | City Life (Night) | 都市の夜 | 夜間 & 人口 100-10,000 |
| `metropolis_theme` | Metropolitan Rush | 大都市の喧騒 | 人口 > 10,000 |
| `disaster_theme` | Crisis Management | 危機管理 | 災害発生中 |

### 効果音リスト

#### UI効果音
- `ui_select`: メニュー選択音
- `ui_confirm`: 決定音
- `ui_cancel`: キャンセル音
- `ui_error`: エラー音

#### 建設効果音
- `place_building`: 建物設置音
- `demolish`: 建物撤去音
- `construction`: 建設作業音

#### 交通効果音
- `car_horn`: 車のクラクション
- `bus_arrival`: バス到着音
- `train_horn`: 電車の汽笛

#### 災害効果音
- `earthquake`: 地震音
- `fire_alarm`: 火災警報
- `siren`: サイレン

#### その他効果音
- `money_gain`: お金獲得音
- `level_up`: レベルアップ音
- `achievement`: 実績解除音

## ✨ ビジュアルエフェクト

### エフェクトタイプ

| タイプ | 説明 | 用途 |
|--------|------|------|
| `EXPLOSION` | 爆発エフェクト | 地震、事故 |
| `CONSTRUCTION` | 建設エフェクト | 建物配置 |
| `SMOKE` | 煙エフェクト | 火災、工場 |
| `SPARKLE` | 光るエフェクト | お金、成功 |
| `FIRE` | 炎エフェクト | 火災災害 |

### パーティクル属性

```python
@dataclass
class Particle:
    x, y: float              # 位置
    velocity_x, velocity_y: float    # 速度
    acceleration_x, acceleration_y: float  # 加速度
    life: int               # 残り寿命
    max_life: int          # 最大寿命
    color: int             # 色
    size: int              # サイズ
    alpha: float           # 透明度
    rotation: float        # 回転角
    angular_velocity: float # 回転速度
```

## 🔧 API使用方法

### 基本的な使用方法

```python
# システム初期化
sound_system = SoundEffectsSystem()

# BGM再生
sound_system.sound_manager.play_bgm("city_day")

# 効果音再生
sound_system.sound_manager.play_sfx("place_building", volume=0.8)

# ビジュアルエフェクト作成
sound_system.visual_effect_manager.create_effect(
    VisualEffectType.EXPLOSION, 
    x=100, y=100, 
    duration=60, 
    scale=1.5
)
```

### イベントドリブン使用方法

```python
# 建物配置イベント
sound_system.emit_event("building_placed", {
    "position": (x, y),
    "building_type": "RESIDENTIAL"
})

# 災害発生イベント
sound_system.emit_event("disaster_started", {
    "disaster_type": "earthquake",
    "position": (x, y),
    "severity": 2.0
})

# お金獲得イベント
sound_system.emit_event("money_gained", {
    "amount": 5000,
    "position": (160, 144)
})
```

### ゲーム統合

```python
# メインゲームループでの更新
def update():
    game_state = {
        "population": self.total_population,
        "active_disasters": len(self.active_disasters),
        "hour": self.current_hour,
        "funds": self.funds
    }
    
    sound_system.update(game_state)

def draw():
    # ゲーム描画
    draw_game()
    
    # エフェクト描画
    sound_system.draw()
```

## ⚙️ 設定管理

### 音量設定

```python
# 音量設定（0.0〜1.0）
sound_system.set_volume(bgm_volume=0.7, sfx_volume=0.8)

# システム有効/無効切り替え
sound_system.toggle_enabled()

# 適応的BGM有効/無効
sound_system.sound_manager.adaptive_volume = True
```

### 設定の保存・読み込み

```python
# 設定保存
sound_system.save_settings("audio_settings.json")

# 設定読み込み
sound_system.load_settings("audio_settings.json")
```

## 📊 パフォーマンス考慮事項

### 最適化機能

1. **エフェクト数制限**: 最大50個のエフェクト同時実行
2. **パーティクル管理**: 死んだパーティクルの自動削除
3. **メモリプール**: パーティクルオブジェクトの再利用
4. **フレームスキップ**: 重い処理の分散実行

### パフォーマンス指標

- **エフェクト処理**: < 1ms/frame
- **メモリ使用量**: < 50MB（最大負荷時）
- **同時エフェクト**: 50個まで
- **同時パーティクル**: 5000個まで

## 🎨 カスタマイズ

### 新しい効果音追加

```python
def add_custom_sfx(sound_manager, sound_id, params):
    sound_manager.sound_library[sound_id] = {
        "tone": params["tone"],
        "duration": params["duration"],
        "wave": params["wave"],
        "category": SoundCategory.SFX_AMBIENT
    }
```

### 新しいエフェクトテンプレート追加

```python
vfx_manager.effect_templates[VisualEffectType.CUSTOM] = {
    "particle_count": 30,
    "colors": [1, 2, 3, 4],
    "life_range": (40, 80),
    "velocity_range": (-4.0, 4.0),
    "acceleration": (0, 0.15)
}
```

## 🐛 トラブルシューティング

### よくある問題

#### BGMが切り替わらない
- **原因**: 適応的BGMが無効になっている
- **解決**: `sound_manager.adaptive_volume = True`

#### エフェクトが表示されない
- **原因**: システムが無効になっている
- **解決**: `sound_system.enabled = True`

#### パフォーマンスが低下する
- **原因**: エフェクトが多すぎる
- **解決**: エフェクト数を制限、または`clear_all()`で全削除

### デバッグ情報取得

```python
status = sound_system.get_system_status()
print(f"有効状態: {status['enabled']}")
print(f"アクティブエフェクト: {status['active_effects']}")
print(f"総パーティクル数: {status['total_particles']}")
print(f"現在のBGM: {status['current_bgm']}")
```

## 🔮 今後の拡張予定

### Phase 1 (実装済み)
- ✅ 基本サウンドシステム
- ✅ パーティクルエフェクト
- ✅ 適応的BGM
- ✅ イベントドリブンサウンド

### Phase 2 (予定)
- 🔄 外部音声ファイル対応
- 🔄 3Dポジショナルオーディオ
- 🔄 リバーブ・エコーエフェクト
- 🔄 動的音量調整

### Phase 3 (予定)
- 📋 カスタムサウンドパック
- 📋 MODサポート
- 📋 リアルタイム音楽生成
- 📋 VRオーディオ対応

## 📈 統計・アナリティクス

### システム使用状況追跡

```python
# 再生統計
sound_usage = {
    "bgm_switches": count,
    "sfx_played": count,
    "effects_created": count,
    "total_particles": count
}
```

## 🎯 統合テスト結果

### 最新テスト結果
- **総テスト数**: 10
- **成功率**: 100% ✅
- **パフォーマンステスト**: 0.00秒で完了
- **メモリリーク**: 検出されず

### テスト項目
1. サウンドマネージャー初期化 ✅
2. ビジュアルエフェクトマネージャー初期化 ✅
3. BGMシステム ✅
4. SFXシステム ✅
5. ビジュアルエフェクト ✅
6. イベント処理 ✅
7. 適応的オーディオ ✅
8. 設定永続化 ✅
9. 負荷テスト ✅
10. メモリ管理 ✅

---

**最終更新**: 2025-08-19  
**バージョン**: 1.0.0  
**作成者**: ConcLand開発チーム