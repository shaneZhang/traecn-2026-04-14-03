import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Callable, Tuple
from .exceptions import DataProcessingError


class DataProcessorCore:
    def __init__(self):
        self.config = {
            'age_bins': [0, 25, 30, 35, 40, 50, 60, 100],
            'age_labels': ['25岁以下', '25-30岁', '30-35岁', '35-40岁',
                           '40-50岁', '50-60岁', '60岁以上'],
            'salary_bins': [0, 5000, 10000, 15000, 20000, 30000, 50000, 100000],
            'salary_labels': ['5千以下', '5千-1万', '1万-1.5万', '1.5万-2万',
                              '2万-3万', '3万-5万', '5万以上'],
            'experience_bins': [0, 1, 3, 5, 10, 15, 20, 100],
            'experience_labels': ['1年以下', '1-3年', '3-5年', '5-10年',
                                  '10-15年', '15-20年', '20年以上'],
            'outlier_threshold': 1.5,
            'outlier_method': 'iqr'
        }

    def remove_duplicates(self, data: pd.DataFrame,
                          subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
        if data.empty:
            return data, 0

        before_count = len(data)
        result = data.drop_duplicates(subset=subset)
        after_count = len(result)

        return result, before_count - after_count

    def handle_missing_values(self, data: pd.DataFrame, strategy: str = 'drop',
                              columns: Optional[List[str]] = None,
                              fill_value: Any = None) -> Tuple[pd.DataFrame, Dict[str, int]]:
        if data.empty:
            return data, {}

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
                    processed[col] = int(count)
            return result, processed

        for col in columns:
            if col not in result.columns:
                continue

            null_count = result[col].isnull().sum()
            if null_count == 0:
                continue

            if strategy == 'fill_mean' and pd.api.types.is_numeric_dtype(result[col]):
                result[col] = result[col].fillna(result[col].mean())
                processed[col] = int(null_count)

            elif strategy == 'fill_median' and pd.api.types.is_numeric_dtype(result[col]):
                result[col] = result[col].fillna(result[col].median())
                processed[col] = int(null_count)

            elif strategy == 'fill_mode':
                mode_value = result[col].mode()
                if len(mode_value) > 0:
                    result[col] = result[col].fillna(mode_value[0])
                    processed[col] = int(null_count)

            elif strategy == 'fill_value':
                result[col] = result[col].fillna(fill_value)
                processed[col] = int(null_count)

            elif strategy == 'fill_forward':
                result[col] = result[col].ffill()
                processed[col] = int(null_count)

            elif strategy == 'fill_backward':
                result[col] = result[col].bfill()
                processed[col] = int(null_count)

        return result, processed

    def detect_outliers(self, data: pd.DataFrame, column: str,
                        method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
        if data.empty or column not in data.columns:
            return pd.Series([False] * len(data))

        if not pd.api.types.is_numeric_dtype(data[column]):
            return pd.Series([False] * len(data))

        col_data = data[column].dropna()

        if method == 'iqr':
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return (data[column] < lower_bound) | (data[column] > upper_bound)

        elif method == 'zscore':
            mean = col_data.mean()
            std = col_data.std()
            if std > 0:
                z_scores = np.abs((data[column] - mean) / std)
                return z_scores > threshold
            return pd.Series([False] * len(data))

        return pd.Series([False] * len(data))

    def remove_outliers(self, data: pd.DataFrame, column: str,
                        method: str = 'iqr', threshold: float = 1.5) -> Tuple[pd.DataFrame, int]:
        if data.empty:
            return data, 0

        outliers = self.detect_outliers(data, column, method, threshold)
        before_count = len(data)
        result = data[~outliers]
        return result, before_count - len(result)

    def convert_dtype(self, data: pd.DataFrame, column: str, target_type: str) -> pd.DataFrame:
        if data.empty or column not in data.columns:
            return data

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
            raise DataProcessingError(f"类型转换失败: {str(e)}") from e

    def create_age_group(self, data: pd.DataFrame, age_column: str = 'age') -> pd.DataFrame:
        if data.empty or age_column not in data.columns:
            return data

        result = data.copy()
        age_data = pd.to_numeric(result[age_column], errors='coerce')

        result['age_group'] = pd.cut(
            age_data,
            bins=self.config['age_bins'],
            labels=self.config['age_labels'],
            right=False,
            include_lowest=True
        )
        return result

    def create_salary_group(self, data: pd.DataFrame,
                            salary_column: str = 'pre_tax_salary') -> pd.DataFrame:
        if data.empty or salary_column not in data.columns:
            return data

        result = data.copy()
        salary_data = pd.to_numeric(result[salary_column], errors='coerce')

        result['salary_group'] = pd.cut(
            salary_data,
            bins=self.config['salary_bins'],
            labels=self.config['salary_labels'],
            right=False,
            include_lowest=True
        )
        return result

    def create_work_experience_group(self, data: pd.DataFrame,
                                     years_column: str = 'work_years') -> pd.DataFrame:
        if data.empty or years_column not in data.columns:
            return data

        result = data.copy()
        years_data = pd.to_numeric(result[years_column], errors='coerce')

        result['experience_group'] = pd.cut(
            years_data,
            bins=self.config['experience_bins'],
            labels=self.config['experience_labels'],
            right=False
        )
        return result

    def filter_data(self, data: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
        if data.empty:
            return data

        filtered = data.copy()

        for column, value in conditions.items():
            if column not in filtered.columns:
                continue

            if isinstance(value, list):
                filtered = filtered[filtered[column].isin(value)]
            else:
                filtered = filtered[filtered[column] == value]

        return filtered

    def get_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        if data.empty:
            return {}

        summary = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'numeric_columns': [],
            'categorical_columns': [],
            'missing_values': {},
            'memory_usage': float(data.memory_usage(deep=True).sum())
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
