from typing import Optional, Callable, Dict, Any, List
from matplotlib.figure import Figure

from ..services.visualization_service import VisualizationService
from ..services.analysis_service import AnalysisService
from ..models.data_manager import DataManager
from ..models.logger import Logger
from ..utils.exceptions import SalaryAnalysisError


class VisualizationController:
    """可视化控制器，处理可视化相关的用户操作"""

    def __init__(self, visualization_service: Optional[VisualizationService] = None,
                 analysis_service: Optional[AnalysisService] = None,
                 data_manager: Optional[DataManager] = None):
        self.visualization_service = visualization_service or VisualizationService()
        self.analysis_service = analysis_service or AnalysisService()
        self.data_manager = data_manager or DataManager.get_instance()
        self.logger = Logger.get_instance()

        self._error_handlers: List[Callable[[str], None]] = []
        self._figure_handlers: List[Callable[[Figure], None]] = []

    def add_error_handler(self, handler: Callable[[str], None]):
        """添加错误处理器"""
        self._error_handlers.append(handler)

    def add_figure_handler(self, handler: Callable[[Figure], None]):
        """添加图表处理器"""
        self._figure_handlers.append(handler)

    def _notify_error(self, message: str):
        """通知错误"""
        self.logger.error(message)
        for handler in self._error_handlers:
            handler(message)

    def _notify_figure(self, figure: Figure):
        """通知图表"""
        for handler in self._figure_handlers:
            handler(figure)

    def create_bar_chart(self, dimension: str, salary_col: str = 'pre_tax_salary') -> bool:
        """创建柱状图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            figure = self.visualization_service.create_comparison_chart(
                data, dimension, salary_col, chart_type='bar'
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建柱状图时发生错误: {str(e)}")
            return False

    def create_horizontal_bar_chart(self, dimension: str, salary_col: str = 'pre_tax_salary') -> bool:
        """创建水平柱状图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            figure = self.visualization_service.create_comparison_chart(
                data, dimension, salary_col, chart_type='horizontal'
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建水平柱状图时发生错误: {str(e)}")
            return False

    def create_pie_chart(self, dimension: str, salary_col: str = 'pre_tax_salary') -> bool:
        """创建饼图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            grouped = data.groupby(dimension)[salary_col].sum().sort_values(ascending=False)
            top_n = min(8, len(grouped))
            grouped = grouped.head(top_n)

            figure = self.visualization_service.create_pie_chart(
                data=grouped.values.tolist(),
                labels=grouped.index.tolist(),
                title=f'{dimension} - 薪资占比'
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建饼图时发生错误: {str(e)}")
            return False

    def create_line_chart(self, time_col: str, salary_col: str = 'pre_tax_salary') -> bool:
        """创建折线图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            figure = self.visualization_service.create_trend_chart(
                data, time_col, salary_col
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建折线图时发生错误: {str(e)}")
            return False

    def create_scatter_chart(self, x_col: str, y_col: str) -> bool:
        """创建散点图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            valid_data = data[[x_col, y_col]].dropna()

            figure = self.visualization_service.create_scatter_chart(
                x_data=valid_data[x_col].tolist(),
                y_data=valid_data[y_col].tolist(),
                title=f'{x_col} vs {y_col}',
                xlabel=x_col,
                ylabel=y_col
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建散点图时发生错误: {str(e)}")
            return False

    def create_boxplot(self, dimension: str, salary_col: str = 'pre_tax_salary') -> bool:
        """创建箱线图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            boxplot_data = self.analysis_service.get_boxplot_data(data, dimension, salary_col)

            figure = self.visualization_service.create_boxplot(
                data_dict=boxplot_data,
                title=f'{dimension} - 薪资分布',
                xlabel=dimension,
                ylabel='薪资'
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建箱线图时发生错误: {str(e)}")
            return False

    def create_histogram(self, salary_col: str = 'pre_tax_salary') -> bool:
        """创建直方图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            salary_data = data[salary_col].dropna().values

            figure = self.visualization_service.create_histogram(
                data=salary_data,
                bins=20,
                title='薪资分布直方图',
                xlabel='薪资'
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建直方图时发生错误: {str(e)}")
            return False

    def create_heatmap(self, columns: Optional[List[str]] = None) -> bool:
        """创建热力图"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("请先加载数据")
                return False

            corr_matrix = self.analysis_service.get_correlation_matrix(data, columns)

            figure = self.visualization_service.create_heatmap(
                data=corr_matrix,
                title='相关性热力图'
            )

            self._notify_figure(figure)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建热力图时发生错误: {str(e)}")
            return False

    def save_chart(self, figure: Figure, output_path: str, dpi: int = 300, format: str = 'png') -> bool:
        """保存图表"""
        try:
            self.visualization_service.save_chart(figure, output_path, dpi, format)
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"保存图表时发生错误: {str(e)}")
            return False
