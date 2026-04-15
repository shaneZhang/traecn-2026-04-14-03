import json
import os
from typing import Any, Dict, Optional, List
from pathlib import Path


class ConfigManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[str] = None):
        if ConfigManager._initialized:
            return

        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._default_config = self._get_default_config()

        if config_path:
            self._config_path = Path(config_path)
            self.load_config()
        else:
            self._config = self._default_config.copy()

        ConfigManager._initialized = True

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'field_mapping': {
                '姓名': 'name',
                '性别': 'gender',
                '年龄': 'age',
                '学历': 'education',
                '工作年限': 'work_years',
                '所在行业': 'industry',
                '岗位类型': 'position_type',
                '职级': 'level',
                '基本工资': 'base_salary',
                '绩效奖金': 'performance_bonus',
                '补贴总和': 'allowance',
                '税前薪资': 'pre_tax_salary',
                '税后薪资': 'post_tax_salary',
                '所属企业规模': 'company_size',
                '入职年份': 'join_year'
            },
            'grouping': {
                'age': {
                    'bins': [0, 25, 30, 35, 40, 50, 60, 100],
                    'labels': ['25岁以下', '25-30岁', '30-35岁', '35-40岁', 
                              '40-50岁', '50-60岁', '60岁以上']
                },
                'salary': {
                    'bins': [0, 5000, 10000, 15000, 20000, 30000, 50000, float('inf')],
                    'labels': ['5千以下', '5千-1万', '1万-1.5万', '1.5万-2万', 
                              '2万-3万', '3万-5万', '5万以上']
                },
                'experience': {
                    'bins': [0, 1, 3, 5, 10, 15, 20, float('inf')],
                    'labels': ['1年以下', '1-3年', '3-5年', '5-10年', 
                              '10-15年', '15-20年', '20年以上']
                }
            },
            'analysis': {
                'default_salary_column': 'pre_tax_salary',
                'outlier_method': 'iqr',
                'outlier_threshold': 1.5,
                'default_chart_type': 'bar'
            },
            'ui': {
                'window_title': '园区白领薪资数据分析工具',
                'window_size': '1400x800',
                'theme': 'default',
                'language': 'zh_CN'
            },
            'export': {
                'default_format': 'excel',
                'chart_dpi': 300,
                'chart_format': 'png'
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def load_config(self, config_path: Optional[str] = None):
        if config_path:
            self._config_path = Path(config_path)
        
        if self._config_path and self._config_path.exists():
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._config = self._merge_config(self._default_config.copy(), loaded_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self._config = self._default_config.copy()
        else:
            self._config = self._default_config.copy()

    def save_config(self, config_path: Optional[str] = None):
        if config_path:
            save_path = Path(config_path)
        elif self._config_path:
            save_path = self._config_path
        else:
            save_path = Path(__file__).parent.parent.parent / 'config' / 'config.json'
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def _merge_config(self, default: Dict, override: Dict) -> Dict:
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get_field_mapping(self) -> Dict[str, str]:
        return self.get('field_mapping', {}).copy()

    def get_grouping_config(self, group_type: str) -> Dict[str, Any]:
        return self.get(f'grouping.{group_type}', {})

    def get_all_config(self) -> Dict[str, Any]:
        return self._config.copy()

    def reset_to_default(self):
        self._config = self._default_config.copy()

    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> 'ConfigManager':
        if cls._instance is None:
            return cls(config_path)
        return cls._instance


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    return ConfigManager.get_instance(config_path)
