import pandas as pd
from typing import Dict, List, Any, Optional
from src.models import DataManager, ConfigManager, Logger
from src.core import DataAnalyzerCore
from src.core.exceptions import AnalysisError


class AnalysisService:
    def __init__(self):
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.analyzer_core = DataAnalyzerCore()

    def _get_data(self) -> pd.DataFrame:
        if not self.data_manager.has_data:
            raise AnalysisError("没有可分析的数据")
        return self.data_manager.get_data()

    def get_descriptive_stats(self, column: str) -> Dict[str, float]:
        data = self._get_data()
        stats = self.analyzer_core.get_descriptive_stats(data, column)
        self.logger.info(f"完成 {column} 的描述性统计分析")
        return stats

    def get_frequency_analysis(self, column: str) -> pd.DataFrame:
        data = self._get_data()
        freq = self.analyzer_core.get_frequency_analysis(data, column)
        self.logger.info(f"完成 {column} 的频率分析")
        return freq

    def get_crosstab(self, row_col: str, col_col: str,
                     normalize: bool = False) -> pd.DataFrame:
        data = self._get_data()
        crosstab = self.analyzer_core.get_crosstab(data, row_col, col_col, normalize)
        self.logger.info(f"完成 {row_col} vs {col_col} 的交叉分析")
        return crosstab

    def compare_by_dimension(self, dimension: str,
                             value_col: str = 'pre_tax_salary') -> pd.DataFrame:
        data = self._get_data()
        comparison = self.analyzer_core.compare_by_dimension(data, dimension, value_col)
        self.logger.info(f"完成 {dimension} 维度的薪资对比分析")
        return comparison

    def get_correlation_matrix(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        data = self._get_data()
        corr = self.analyzer_core.get_correlation_matrix(data, columns)
        self.logger.info("完成相关性矩阵分析")
        return corr

    def get_correlation(self, col1: str, col2: str) -> Dict[str, float]:
        data = self._get_data()
        corr = self.analyzer_core.get_correlation(data, col1, col2)
        self.logger.info(f"完成 {col1} vs {col2} 的相关性分析")
        return corr

    def get_trend_analysis(self, time_col: str, value_col: str) -> pd.DataFrame:
        data = self._get_data()
        trend = self.analyzer_core.get_trend_analysis(data, time_col, value_col)
        self.logger.info(f"完成 {time_col} 的趋势分析")
        return trend

    def get_percentile_distribution(self, column: str) -> Dict[str, float]:
        data = self._get_data()
        distribution = self.analyzer_core.get_percentile_distribution(data, column)
        self.logger.info(f"完成 {column} 的分位数分布分析")
        return distribution

    def get_boxplot_data(self, group_by: str, value_col: str) -> Dict[str, Dict]:
        data = self._get_data()
        data_dict = self.analyzer_core.get_boxplot_data(data, group_by, value_col)
        self.logger.info(f"完成 {group_by} - {value_col} 的箱线图数据生成")
        return data_dict

    def format_stats_result(self, stats: Dict[str, float]) -> str:
        result = ""
        for key, value in stats.items():
            if value is not None:
                if isinstance(value, float):
                    result += f'{key}: {value:,.2f}\n'
                else:
                    result += f'{key}: {value}\n'
        return result
