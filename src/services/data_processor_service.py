import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Callable, Tuple
from ..models.config_manager import ConfigManager


class DataProcessingError(Exception):
    pass


class DataProcessor:
    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()
    
    def remove_duplicates(self, data: pd.DataFrame, subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
        if data is None or len(data) == 0:
            raise DataProcessingError("数据为空")
        
        before_count = len(data)
        result = data.drop_duplicates(subset=subset)
        after_count = len(result)
        
        return result, before_count - after_count
    
    def handle_missing_values(self, data: pd.DataFrame, strategy: str = 'drop',
                             columns: Optional[List[str]] = None,
                             fill_value: Any = None) -> Tuple[pd.DataFrame, Dict[str, int]]:
        if data is None or len(data) == 0:
            raise DataProcessingError("数据为空")
        
        result = data.copy()
        processed = {}
        
        if columns is None:
            columns = result.columns.tolist()
        
        if strategy == 'drop':
            null_counts = result[columns].isnull().sum()
            cols_with_null = null_counts[null_counts > 0]
            
            if len(cols_with_null) > 0:
                before_count = len(result)
                result = result.dropna(subset=columns)
                after_count = len(result)
                
                for col, count in cols_with_null.items():
                    processed[col] = count
            
            return result, processed
        
        for col in columns:
            if col not in result.columns:
                continue
            
            null_count = result[col].isnull().sum()
            
            if null_count == 0:
                continue
            
            if strategy == 'fill_mean' and pd.api.types.is_numeric_dtype(result[col]):
                result[col] = result[col].fillna(result[col].mean())
                processed[col] = null_count
            
            elif strategy == 'fill_median' and pd.api.types.is_numeric_dtype(result[col]):
                result[col] = result[col].fillna(result[col].median())
                processed[col] = null_count
            
            elif strategy == 'fill_mode':
                mode_value = result[col].mode()
                if len(mode_value) > 0:
                    result[col] = result[col].fillna(mode_value[0])
                    processed[col] = null_count
            
            elif strategy == 'fill_value':
                result[col] = result[col].fillna(fill_value)
                processed[col] = null_count
            
            elif strategy == 'fill_forward':
                result[col] = result[col].ffill()
                processed[col] = null_count
            
            elif strategy == 'fill_backward':
                result[col] = result[col].bfill()
                processed[col] = null_count
        
        return result, processed
    
    def detect_outliers(self, data: pd.DataFrame, column: str, method: str = 'iqr',
                       threshold: float = None) -> pd.Series:
        if data is None or column not in data.columns:
            raise DataProcessingError(f"列 '{column}' 不存在")
        
        if not pd.api.types.is_numeric_dtype(data[column]):
            raise DataProcessingError(f"列 '{column}' 不是数值类型")
        
        if threshold is None:
            threshold = self.config.get('processing.outlier_threshold', 1.5)
        
        if method == 'iqr':
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return (data[column] < lower_bound) | (data[column] > upper_bound)
        
        elif method == 'zscore':
            mean = data[column].mean()
            std = data[column].std()
            if std == 0:
                return pd.Series([False] * len(data), index=data.index)
            z_scores = np.abs((data[column] - mean) / std)
            return z_scores > threshold
        
        return pd.Series([False] * len(data), index=data.index)
    
    def remove_outliers(self, data: pd.DataFrame, column: str, method: str = 'iqr',
                       threshold: float = None) -> Tuple[pd.DataFrame, int]:
        if data is None:
            raise DataProcessingError("数据为空")
        
        outliers = self.detect_outliers(data, column, method, threshold)
        before_count = len(data)
        result = data[~outliers]
        
        return result, before_count - len(result)
    
    def convert_dtype(self, data: pd.DataFrame, column: str, target_type: str) -> pd.DataFrame:
        if data is None or column not in data.columns:
            raise DataProcessingError(f"列 '{column}' 不存在")
        
        result = data.copy()
        
        try:
            if target_type == 'numeric':
                result[column] = pd.to_numeric(result[column], errors='coerce')
            elif target_type == 'string':
                result[column] = result[column].astype(str)
            elif target_type == 'datetime':
                result[column] = pd.to_datetime(result[column], errors='coerce')
            elif target_type == 'category':
                result[column] = result[column].astype('category')
            return result
        except Exception as e:
            raise DataProcessingError(f"类型转换失败: {str(e)}")
    
    def create_calculated_field(self, data: pd.DataFrame, field_name: str,
                               calculation: Callable[[pd.DataFrame], pd.Series]) -> pd.DataFrame:
        if data is None:
            raise DataProcessingError("数据为空")
        
        result = data.copy()
        
        try:
            result[field_name] = calculation(result)
            return result
        except Exception as e:
            raise DataProcessingError(f"计算字段创建失败: {str(e)}")
    
    def create_age_group(self, data: pd.DataFrame, age_column: str = 'age',
                        bins: Optional[List[int]] = None,
                        labels: Optional[List[str]] = None) -> pd.DataFrame:
        if data is None or age_column not in data.columns:
            raise DataProcessingError(f"列 '{age_column}' 不存在")
        
        if bins is None or labels is None:
            age_config = self.config.get_age_groups()
            bins = age_config.get('bins', [0, 25, 30, 35, 40, 50, 60, 100])
            labels = age_config.get('labels', ['25岁以下', '25-30岁', '30-35岁', '35-40岁',
                                               '40-50岁', '50-60岁', '60岁以上'])
        
        result = data.copy()
        
        try:
            age_data = pd.to_numeric(result[age_column], errors='coerce')
            result['age_group'] = pd.cut(age_data, bins=bins, labels=labels,
                                         right=False, include_lowest=True)
            return result
        except Exception as e:
            raise DataProcessingError(f"年龄分组失败: {str(e)}")
    
    def create_salary_group(self, data: pd.DataFrame, salary_column: str = 'pre_tax_salary',
                           bins: Optional[List[int]] = None,
                           labels: Optional[List[str]] = None) -> pd.DataFrame:
        if data is None or salary_column not in data.columns:
            raise DataProcessingError(f"列 '{salary_column}' 不存在")
        
        if bins is None or labels is None:
            salary_config = self.config.get_salary_groups()
            bins = salary_config.get('bins', [0, 5000, 10000, 15000, 20000, 30000, 50000, float('inf')])
            labels = salary_config.get('labels', ['5千以下', '5千-1万', '1万-1.5万', '1.5万-2万',
                                                  '2万-3万', '3万-5万', '5万以上'])
        
        result = data.copy()
        
        try:
            salary_data = pd.to_numeric(result[salary_column], errors='coerce')
            result['salary_group'] = pd.cut(salary_data, bins=bins, labels=labels,
                                            right=False, include_lowest=True)
            return result
        except Exception as e:
            raise DataProcessingError(f"薪资分组失败: {str(e)}")
    
    def create_work_experience_group(self, data: pd.DataFrame, years_column: str = 'work_years',
                                     bins: Optional[List[int]] = None,
                                     labels: Optional[List[str]] = None) -> pd.DataFrame:
        if data is None or years_column not in data.columns:
            raise DataProcessingError(f"列 '{years_column}' 不存在")
        
        if bins is None or labels is None:
            exp_config = self.config.get_experience_groups()
            bins = exp_config.get('bins', [0, 1, 3, 5, 10, 15, 20, float('inf')])
            labels = exp_config.get('labels', ['1年以下', '1-3年', '3-5年', '5-10年',
                                               '10-15年', '15-20年', '20年以上'])
        
        result = data.copy()
        
        try:
            years_data = pd.to_numeric(result[years_column], errors='coerce')
            result['experience_group'] = pd.cut(years_data, bins=bins, labels=labels, right=False)
            return result
        except Exception as e:
            raise DataProcessingError(f"工作年限分组失败: {str(e)}")
    
    def filter_data(self, data: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
        if data is None:
            raise DataProcessingError("数据为空")
        
        result = data.copy()
        
        for column, value in conditions.items():
            if column not in result.columns:
                continue
            
            if isinstance(value, list):
                result = result[result[column].isin(value)]
            else:
                result = result[result[column] == value]
        
        return result
    
    def encode_categorical(self, data: pd.DataFrame, columns: Optional[List[str]] = None,
                          method: str = 'label') -> Tuple[pd.DataFrame, Dict[str, bool]]:
        if data is None:
            raise DataProcessingError("数据为空")
        
        result = data.copy()
        encoded = {}
        
        if columns is None:
            columns = result.select_dtypes(include=['object', 'category']).columns.tolist()
        
        for col in columns:
            if col not in result.columns:
                continue
            
            try:
                if method == 'label':
                    categories = result[col].unique()
                    mapping = {cat: i for i, cat in enumerate(categories)}
                    result[f'{col}_encoded'] = result[col].map(mapping)
                    encoded[col] = True
                elif method == 'onehot':
                    dummies = pd.get_dummies(result[col], prefix=col)
                    result = pd.concat([result, dummies], axis=1)
                    encoded[col] = True
            except Exception:
                encoded[col] = False
        
        return result, encoded
    
    def get_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        if data is None or len(data) == 0:
            return {}
        
        summary = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'numeric_columns': [],
            'categorical_columns': [],
            'missing_values': {},
            'memory_usage': data.memory_usage(deep=True).sum()
        }
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                summary['numeric_columns'].append(col)
            else:
                summary['categorical_columns'].append(col)
            
            null_count = data[col].isnull().sum()
            if null_count > 0:
                summary['missing_values'][col] = int(null_count)
        
        return summary
