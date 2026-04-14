import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Callable
import tkinter as tk
from tkinter import messagebox


class DataProcessor:
    def __init__(self, data: Optional[pd.DataFrame] = None):
        self.data = data.copy() if data is not None else None
        self.original_data = data.copy() if data is not None else None
    
    def set_data(self, data: pd.DataFrame):
        self.data = data.copy()
        self.original_data = data.copy()
    
    def reset_data(self):
        if self.original_data is not None:
            self.data = self.original_data.copy()
    
    def remove_duplicates(self, subset: Optional[List[str]] = None) -> int:
        if self.data is None:
            return 0
        
        before_count = len(self.data)
        self.data.drop_duplicates(subset=subset, inplace=True)
        after_count = len(self.data)
        
        return before_count - after_count
    
    def handle_missing_values(self, strategy: str = 'drop', 
                            columns: Optional[List[str]] = None,
                            fill_value: Any = None) -> Dict[str, int]:
        if self.data is None:
            return {}
        
        result = {}
        
        if columns is None:
            columns = self.data.columns.tolist()
        
        # 处理drop策略：一次性删除所有包含缺失值的行
        if strategy == 'drop':
            null_counts = self.data[columns].isnull().sum()
            cols_with_null = null_counts[null_counts > 0]
            
            if len(cols_with_null) > 0:
                before_count = len(self.data)
                self.data.dropna(subset=columns, inplace=True)
                after_count = len(self.data)
                dropped_count = before_count - after_count
                
                for col, count in cols_with_null.items():
                    result[col] = count
            
            return result
        
        # 其他策略按列处理
        for col in columns:
            if col not in self.data.columns:
                continue
            
            null_count = self.data[col].isnull().sum()
            
            if null_count == 0:
                continue
            
            if strategy == 'fill_mean' and pd.api.types.is_numeric_dtype(self.data[col]):
                self.data[col] = self.data[col].fillna(self.data[col].mean())
                result[col] = null_count
            
            elif strategy == 'fill_median' and pd.api.types.is_numeric_dtype(self.data[col]):
                self.data[col] = self.data[col].fillna(self.data[col].median())
                result[col] = null_count
            
            elif strategy == 'fill_mode':
                mode_value = self.data[col].mode()
                if len(mode_value) > 0:
                    self.data[col] = self.data[col].fillna(mode_value[0])
                    result[col] = null_count
            
            elif strategy == 'fill_value':
                self.data[col] = self.data[col].fillna(fill_value)
                result[col] = null_count
            
            elif strategy == 'fill_forward':
                self.data[col] = self.data[col].ffill()
                result[col] = null_count
            
            elif strategy == 'fill_backward':
                self.data[col] = self.data[col].bfill()
                result[col] = null_count
        
        return result
    
    def detect_outliers(self, column: str, method: str = 'iqr', 
                       threshold: float = 1.5) -> pd.Series:
        if self.data is None or column not in self.data.columns:
            return pd.Series()
        
        if not pd.api.types.is_numeric_dtype(self.data[column]):
            return pd.Series()
        
        if method == 'iqr':
            Q1 = self.data[column].quantile(0.25)
            Q3 = self.data[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return (self.data[column] < lower_bound) | (self.data[column] > upper_bound)
        
        elif method == 'zscore':
            mean = self.data[column].mean()
            std = self.data[column].std()
            z_scores = np.abs((self.data[column] - mean) / std)
            return z_scores > threshold
        
        return pd.Series()
    
    def remove_outliers(self, column: str, method: str = 'iqr', 
                       threshold: float = 1.5) -> int:
        if self.data is None:
            return 0
        
        outliers = self.detect_outliers(column, method, threshold)
        before_count = len(self.data)
        self.data = self.data[~outliers]
        
        return before_count - len(self.data)
    
    def handle_outliers(self, column: str, strategy: str = 'remove',
                       method: str = 'iqr', threshold: float = 1.5) -> int:
        return self.remove_outliers(column, method, threshold)
    
    def convert_dtype(self, column: str, target_type: str) -> bool:
        if self.data is None or column not in self.data.columns:
            return False
        
        try:
            if target_type == 'numeric':
                self.data[column] = pd.to_numeric(self.data[column], errors='coerce')
            elif target_type == 'string':
                self.data[column] = self.data[column].astype(str)
            elif target_type == 'datetime':
                self.data[column] = pd.to_datetime(self.data[column], errors='coerce')
            elif target_type == 'category':
                self.data[column] = self.data[column].astype('category')
            return True
        except Exception as e:
            messagebox.showerror('错误', f'类型转换失败: {str(e)}')
            return False
    
    def create_calculated_field(self, field_name: str, 
                               calculation: Callable[[pd.DataFrame], pd.Series]) -> bool:
        if self.data is None:
            return False
        
        try:
            self.data[field_name] = calculation(self.data)
            return True
        except Exception as e:
            messagebox.showerror('错误', f'计算字段创建失败: {str(e)}')
            return False
    
    def calculate_age_from_year(self, birth_year_column: str, 
                                reference_year: Optional[int] = None) -> bool:
        if self.data is None or birth_year_column not in self.data.columns:
            return False
        
        if reference_year is None:
            reference_year = pd.Timestamp.now().year
        
        try:
            self.data['age'] = reference_year - pd.to_numeric(self.data[birth_year_column], errors='coerce')
            return True
        except Exception as e:
            messagebox.showerror('错误', f'年龄计算失败: {str(e)}')
            return False
    
    def create_age_group(self, age_column: str = 'age', 
                        bins: Optional[List[int]] = None) -> bool:
        if self.data is None or age_column not in self.data.columns:
            return False
        
        if bins is None:
            bins = [0, 25, 30, 35, 40, 50, 60, 100]
        
        try:
            # bins有8个边界，需要7个labels
            labels = ['25岁以下', '25-30岁', '30-35岁', '35-40岁', 
                     '40-50岁', '50-60岁', '60岁以上']
            
            # 确保年龄列是数值类型
            age_data = pd.to_numeric(self.data[age_column], errors='coerce')
            
            self.data['age_group'] = pd.cut(age_data, 
                                           bins=bins, 
                                           labels=labels,
                                           right=False,
                                           include_lowest=True)
            return True
        except Exception as e:
            messagebox.showerror('错误', f'年龄分组失败: {str(e)}')
            return False
    
    def create_salary_group(self, salary_column: str = 'pre_tax_salary',
                          bins: Optional[List[int]] = None) -> bool:
        if self.data is None or salary_column not in self.data.columns:
            return False
        
        if bins is None:
            bins = [0, 5000, 10000, 15000, 20000, 30000, 50000, float('inf')]
        
        try:
            # bins有8个边界，需要7个labels
            labels = ['5千以下', '5千-1万', '1万-1.5万', '1.5万-2万', 
                     '2万-3万', '3万-5万', '5万以上']
            
            # 确保薪资列是数值类型
            salary_data = pd.to_numeric(self.data[salary_column], errors='coerce')
            
            self.data['salary_group'] = pd.cut(salary_data,
                                               bins=bins,
                                               labels=labels,
                                               right=False,
                                               include_lowest=True)
            return True
        except Exception as e:
            messagebox.showerror('错误', f'薪资分组失败: {str(e)}')
            return False
    
    def create_work_experience_group(self, years_column: str = 'work_years') -> bool:
        if self.data is None or years_column not in self.data.columns:
            return False
        
        try:
            bins = [0, 1, 3, 5, 10, 15, 20, float('inf')]
            labels = ['1年以下', '1-3年', '3-5年', '5-10年', 
                     '10-15年', '15-20年', '20年以上']
            self.data['experience_group'] = pd.cut(pd.to_numeric(self.data[years_column], errors='coerce'),
                                                    bins=bins,
                                                    labels=labels,
                                                    right=False)
            return True
        except Exception as e:
            messagebox.showerror('错误', f'工作年限分组失败: {str(e)}')
            return False
    
    def filter_data(self, conditions: Dict[str, Any]) -> pd.DataFrame:
        if self.data is None:
            return pd.DataFrame()
        
        filtered = self.data.copy()
        
        for column, value in conditions.items():
            if column not in filtered.columns:
                continue
            
            if isinstance(value, list):
                filtered = filtered[filtered[column].isin(value)]
            else:
                filtered = filtered[filtered[column] == value]
        
        return filtered
    
    def apply_filter(self, conditions: Dict[str, Any]) -> int:
        if self.data is None:
            return 0
        
        before_count = len(self.data)
        self.data = self.filter_data(conditions)
        
        return before_count - len(self.data)
    
    def encode_categorical(self, columns: Optional[List[str]] = None,
                          method: str = 'label') -> Dict[str, bool]:
        if self.data is None:
            return {}
        
        result = {}
        
        if columns is None:
            columns = self.data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        for col in columns:
            if col not in self.data.columns:
                continue
            
            try:
                if method == 'label':
                    categories = self.data[col].unique()
                    mapping = {cat: i for i, cat in enumerate(categories)}
                    self.data[f'{col}_encoded'] = self.data[col].map(mapping)
                    result[col] = True
                elif method == 'onehot':
                    dummies = pd.get_dummies(self.data[col], prefix=col)
                    self.data = pd.concat([self.data, dummies], axis=1)
                    result[col] = True
            except Exception as e:
                result[col] = False
        
        return result
    
    def get_data_summary(self) -> Dict[str, Any]:
        if self.data is None:
            return {}
        
        summary = {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'numeric_columns': [],
            'categorical_columns': [],
            'missing_values': {},
            'memory_usage': self.data.memory_usage(deep=True).sum()
        }
        
        for col in self.data.columns:
            if pd.api.types.is_numeric_dtype(self.data[col]):
                summary['numeric_columns'].append(col)
            else:
                summary['categorical_columns'].append(col)
            
            null_count = self.data[col].isnull().sum()
            if null_count > 0:
                summary['missing_values'][col] = int(null_count)
        
        return summary
    
    def get_current_data(self) -> Optional[pd.DataFrame]:
        return self.data
