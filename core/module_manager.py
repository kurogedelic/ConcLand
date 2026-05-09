"""
モジュールマネージャー
Module Manager

ゲームシステムのモジュールを動的に管理・ロードするシステム。
プラグイン形式でシステムを追加・削除可能。
"""

import importlib
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class ModuleInfo:
    """
    モジュール情報
    各モジュールのメタデータを保持
    """
    name: str                # モジュール名
    version: str            # バージョン
    description: str        # 説明
    dependencies: List[str] # 依存モジュール
    enabled: bool          # 有効/無効
    loaded: bool = False   # ロード済みフラグ
    instance: Any = None   # モジュールインスタンス
    config: Dict = None    # モジュール設定


class ModuleManager:
    """
    モジュールマネージャークラス
    ゲームシステムのモジュールを管理
    """
    
    def __init__(self, game_instance=None):
        """
        初期化
        
        Args:
            game_instance: メインゲームインスタンス
        """
        self.game = game_instance
        self.modules: Dict[str, ModuleInfo] = {}
        self.load_order: List[str] = []
        self.module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # モジュール設定をロード
        self._load_module_config()
    
    def _load_module_config(self):
        """
        モジュール設定ファイルをロード
        """
        config_file = os.path.join(self.module_path, 'config', 'modules.json')
        
        # デフォルト設定
        default_config = {
            "modules": [
                {
                    "name": "traffic_system",
                    "version": "1.0.0",
                    "description": "高度な交通管理システム",
                    "dependencies": [],
                    "enabled": True,
                    "class_name": "AdvancedTrafficSystem",
                    "config": {}
                },
                {
                    "name": "economic_system",
                    "version": "1.0.0",
                    "description": "経済管理システム",
                    "dependencies": [],
                    "enabled": True,
                    "class_name": "ConcLandEconomicSystem",
                    "config": {}
                },
                {
                    "name": "disaster_system",
                    "version": "1.0.0",
                    "description": "災害シミュレーションシステム",
                    "dependencies": [],
                    "enabled": True,
                    "class_name": "DisasterSystem",
                    "config": {}
                },
                {
                    "name": "sound_effects_system",
                    "version": "1.0.0",
                    "description": "サウンドエフェクトシステム",
                    "dependencies": [],
                    "enabled": True,
                    "class_name": "SoundEffectsSystem",
                    "config": {}
                },
                {
                    "name": "visual_system",
                    "version": "1.0.0",
                    "description": "ビジュアル強化システム",
                    "dependencies": [],
                    "enabled": True,
                    "class_name": "VisualSystem",
                    "config": {}
                },
                {
                    "name": "advanced_window_system",
                    "version": "1.0.0",
                    "description": "高度なウィンドウシステム",
                    "dependencies": ["visual_system"],
                    "enabled": True,
                    "class_name": "WindowSystem",
                    "config": {}
                },
                {
                    "name": "data_visualization",
                    "version": "1.0.0",
                    "description": "データビジュアライゼーション",
                    "dependencies": ["visual_system"],
                    "enabled": True,
                    "class_name": "Dashboard",
                    "config": {}
                },
                {
                    "name": "tutorial_system",
                    "version": "1.0.0",
                    "description": "チュートリアルシステム",
                    "dependencies": [],
                    "enabled": False,  # デフォルトで無効
                    "class_name": "TutorialManager",
                    "config": {}
                },
                {
                    "name": "difficulty_system",
                    "version": "1.0.0",
                    "description": "難易度管理システム",
                    "dependencies": [],
                    "enabled": True,
                    "class_name": "DifficultyManager",
                    "config": {}
                },
                {
                    "name": "goals_challenges_system",
                    "version": "1.0.0",
                    "description": "目標とチャレンジシステム",
                    "dependencies": [],
                    "enabled": True,
                    "class_name": "GoalsManager",
                    "config": {}
                }
            ]
        }
        
        # 設定ファイルが存在する場合はロード
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"⚠️ モジュール設定のロード失敗: {e}")
                config = default_config
        else:
            # 設定ファイルが存在しない場合は作成
            config = default_config
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        
        # モジュール情報を登録
        for module_config in config.get('modules', []):
            info = ModuleInfo(
                name=module_config['name'],
                version=module_config['version'],
                description=module_config['description'],
                dependencies=module_config['dependencies'],
                enabled=module_config['enabled'],
                config=module_config.get('config', {})
            )
            # クラス名を設定に保存
            info.config['class_name'] = module_config.get('class_name', '')
            self.modules[info.name] = info
    
    def load_module(self, module_name: str) -> bool:
        """
        モジュールをロード
        
        Args:
            module_name: モジュール名
            
        Returns:
            成功時True
        """
        if module_name not in self.modules:
            print(f"❌ モジュール '{module_name}' が見つかりません")
            return False
        
        module_info = self.modules[module_name]
        
        if not module_info.enabled:
            print(f"⚠️ モジュール '{module_name}' は無効です")
            return False
        
        if module_info.loaded:
            print(f"ℹ️ モジュール '{module_name}' は既にロード済みです")
            return True
        
        # 依存関係をチェック・ロード
        for dep in module_info.dependencies:
            if dep not in self.modules or not self.modules[dep].loaded:
                print(f"📦 依存モジュール '{dep}' をロード中...")
                if not self.load_module(dep):
                    print(f"❌ 依存モジュール '{dep}' のロード失敗")
                    return False
        
        try:
            # モジュールをインポート
            print(f"📦 モジュール '{module_name}' をロード中...")
            
            # パスを追加
            if self.module_path not in sys.path:
                sys.path.insert(0, self.module_path)
            
            # モジュールをインポート
            imported_module = importlib.import_module(module_name)
            
            # クラスを取得してインスタンス化
            class_name = module_info.config.get('class_name', '')
            if class_name and hasattr(imported_module, class_name):
                module_class = getattr(imported_module, class_name)
                
                # インスタンス化（引数を判定）
                try:
                    # ゲームインスタンスを渡してみる
                    if self.game:
                        module_info.instance = module_class(self.game)
                    else:
                        module_info.instance = module_class()
                except TypeError:
                    # 引数なしで試す
                    module_info.instance = module_class()
            else:
                # モジュール自体を保存
                module_info.instance = imported_module
            
            module_info.loaded = True
            self.load_order.append(module_name)
            
            print(f"✅ モジュール '{module_name}' をロードしました")
            return True
            
        except ImportError as e:
            print(f"❌ モジュール '{module_name}' のインポート失敗: {e}")
            return False
        except Exception as e:
            print(f"❌ モジュール '{module_name}' のロード中にエラー: {e}")
            return False
    
    def unload_module(self, module_name: str) -> bool:
        """
        モジュールをアンロード
        
        Args:
            module_name: モジュール名
            
        Returns:
            成功時True
        """
        if module_name not in self.modules:
            return False
        
        module_info = self.modules[module_name]
        
        if not module_info.loaded:
            return True
        
        # 依存しているモジュールをチェック
        for name, info in self.modules.items():
            if name != module_name and module_name in info.dependencies and info.loaded:
                print(f"⚠️ モジュール '{name}' が '{module_name}' に依存しています")
                return False
        
        # クリーンアップ処理を呼び出す
        if module_info.instance and hasattr(module_info.instance, 'cleanup'):
            try:
                module_info.instance.cleanup()
            except Exception as e:
                print(f"⚠️ クリーンアップ中にエラー: {e}")
        
        # アンロード
        module_info.instance = None
        module_info.loaded = False
        if module_name in self.load_order:
            self.load_order.remove(module_name)
        
        print(f"✅ モジュール '{module_name}' をアンロードしました")
        return True
    
    def load_all_enabled(self):
        """
        有効なすべてのモジュールをロード
        """
        print("\n📦 有効なモジュールをロード中...")
        loaded_count = 0
        
        for module_name, module_info in self.modules.items():
            if module_info.enabled and not module_info.loaded:
                if self.load_module(module_name):
                    loaded_count += 1
        
        print(f"\n✅ {loaded_count} 個のモジュールをロードしました")
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """
        モジュールインスタンスを取得
        
        Args:
            module_name: モジュール名
            
        Returns:
            モジュールインスタンス、ない場合None
        """
        if module_name in self.modules and self.modules[module_name].loaded:
            return self.modules[module_name].instance
        return None
    
    def update_all(self, *args, **kwargs):
        """
        すべてのロード済みモジュールのupdate()を呼び出す
        
        Args:
            *args, **kwargs: update()に渡す引数
        """
        for module_name in self.load_order:
            module_info = self.modules[module_name]
            if module_info.loaded and module_info.instance:
                if hasattr(module_info.instance, 'update'):
                    try:
                        module_info.instance.update(*args, **kwargs)
                    except Exception as e:
                        print(f"⚠️ モジュール '{module_name}' の更新中にエラー: {e}")
    
    def draw_all(self, *args, **kwargs):
        """
        すべてのロード済みモジュールのdraw()を呼び出す
        
        Args:
            *args, **kwargs: draw()に渡す引数
        """
        for module_name in self.load_order:
            module_info = self.modules[module_name]
            if module_info.loaded and module_info.instance:
                if hasattr(module_info.instance, 'draw'):
                    try:
                        module_info.instance.draw(*args, **kwargs)
                    except Exception as e:
                        print(f"⚠️ モジュール '{module_name}' の描画中にエラー: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        モジュールマネージャーのステータスを取得
        
        Returns:
            ステータス情報
        """
        return {
            'total_modules': len(self.modules),
            'loaded_modules': len([m for m in self.modules.values() if m.loaded]),
            'enabled_modules': len([m for m in self.modules.values() if m.enabled]),
            'load_order': self.load_order,
            'modules': {
                name: {
                    'version': info.version,
                    'enabled': info.enabled,
                    'loaded': info.loaded,
                    'dependencies': info.dependencies
                }
                for name, info in self.modules.items()
            }
        }
    
    def save_config(self, filename: str = None):
        """
        モジュール設定を保存
        
        Args:
            filename: 保存先ファイル名
        """
        if filename is None:
            filename = os.path.join(self.module_path, 'config', 'modules.json')
        
        config = {
            'modules': [
                {
                    'name': name,
                    'version': info.version,
                    'description': info.description,
                    'dependencies': info.dependencies,
                    'enabled': info.enabled,
                    'class_name': info.config.get('class_name', ''),
                    'config': info.config
                }
                for name, info in self.modules.items()
            ]
        }
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ モジュール設定を保存しました: {filename}")


# テスト関数
def test_module_manager():
    """
    モジュールマネージャーのテスト
    """
    print("=== モジュールマネージャーテスト ===\n")
    
    manager = ModuleManager()
    
    # ステータス表示
    status = manager.get_status()
    print(f"総モジュール数: {status['total_modules']}")
    print(f"有効モジュール: {status['enabled_modules']}")
    print(f"ロード済み: {status['loaded_modules']}")
    
    # すべての有効モジュールをロード
    manager.load_all_enabled()
    
    # ステータス再表示
    status = manager.get_status()
    print(f"\nロード後:")
    print(f"ロード済み: {status['loaded_modules']}")
    print(f"ロード順序: {status['load_order']}")
    
    # 特定モジュールの取得
    traffic = manager.get_module('traffic_system')
    if traffic:
        print(f"\n✅ 交通システムモジュール取得成功")
    
    # 設定保存
    manager.save_config()
    
    print("\n✅ テスト完了")


if __name__ == "__main__":
    test_module_manager()