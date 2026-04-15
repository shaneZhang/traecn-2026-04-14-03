import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple, Any
from scipy import stats


class DataAnalysisError(Exception):
    pass


class DataAnalyzer:
    def __init__(self):
        pass
    
    def get_descriptive_stats(self, data: pd.DataFrame, column: str) -> Dict[str, Any]:
        if data is None or column not in data.columns:
            raise DataAnalysisError(f"列 '{column}' 不存在")
        
        if not pd.api.types.is_numeric_dtype(data[column]):
            raise DataAnalysisError(f"列 '{column}' 不是数值类型")
        
        col_data = data[column].dropna()
        
        if len(col_data) == 0:
            raise DataAnalysisError("没有有效数据")
        
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
    
    def get_grouped_stats(self, data: pd.DataFrame, group_by: str, value_col: str) -> pd.DataFrame:
        if data is None or group_by not in data.columns or value_col not in data.columns:
            raise DataAnalysisError("指定的列不存在")
        
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
        if data is None or column not in data.columns:
            raise DataAnalysisError(f"列 '{column}' 不存在")
        
        freq = data[column].value_counts().reset_index()
        freq.columns = [column, 'count']
        freq['percentage'] = (freq['count'] / freq['count'].sum() * 100).round(2)
        freq = freq.reset_index(drop=True)
        
        return freq
    
    def get_crosstab(self, data: pd.DataFrame, row_col: str, col_col: str,
                     normalize: bool = False) -> pd.DataFrame:
        if data is None:
            raise DataAnalysisError("数据为空")
        
        if row_col not in data.columns or col_col not in data.columns:
            raise DataAnalysisError("指定的列不存在")
        
        crosstab = pd.crosstab(data[row_col], data[col_col])
        
        if normalize:
            crosstab = crosstab.div(crosstab.sum(axis=1), axis=0) * 100
        
        return crosstab
    
    def compare_by_dimension(self, data: pd.DataFrame, dimension: str,
                            value_col: str = 'pre_tax_salary') -> pd.DataFrame:
        if data is None or dimension not in data.columns:
            raise DataAnalysisError(f"维度 '{dimension}' 不存在")
        
        if value_col not in data.columns:
            raise DataAnalysisError(f"数值列 '{value_col}' 不存在")
        
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
    
    def get_correlation_matrix(self, data: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        if data is None:
            raise DataAnalysisError("数据为空")
        
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        if not columns:
            raise DataAnalysisError("没有数值列")
        
        corr_matrix = data[columns].corr().round(3)
        return corr_matrix
    
    def get_correlation(self, data: pd.DataFrame, col1: str, col2: str) -> Dict[str, float]:
        if data is None:
            raise DataAnalysisError("数据为空")
        
        if col1 not in data.columns or col2 not in data.columns:
            raise DataAnalysisError("指定的列不存在")
        
        if not (pd.api.types.is_numeric_dtype(data[col1]) and
                pd.api.types.is_numeric_dtype(data[col2])):
            raise DataAnalysisError("两列都必须是数值类型")
        
        valid_data = data[[col1, col2]].dropna()
        
        if len(valid_data) < 3:
            raise DataAnalysisError("有效数据不足")
        
        pearson_corr, pearson_p = stats.pearsonr(valid_data[col1], valid_data[col2])
        spearman_corr, spearman_p = stats.spearmanr(valid_data[col1], valid_data[col2])
        
        return {
            'pearson_r': round(pearson_corr, 4),
            'pearson_p': round(pearson_p, 4),
            'spearman_r': round(spearman_corr, 4),
            'spearman_p': round(spearman_p, 4)
        }
    
    def get_trend_analysis(self, data: pd.DataFrame, time_col: str, value_col: str) -> pd.DataFrame:
        if data is None or time_col not in data.columns:
            raise DataAnalysisError(f"时间列 '{time_col}' 不存在")
        
        if value_col not in data.columns:
            raise DataAnalysisError(f"数值列 '{value_col}' 不存在")
        
        if not pd.api.types.is_numeric_dtype(data[value_col]):
            raise DataAnalysisError(f"列 '{value_col}' 不是数值类型")
        
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
        if data is None or column not in data.columns:
            raise DataAnalysisError(f"列 '{column}' 不存在")
        
        if percentiles is None:
            percentiles = [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99]
        
        result = {}
        col_data = data[column].dropna()
        
        for p in percentiles:
            result[f'p{int(p)}'] = float(col_data.quantile(p / 100))
        
        return result
    
    def get_salary_distribution(self, data: pd.DataFrame, salary_col: str = 'pre_tax_salary',
                               bins: List[int] = None) -> pd.DataFrame:
        if data is None or salary_col not in data.columns:
            raise DataAnalysisError(f"薪资列 '{salary_col}' 不存在")
        
        if bins is None:
            bins = [0, 5000, 8000, 10000, 15000, 20000, 30000, 50000, 100000, float('inf')]
        
        labels = ['5千以下', '5千-8千', '8千-1万', '1万-1.5万',
                 '1.5万-2万', '2万-3万', '3万-5万', '5万-10万', '10万以上']
        
        try:
            distribution = pd.cut(data[salary_col], bins=bins, labels=labels)
            result = distribution.value_counts().sort_index().reset_index()
            result.columns = ['薪资区间', '人数']
            result['占比'] = (result['人数'] / result['人数'].sum() * 100).round(2)
            return result
        except Exception as e:
            raise DataAnalysisError(f"薪资分布计算失败: {str(e)}")
    
    def get_top_bottom(self, data: pd.DataFrame, column: str, n: int = 10,
                      top: bool = True) -> pd.DataFrame:
        if data is None or column not in data.columns:
            raise DataAnalysisError(f"列 '{column}' 不存在")
        
        if top:
            result = data.nlargest(n, column)
        else:
            result = data.nsmallest(n, column)
        
        return result
    
    def get_summary_report(self, data: pd.DataFrame, salary_col: str = 'pre_tax_salary') -> Dict[str, Any]:
        if data is None or salary_col not in data.columns:
            raise DataAnalysisError(f"薪资列 '{salary_col}' 不存在")
        
        salary_data = data[salary_col].dropna()
        
        if len(salary_data) == 0:
            raise DataAnalysisError("没有有效薪资数据")
        
        report = {
            '数据总量': int(len(data)),
            '有效薪资数据': int(len(salary_data)),
            '平均薪资': round(float(salary_data.mean()), 2),
            '中位薪资': round(float(salary_data.median()), 2),
            '最高薪资': round(float(salary_data.max()), 2),
            '最低薪资': round(float(salary_data.min()), 2),
            '薪资标准差': round(float(salary_data.std()), 2),
            '薪资25分位': round(float(salary_data.quantile(0.25)), 2),
            '薪资75分位': round(float(salary_data.quantile(0.75)), 2),
            '四分位距': round(float(salary_data.quantile(0.75) - salary_data.quantile(0.25)), 2)
        }
        
        return report
    
    def get_dimensions_analysis(self, data: pd.DataFrame, dimensions: List[str],
                               salary_col: str = 'pre_tax_salary') -> Dict[str, pd.DataFrame]:
        if data is None:
            raise DataAnalysisError("数据为空")
        
        results = {}
        
        for dim in dimensions:
            if dim in data.columns:
                results[dim] = self.compare_by_dimension(data, dim, salary_col)
        
        return results
    
    def get_boxplot_data(self, data: pd.DataFrame, group_by: str, value_col: str) -> Dict[str, Dict]:
        if data is None or group_by not in data.columns:
            raise DataAnalysisError(f"分组列 '{group_by}' 不存在")
        
        if value_col not in data.columns:
            raise DataAnalysisError(f"数值列 '{value_col}' 不存在")
        
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
