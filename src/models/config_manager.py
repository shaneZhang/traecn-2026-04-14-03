import json
import os
from typing import Any, Dict, Optional


class ConfigManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = 'config.json'):
        if ConfigManager._initialized:
            return

        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_defaults()
        self._load_config()
        ConfigManager._initialized = True

    def _load_defaults(self):
        self.config = {
            'app': {
                'title': '园区白领薪资数据分析工具',
                'version': '2.0.0',
                'window_size': '1400x800',
                'theme': 'clam'
            },
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
                'age_bins': [0, 25, 30, 35, 40, 50, 60, 100],
                'age_labels': ['25岁以下', '25-30岁', '30-35岁', '35-40岁',
                               '40-50岁', '50-60岁', '60岁以上'],
                'salary_bins': [0, 5000, 10000, 15000, 20000, 30000, 50000, 100000],
                'salary_labels': ['5千以下', '5千-1万', '1万-1.5万', '1.5万-2万',
                                  '2万-3万', '3万-5万', '5万以上'],
                'experience_bins': [0, 1, 3, 5, 10, 15, 20, 100],
                'experience_labels': ['1年以下', '1-3年', '3-5年', '5-10年',
                                      '10-15年', '15-20年', '20年以上']
            },
            'visualization': {
                'figure_size': [10, 6],
                'dpi': 100,
                'colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12',
                           '#9b59b6', '#1abc9c', '#e67e22', '#34495e'],
                'font_sizes': {
                    'title': 14,
                    'label': 12,
                    'tick': 10,
                    'legend': 10
                }
            },
            'processing': {
                'outlier_threshold': 1.5,
                'outlier_method': 'iqr'
            }
        }

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_config(self.config, loaded_config)
            except Exception as e:
                from .logger import Logger
                Logger().warning(f"加载配置文件失败: {str(e)}，使用默认配置")

    def _merge_config(self, base: Dict, override: Dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def save_config(self) -> bool:
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            from .logger import Logger
            Logger().error(f"保存配置文件失败: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        return self.config.copy()
