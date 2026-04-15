import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple, Any
from scipy import stats


class DataAnalyzerCore:
    def get_descriptive_stats(self, data: pd.DataFrame, column: str) -> Dict[str, float]:
        if data.empty or column not in data.columns:
            return {}

        if not pd.api.types.is_numeric_dtype(data[column]):
            return {}

        col_data = data[column].dropna()

        if len(col_data) == 0:
            return {}

        mode_values = col_data.mode()
        mode_value = float(mode_values[0]) if len(mode_values) > 0 else None

        stats_dict = {
            'count': int(len(col_data)),
            'mean': float(col_data.mean()),
            'median': float(col_data.median()),
            'mode': mode_value,
            'std': float(col_data.std()),
            'min': float(col_data.min()),
            'max': float(col_data.max()),
            'q25': float(col_data.quantile(0.25)),
            'q50': float(col_data.quantile(0.50)),
            'q75': float(col_data.quantile(0.75)),
            'iqr': float(col_data.quantile(0.75) - col_data.quantile(0.25)),
            'skewness': float(col_data.skew()),
            'kurtosis': float(col_data.kurtosis()),
            'variance': float(col_data.var())
        }

        return stats_dict

    def get_grouped_stats(self, data: pd.DataFrame, group_by: str,
                          value_col: str) -> pd.DataFrame:
        if data.empty or group_by not in data.columns or value_col not in data.columns:
            return pd.DataFrame()

        grouped = data.groupby(group_by)[value_col].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max'),
            ('sum', 'sum')
        ]).reset_index()

        return grouped

    def get_frequency_analysis(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        if data.empty or column not in data.columns:
            return pd.DataFrame()

        freq = data[column].value_counts().reset_index()
        if len(freq.columns) == 2:
            freq.columns = [column, 'count']
        freq['percentage'] = (freq['count'] / freq['count'].sum() * 100).round(2)
        freq = freq.reset_index(drop=True)

        return freq

    def get_crosstab(self, data: pd.DataFrame, row_col: str, col_col: str,
                     normalize: bool = False) -> pd.DataFrame:
        if data.empty or row_col not in data.columns or col_col not in data.columns:
            return pd.DataFrame()

        crosstab = pd.crosstab(data[row_col], data[col_col])

        if normalize:
            crosstab = crosstab.div(crosstab.sum(axis=1), axis=0) * 100

        return crosstab

    def compare_by_dimension(self, data: pd.DataFrame, dimension: str,
                             value_col: str = 'pre_tax_salary') -> pd.DataFrame:
        if data.empty or dimension not in data.columns:
            return pd.DataFrame()

        comparison = data.groupby(dimension)[value_col].agg([
            ('人数', 'count'),
            ('平均薪资', 'mean'),
            ('中位薪资', 'median'),
            ('最高薪资', 'max'),
            ('最低薪资', 'min'),
            ('标准差', 'std')
        ]).reset_index()

        comparison['平均薪资'] = comparison['平均薪资'].round(2)
        comparison['中位薪资'] = comparison['中位薪资'].round(2)
        comparison['标准差'] = comparison['标准差'].round(2)

        return comparison

    def get_correlation_matrix(self, data: pd.DataFrame,
                               columns: Optional[List[str]] = None) -> pd.DataFrame:
        if data.empty:
            return pd.DataFrame()

        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()

        if not columns:
            return pd.DataFrame()

        corr_matrix = data[columns].corr().round(3)
        return corr_matrix

    def get_correlation(self, data: pd.DataFrame, col1: str, col2: str) -> Dict[str, float]:
        if data.empty:
            return {}

        if col1 not in data.columns or col2 not in data.columns:
            return {}

        if not (pd.api.types.is_numeric_dtype(data[col1]) and
                pd.api.types.is_numeric_dtype(data[col2])):
            return {}

        valid_data = data[[col1, col2]].dropna()

        if len(valid_data) < 3:
            return {}

        pearson_corr, pearson_p = stats.pearsonr(valid_data[col1], valid_data[col2])
        spearman_corr, spearman_p = stats.spearmanr(valid_data[col1], valid_data[col2])

        return {
            'pearson_r': round(pearson_corr, 4),
            'pearson_p': round(pearson_p, 4),
            'spearman_r': round(spearman_corr, 4),
            'spearman_p': round(spearman_p, 4)
        }

    def get_trend_analysis(self, data: pd.DataFrame, time_col: str,
                           value_col: str) -> pd.DataFrame:
        if data.empty or time_col not in data.columns:
            return pd.DataFrame()

        if not pd.api.types.is_numeric_dtype(data[value_col]):
            return pd.DataFrame()

        trend = data.groupby(time_col)[value_col].agg([
            ('人数', 'count'),
            ('平均薪资', 'mean'),
            ('中位薪资', 'median'),
            ('总薪资', 'sum')
        ]).reset_index()

        trend['平均薪资'] = trend['平均薪资'].round(2)
        trend['中位薪资'] = trend['中位薪资'].round(2)

        if len(trend) > 1:
            trend['薪资增长率'] = trend['平均薪资'].pct_change() * 100
            trend['薪资增长率'] = trend['薪资增长率'].round(2)

        return trend

    def get_percentile_distribution(self, data: pd.DataFrame, column: str,
                                    percentiles: List[float] = None) -> Dict[str, float]:
        if data.empty or column not in data.columns:
            return {}

        if percentiles is None:
            percentiles = [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99]

        result = {}
        col_data = data[column].dropna()

        for p in percentiles:
            result[f'p{int(p)}'] = float(col_data.quantile(p / 100))

        return result

    def get_boxplot_data(self, data: pd.DataFrame, group_by: str,
                         value_col: str) -> Dict[str, Dict]:
        if data.empty or group_by not in data.columns:
            return {}

        result = {}

        for category in data[group_by].unique():
            subset = data[data[group_by] == category][value_col].dropna()

            if len(subset) > 0:
                result[str(category)] = {
                    'min': float(subset.min()),
                    'q1': float(subset.quantile(0.25)),
                    'median': float(subset.median()),
                    'q3': float(subset.quantile(0.75)),
                    'max': float(subset.max()),
                    'mean': float(subset.mean()),
                    'count': int(len(subset))
                }

        return result
