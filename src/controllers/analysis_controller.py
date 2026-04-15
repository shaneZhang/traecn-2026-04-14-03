from typing import Optional, Callable, Dict, Any, List
import pandas as pd

from ..services.analysis_service import AnalysisService
from ..models.data_manager import DataManager
from ..models.logger import Logger
from ..utils.exceptions import SalaryAnalysisError


class AnalysisController:
    """分析控制器，处理分析相关的用户操作"""

    def __init__(self, analysis_service: Optional[AnalysisService] = None,
                 data_manager: Optional[DataManager] = None):
        self.analysis_service = analysis_service or AnalysisService()
        self.data_manager = data_manager or DataManager.get_instance()
        self.logger = Logger.get_instance()

        self._error_handlers: List[Callable[[str], None]] = []
        self._result_handlers: List[Callable[[Any, str], None]] = []

    def add_error_handler(self, handler: Callable[[str], None]):
        """添加错误处理器"""
        self._error_handlers.append(handler)

    def add_result_handler(self, handler: Callable[[Any, str], None]):
        """添加结果处理器"""
        self._result_handlers.append(handler)

    def _notify_error(self, message: str):
        """通知错误"""
        self.logger.error(message)
        for handler in self._error_handlers:
            handler(message)

    def _notify_result(self, result: Any, title: str = ""):
        """通知结果"""
        for handler in self._result_handlers:
            handler(result, title)

    def get_descriptive_stats(self, column: str) -> bool:
        """获取描述性统计"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            stats = self.analysis_service.get_descriptive_stats(data, column)

            result_text = f"描述性统计: {column}\n"
            result_text += "=" * 50 + "\n\n"

            for key, value in stats.items():
                if value is not None:
                    if isinstance(value, float):
                        result_text += f"{key}: {value:,.2f}\n"
                    else:
                        result_text += f"{key}: {value}\n"

            self._notify_result(result_text, f"描述性统计 - {column}")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取描述性统计时发生错误: {str(e)}")
            return False

    def get_frequency_analysis(self, column: str) -> bool:
        """获取频率分析"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            freq = self.analysis_service.get_frequency_analysis(data, column)

            result_text = f"频率分析: {column}\n"
            result_text += "=" * 50 + "\n\n"
            result_text += freq.to_string(index=False)

            self._notify_result(result_text, f"频率分析 - {column}")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取频率分析时发生错误: {str(e)}")
            return False

    def get_crosstab(self, row_col: str, col_col: str) -> bool:
        """获取交叉分析"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            crosstab = self.analysis_service.get_crosstab(data, row_col, col_col)

            result_text = f"交叉分析: {row_col} vs {col_col}\n"
            result_text += "=" * 50 + "\n\n"
            result_text += crosstab.to_string()

            self._notify_result(result_text, f"交叉分析 - {row_col} vs {col_col}")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取交叉分析时发生错误: {str(e)}")
            return False

    def get_correlation_matrix(self) -> bool:
        """获取相关性矩阵"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            corr = self.analysis_service.get_correlation_matrix(data)

            if corr.empty:
                self._notify_error("没有可用的数值列进行相关性分析")
                return False

            result_text = "相关性矩阵\n"
            result_text += "=" * 50 + "\n\n"
            result_text += corr.to_string()

            self._notify_result(result_text, "相关性矩阵")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取相关性矩阵时发生错误: {str(e)}")
            return False

    def get_correlation(self, col1: str, col2: str) -> bool:
        """获取两列相关性"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            corr = self.analysis_service.get_correlation(data, col1, col2)

            result_text = f"相关性分析: {col1} vs {col2}\n"
            result_text += "=" * 50 + "\n\n"

            for key, value in corr.items():
                result_text += f"{key}: {value}\n"

            self._notify_result(result_text, f"相关性分析 - {col1} vs {col2}")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取相关性时发生错误: {str(e)}")
            return False

    def compare_by_dimension(self, dimension: str, value_col: str = 'pre_tax_salary') -> bool:
        """按维度对比"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            comparison = self.analysis_service.compare_by_dimension(data, dimension, value_col)

            result_text = f"维度对比: {dimension}\n"
            result_text += "=" * 50 + "\n\n"
            result_text += comparison.to_string(index=False)

            self._notify_result(result_text, f"维度对比 - {dimension}")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"维度对比时发生错误: {str(e)}")
            return False

    def get_trend_analysis(self, time_col: str, value_col: str) -> bool:
        """获取趋势分析"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            trend = self.analysis_service.get_trend_analysis(data, time_col, value_col)

            result_text = f"趋势分析: {time_col}\n"
            result_text += "=" * 50 + "\n\n"
            result_text += trend.to_string(index=False)

            self._notify_result(result_text, f"趋势分析 - {time_col}")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取趋势分析时发生错误: {str(e)}")
            return False

    def get_summary_report(self, salary_col: str = 'pre_tax_salary') -> bool:
        """获取汇总报告"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            report = self.analysis_service.get_summary_report(data, salary_col)

            result_text = "薪资汇总报告\n"
            result_text += "=" * 50 + "\n\n"

            for key, value in report.items():
                result_text += f"{key}: {value}\n"

            self._notify_result(result_text, "薪资汇总报告")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取汇总报告时发生错误: {str(e)}")
            return False

    def get_salary_distribution(self, salary_col: str = 'pre_tax_salary') -> bool:
        """获取薪资分布"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            distribution = self.analysis_service.get_salary_distribution(data, salary_col)

            result_text = "薪资分布\n"
            result_text += "=" * 50 + "\n\n"
            result_text += distribution.to_string(index=False)

            self._notify_result(result_text, "薪资分布")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"获取薪资分布时发生错误: {str(e)}")
            return False
