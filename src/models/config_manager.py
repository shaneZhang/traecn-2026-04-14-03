import os
import json
from typing import Any, Dict, Optional


class ConfigManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if ConfigManager._initialized:
            return
        ConfigManager._initialized = True
        
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[str] = None
        self._load_default_config()
    
    def _load_default_config(self) -> None:
        self._config = {
            'app': {
                'name': '园区白领薪资数据分析工具',
                'version': '2.0.0',
                'window': {
                    'width': 1400,
                    'height': 800,
                    'title': '园区白领薪资数据分析工具'
                }
            },
            'data': {
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
                'salary_fields': ['pre_tax_salary', 'post_tax_salary', 'base_salary', 'total_salary'],
                'numeric_fields': ['age', 'work_years', 'base_salary', 'performance_bonus', 
                                  'allowance', 'pre_tax_salary', 'post_tax_salary', 'join_year']
            },
            'processing': {
                'age_groups': {
                    'bins': [0, 25, 30, 35, 40, 50, 60, 100],
                    'labels': ['25岁以下', '25-30岁', '30-35岁', '35-40岁', 
                              '40-50岁', '50-60岁', '60岁以上']
                },
                'salary_groups': {
                    'bins': [0, 5000, 10000, 15000, 20000, 30000, 50000, float('inf')],
                    'labels': ['5千以下', '5千-1万', '1万-1.5万', '1.5万-2万', 
                              '2万-3万', '3万-5万', '5万以上']
                },
                'experience_groups': {
                    'bins': [0, 1, 3, 5, 10, 15, 20, float('inf')],
                    'labels': ['1年以下', '1-3年', '3-5年', '5-10年', 
                              '10-15年', '15-20年', '20年以上']
                },
                'outlier_threshold': 1.5
            },
            'visualization': {
                'figure_size': [10, 6],
                'dpi': 100,
                'title_fontsize': 14,
                'label_fontsize': 12,
                'tick_fontsize': 10,
                'legend_fontsize': 10,
                'colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', 
                          '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'salary_analysis.log',
                'console': True
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
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def load_config(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            self._deep_merge(self._config, loaded_config)
            self._config_path = file_path
            return True
        except Exception:
            return False
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        path = file_path or self._config_path
        if not path:
            return False
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get_field_mapping(self) -> Dict[str, str]:
        return self.get('data.field_mapping', {})
    
    def get_age_groups(self) -> Dict:
        return self.get('processing.age_groups', {})
    
    def get_salary_groups(self) -> Dict:
        return self.get('processing.salary_groups', {})
    
    def get_experience_groups(self) -> Dict:
        return self.get('processing.experience_groups', {})
    
    def get_chart_colors(self) -> list:
        return self.get('visualization.colors', [])
    
    def get_figure_config(self) -> Dict:
        return {
            'figsize': tuple(self.get('visualization.figure_size', [10, 6])),
            'dpi': self.get('visualization.dpi', 100),
            'title_fontsize': self.get('visualization.title_fontsize', 14),
            'label_fontsize': self.get('visualization.label_fontsize', 12),
            'tick_fontsize': self.get('visualization.tick_fontsize', 10),
            'legend_fontsize': self.get('visualization.legend_fontsize', 10)
        }
    
    def get_window_config(self) -> Dict:
        return self.get('app.window', {})
    
    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()
