import pandas as pd
from typing import Dict, List, Optional
from src.services import AnalysisService
from src.models import Logger


class AnalysisController:
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.logger = Logger()

    def has_data(self) -> bool:
        try:
            self.analysis_service._get_data()
            return True
        except Exception:
            return False

    def get_descriptive_stats(self, column: str) -> Dict[str, float]:
        try:
            return self.analysis_service.get_descriptive_stats(column)
        except Exception as e:
            self.logger.error(f"描述性统计失败: {str(e)}")
            raise

    def get_frequency_analysis(self, column: str) -> pd.DataFrame:
        try:
            return self.analysis_service.get_frequency_analysis(column)
        except Exception as e:
            self.logger.error(f"频率分析失败: {str(e)}")
            raise

    def get_crosstab(self, row_col: str, col_col: str) -> pd.DataFrame:
        try:
            return self.analysis_service.get_crosstab(row_col, col_col)
        except Exception as e:
            self.logger.error(f"交叉分析失败: {str(e)}")
            raise

    def get_correlation_matrix(self) -> pd.DataFrame:
        try:
            return self.analysis_service.get_correlation_matrix()
        except Exception as e:
            self.logger.error(f"相关性分析失败: {str(e)}")
            raise

    def compare_by_dimension(self, dimension: str, value_col: str) -> pd.DataFrame:
        try:
            return self.analysis_service.compare_by_dimension(dimension, value_col)
        except Exception as e:
            self.logger.error(f"维度对比失败: {str(e)}")
            raise

    def format_descriptive_stats(self, stats: Dict[str, float], column: str) -> str:
        result = f'薪资字段: {column}\n{"="*40}\n\n'
        result += self.analysis_service.format_stats_result(stats)
        return result

    def format_frequency(self, freq: pd.DataFrame, column: str) -> str:
        result = f'频率分析: {column}\n{"="*40}\n\n'
        result += freq.to_string(index=False)
        return result

    def format_crosstab(self, crosstab: pd.DataFrame, column: str) -> str:
        result = f'交叉分析: {column}\n{"="*40}\n\n'
        result += crosstab.to_string()
        return result

    def format_correlation(self, corr: pd.DataFrame) -> str:
        result = f'相关性矩阵\n{"="*40}\n\n'
        result += corr.to_string()
        return result

    def format_comparison(self, comparison: pd.DataFrame, dimension: str, value_col: str) -> str:
        result = f'维度分析: {dimension}\n薪资字段: {value_col}\n{"="*50}\n\n'
        result += comparison.to_string(index=False)
        return result
