import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Callable, Tuple

from ..utils.exceptions import DataProcessError
from ..models.config_manager import ConfigManager
from ..models.logger import Logger


class ProcessingService:
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager.get_instance()
        self.logger = Logger.get_instance()

    def remove_duplicates(self, data: pd.DataFrame, subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
        try:
            before_count = len(data)
            result = data.drop_duplicates(subset=subset)
            after_count = len(result)
            removed_count = before_count - after_count
            
            self.logger.info(f"删除重复数据: 删除了 {removed_count} 条记录")
            return result, removed_count
        except Exception as e:
            self.logger.error(f"删除重复数据失败: {str(e)}")
            raise DataProcessError(f"删除重复数据失败: {str(e)}")

    def handle_missing_values(self, data: pd.DataFrame, strategy: str = 'drop',
                             columns: Optional[List[str]] = None,
                             fill_value: Any = None) -> Tuple[pd.DataFrame, Dict[str, int]]:
        try:
            result = data.copy()
            
            if columns is None:
                columns = result.columns.tolist()
            
            result_info = {}
            
            if strategy == 'drop':
                null_counts = result[columns].isnull().sum()
                cols_with_null = null_counts[null_counts > 0]
                
                if len(cols_with_null) > 0:
                    before_count = len(result)
                    result = result.dropna(subset=columns)
                    
                    for col, count in cols_with_null.items():
                        result_info[col] = int(count)
                
                self.logger.info(f"删除缺失值: 删除了 {len(data) - len(result)} 条记录")
                return result, result_info
            
            for col in columns:
                if col not in result.columns:
                    continue
                
                null_count = result[col].isnull().sum()
                
                if null_count == 0:
                    continue
                
                if strategy == 'fill_mean' and pd.api.types.is_numeric_dtype(result[col]):
                    result[col] = result[col].fillna(result[col].mean())
                    result_info[col] = int(null_count)
                
                elif strategy == 'fill_median' and pd.api.types.is_numeric_dtype(result[col]):
                    result[col] = result[col].fillna(result[col].median())
                    result_info[col] = int(null_count)
                
                elif strategy == 'fill_mode':
                    mode_value = result[col].mode()
                    if len(mode_value) > 0:
                        result[col] = result[col].fillna(mode_value[0])
                        result_info[col] = int(null_count)
                
                elif strategy == 'fill_value':
                    result[col] = result[col].fillna(fill_value)
                    result_info[col] = int(null_count)
                
                elif strategy == 'fill_forward':
                    result[col] = result[col].ffill()
                    result_info[col] = int(null_count)
                
                elif strategy == 'fill_backward':
                    result[col] = result[col].bfill()
                    result_info[col] = int(null_count)
            
            self.logger.info(f"处理缺失值: 策略={strategy}, 影响列={list(result_info.keys())}")
            return result, result_info
            
        except Exception as e:
            self.logger.error(f"处理缺失值失败: {str(e)}")
            raise DataProcessError(f"处理缺失值失败: {str(e)}")

    def detect_outliers(self, data: pd.DataFrame, column: str, method: str = 'iqr',
                       threshold: float = 1.5) -> pd.Series:
        try:
            if column not in data.columns:
                raise DataProcessError(f"列 '{column}' 不存在")
            
            if not pd.api.types.is_numeric_dtype(data[column]):
                raise DataProcessError(f"列 '{column}' 不是数值类型")
            
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
                z_scores = np.abs((data[column] - mean) / std)
                return z_scores > threshold
            
            else:
                raise DataProcessError(f"不支持的异常值检测方法: {method}")
                
        except Exception as e:
            self.logger.error(f"异常值检测失败: {str(e)}")
            raise DataProcessError(f"异常值检测失败: {str(e)}")

    def remove_outliers(self, data: pd.DataFrame, column: str, method: str = 'iqr',
                       threshold: float = 1.5) -> Tuple[pd.DataFrame, int]:
        try:
            outliers = self.detect_outliers(data, column, method, threshold)
            before_count = len(data)
            result = data[~outliers]
            removed_count = before_count - len(result)
            
            self.logger.info(f"移除异常值: 列={column}, 移除了 {removed_count} 条记录")
            return result, removed_count
        except Exception as e:
            self.logger.error(f"移除异常值失败: {str(e)}")
            raise DataProcessError(f"移除异常值失败: {str(e)}")

    def create_age_group(self, data: pd.DataFrame, age_column: str = 'age') -> pd.DataFrame:
        try:
            if age_column not in data.columns:
                raise DataProcessError(f"年龄列 '{age_column}' 不存在")
            
            grouping_config = self.config.get_grouping_config('age')
            bins = grouping_config.get('bins', [0, 25, 30, 35, 40, 50, 60, 100])
            labels = grouping_config.get('labels', ['25岁以下', '25-30岁', '30-35岁', '35-40岁',
                                                     '40-50岁', '50-60岁', '60岁以上'])
            
            result = data.copy()
            age_data = pd.to_numeric(result[age_column], errors='coerce')
            
            result['age_group'] = pd.cut(age_data,
                                        bins=bins,
                                        labels=labels,
                                        right=False,
                                        include_lowest=True)
            
            self.logger.info(f"创建年龄分组: 使用列 '{age_column}'")
            return result
        except Exception as e:
            self.logger.error(f"年龄分组失败: {str(e)}")
            raise DataProcessError(f"年龄分组失败: {str(e)}")

    def create_salary_group(self, data: pd.DataFrame, salary_column: str = 'pre_tax_salary') -> pd.DataFrame:
        try:
            if salary_column not in data.columns:
                raise DataProcessError(f"薪资列 '{salary_column}' 不存在")
            
            grouping_config = self.config.get_grouping_config('salary')
            bins = grouping_config.get('bins', [0, 5000, 10000, 15000, 20000, 30000, 50000, float('inf')])
            labels = grouping_config.get('labels', ['5千以下', '5千-1万', '1万-1.5万', '1.5万-2万',
                                                     '2万-3万', '3万-5万', '5万以上'])
            
            result = data.copy()
            salary_data = pd.to_numeric(result[salary_column], errors='coerce')
            
            result['salary_group'] = pd.cut(salary_data,
                                           bins=bins,
                                           labels=labels,
                                           right=False,
                                           include_lowest=True)
            
            self.logger.info(f"创建薪资分组: 使用列 '{salary_column}'")
            return result
        except Exception as e:
            self.logger.error(f"薪资分组失败: {str(e)}")
            raise DataProcessError(f"薪资分组失败: {str(e)}")

    def create_work_experience_group(self, data: pd.DataFrame, years_column: str = 'work_years') -> pd.DataFrame:
        try:
            if years_column not in data.columns:
                raise DataProcessError(f"工作年限列 '{years_column}' 不存在")
            
            grouping_config = self.config.get_grouping_config('experience')
            bins = grouping_config.get('bins', [0, 1, 3, 5, 10, 15, 20, float('inf')])
            labels = grouping_config.get('labels', ['1年以下', '1-3年', '3-5年', '5-10年',
                                                     '10-15年', '15-20年', '20年以上'])
            
            result = data.copy()
            years_data = pd.to_numeric(result[years_column], errors='coerce')
            
            result['experience_group'] = pd.cut(years_data,
                                               bins=bins,
                                               labels=labels,
                                               right=False)
            
            self.logger.info(f"创建工作年限分组: 使用列 '{years_column}'")
            return result
        except Exception as e:
            self.logger.error(f"工作年限分组失败: {str(e)}")
            raise DataProcessError(f"工作年限分组失败: {str(e)}")

    def filter_data(self, data: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
        try:
            result = data.copy()
            
            for column, value in conditions.items():
                if column not in result.columns:
                    continue
                
                if isinstance(value, list):
                    result = result[result[column].isin(value)]
                else:
                    result = result[result[column] == value]
            
            self.logger.info(f"数据筛选: 条件={conditions}, 结果记录数={len(result)}")
            return result
        except Exception as e:
            self.logger.error(f"数据筛选失败: {str(e)}")
            raise DataProcessError(f"数据筛选失败: {str(e)}")

    def convert_dtype(self, data: pd.DataFrame, column: str, target_type: str) -> pd.DataFrame:
        try:
            if column not in data.columns:
                raise DataProcessError(f"列 '{column}' 不存在")
            
            result = data.copy()
            
            if target_type == 'numeric':
                result[column] = pd.to_numeric(result[column], errors='coerce')
            elif target_type == 'string':
                result[column] = result[column].astype(str)
            elif target_type == 'datetime':
                result[column] = pd.to_datetime(result[column], errors='coerce')
            elif target_type == 'category':
                result[column] = result[column].astype('category')
            else:
                raise DataProcessError(f"不支持的目标类型: {target_type}")
            
            self.logger.info(f"类型转换: 列={column}, 目标类型={target_type}")
            return result
        except Exception as e:
            self.logger.error(f"类型转换失败: {str(e)}")
            raise DataProcessError(f"类型转换失败: {str(e)}")

    def encode_categorical(self, data: pd.DataFrame, columns: Optional[List[str]] = None,
                          method: str = 'label') -> Tuple[pd.DataFrame, Dict[str, bool]]:
        try:
            result = data.copy()
            
            if columns is None:
                columns = result.select_dtypes(include=['object', 'category']).columns.tolist()
            
            result_info = {}
            
            for col in columns:
                if col not in result.columns:
                    continue
                
                if method == 'label':
                    categories = result[col].unique()
                    mapping = {cat: i for i, cat in enumerate(categories)}
                    result[f'{col}_encoded'] = result[col].map(mapping)
                    result_info[col] = True
                elif method == 'onehot':
                    dummies = pd.get_dummies(result[col], prefix=col)
                    result = pd.concat([result, dummies], axis=1)
                    result_info[col] = True
            
            self.logger.info(f"分类编码: 方法={method}, 列={list(result_info.keys())}")
            return result, result_info
        except Exception as e:
            self.logger.error(f"分类编码失败: {str(e)}")
            raise DataProcessError(f"分类编码失败: {str(e)}")
