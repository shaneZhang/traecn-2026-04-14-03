from typing import Optional, List, Dict, Any
import pandas as pd

from ..models.data_manager import DataManager
from ..models.config_manager import ConfigManager
from ..models.logger import get_logger
from .data_analyzer_service import DataAnalyzer, DataAnalysisError


class AnalysisService:
    def __init__(self, data_manager: DataManager, config: Optional[ConfigManager] = None):
        self.data_manager = data_manager
        self.config = config or ConfigManager()
        self.logger = get_logger('AnalysisService')
        self.analyzer = DataAnalyzer()
    
    def get_descriptive_stats(self, column: str) -> Dict[str, Any]:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_descriptive_stats(data, column)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"获取描述性统计失败: {str(e)}")
            raise DataAnalysisError(f"获取描述性统计失败: {str(e)}")
    
    def get_frequency_analysis(self, column: str) -> pd.DataFrame:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_frequency_analysis(data, column)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"频率分析失败: {str(e)}")
            raise DataAnalysisError(f"频率分析失败: {str(e)}")
    
    def get_crosstab(self, row_col: str, col_col: str, normalize: bool = False) -> pd.DataFrame:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_crosstab(data, row_col, col_col, normalize)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"交叉分析失败: {str(e)}")
            raise DataAnalysisError(f"交叉分析失败: {str(e)}")
    
    def compare_by_dimension(self, dimension: str, value_col: str = 'pre_tax_salary') -> pd.DataFrame:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.compare_by_dimension(data, dimension, value_col)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"维度对比分析失败: {str(e)}")
            raise DataAnalysisError(f"维度对比分析失败: {str(e)}")
    
    def get_correlation_matrix(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_correlation_matrix(data, columns)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"相关性分析失败: {str(e)}")
            raise DataAnalysisError(f"相关性分析失败: {str(e)}")
    
    def get_correlation(self, col1: str, col2: str) -> Dict[str, float]:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_correlation(data, col1, col2)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"相关性计算失败: {str(e)}")
            raise DataAnalysisError(f"相关性计算失败: {str(e)}")
    
    def get_trend_analysis(self, time_col: str, value_col: str = 'pre_tax_salary') -> pd.DataFrame:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_trend_analysis(data, time_col, value_col)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"趋势分析失败: {str(e)}")
            raise DataAnalysisError(f"趋势分析失败: {str(e)}")
    
    def get_summary_report(self, salary_col: str = 'pre_tax_salary') -> Dict[str, Any]:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_summary_report(data, salary_col)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"获取摘要报告失败: {str(e)}")
            raise DataAnalysisError(f"获取摘要报告失败: {str(e)}")
    
    def get_boxplot_data(self, group_by: str, value_col: str) -> Dict[str, Dict]:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_boxplot_data(data, group_by, value_col)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"获取箱线图数据失败: {str(e)}")
            raise DataAnalysisError(f"获取箱线图数据失败: {str(e)}")
    
    def get_salary_distribution(self, salary_col: str = 'pre_tax_salary') -> pd.DataFrame:
        data = self.data_manager.get_data()
        if data is None:
            raise DataAnalysisError("没有可分析的数据")
        
        try:
            return self.analyzer.get_salary_distribution(data, salary_col)
        except DataAnalysisError:
            raise
        except Exception as e:
            self.logger.exception(f"获取薪资分布失败: {str(e)}")
            raise DataAnalysisError(f"获取薪资分布失败: {str(e)}")
