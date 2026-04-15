from typing import Optional, List, Dict, Tuple
import pandas as pd

from ..models.data_manager import DataManager
from ..models.config_manager import ConfigManager
from ..models.logger import get_logger
from .data_visualizer_service import DataVisualizer, VisualizationError
from matplotlib.figure import Figure


class VisualizationService:
    def __init__(self, data_manager: DataManager, config: Optional[ConfigManager] = None):
        self.data_manager = data_manager
        self.config = config or ConfigManager()
        self.logger = get_logger('VisualizationService')
        self.visualizer = DataVisualizer(self.config)
    
    def create_bar_chart(self, dimension: str, value_col: str = 'pre_tax_salary',
                        horizontal: bool = False) -> Figure:
        data = self.data_manager.get_data()
        if data is None:
            raise VisualizationError("没有可可视化的数据")
        
        try:
            grouped = data.groupby(dimension)[value_col].mean().sort_values(ascending=False)
            return self.visualizer.create_bar_chart(
                x_data=grouped.index.tolist(),
                y_data=grouped.values.tolist(),
                title=f'{dimension} - 平均薪资对比',
                xlabel='平均薪资' if horizontal else dimension,
                ylabel=dimension if horizontal else '平均薪资',
                horizontal=horizontal
            )
        except Exception as e:
            self.logger.exception(f"创建柱状图失败: {str(e)}")
            raise VisualizationError(f"创建柱状图失败: {str(e)}")
    
    def create_line_chart(self, time_col: str, value_col: str = 'pre_tax_salary') -> Figure:
        data = self.data_manager.get_data()
        if data is None:
            raise VisualizationError("没有可可视化的数据")
        
        try:
            trend = data.groupby(time_col)[value_col].agg(['mean', 'median']).reset_index()
            return self.visualizer.create_line_chart(
                x_data=trend[time_col].tolist(),
                y_data_list=[trend['mean'].tolist(), trend['median'].tolist()],
                title='薪资趋势变化',
                xlabel=time_col,
                ylabel='薪资',
                labels=['平均薪资', '中位薪资']
            )
        except Exception as e:
            self.logger.exception(f"创建折线图失败: {str(e)}")
            raise VisualizationError(f"创建折线图失败: {str(e)}")
    
    def create_pie_chart(self, dimension: str, value_col: str = 'pre_tax_salary') -> Figure:
        data = self.data_manager.get_data()
        if data is None:
            raise VisualizationError("没有可可视化的数据")
        
        try:
            grouped = data.groupby(dimension)[value_col].sum().sort_values(ascending=False)
            top_n = min(8, len(grouped))
            grouped = grouped.head(top_n)
            return self.visualizer.create_pie_chart(
                data=grouped.values.tolist(),
                labels=grouped.index.tolist(),
                title=f'{dimension} - 薪资占比'
            )
        except Exception as e:
            self.logger.exception(f"创建饼图失败: {str(e)}")
            raise VisualizationError(f"创建饼图失败: {str(e)}")
    
    def create_scatter_chart(self, x_col: str, y_col: str) -> Figure:
        data = self.data_manager.get_data()
        if data is None:
            raise VisualizationError("没有可可视化的数据")
        
        try:
            valid_data = data[[x_col, y_col]].dropna()
            return self.visualizer.create_scatter_chart(
                x_data=valid_data[x_col].tolist(),
                y_data=valid_data[y_col].tolist(),
                title=f'{x_col} 与 {y_col} 关系',
                xlabel=x_col,
                ylabel=y_col
            )
        except Exception as e:
            self.logger.exception(f"创建散点图失败: {str(e)}")
            raise VisualizationError(f"创建散点图失败: {str(e)}")
    
    def create_boxplot(self, dimension: str, value_col: str = 'pre_tax_salary') -> Figure:
        data = self.data_manager.get_data()
        if data is None:
            raise VisualizationError("没有可可视化的数据")
        
        try:
            box_data = {}
            for cat in data[dimension].unique():
                values = data[data[dimension] == cat][value_col].dropna().values
                if len(values) > 0:
                    box_data[str(cat)] = values
            
            return self.visualizer.create_boxplot(
                data_dict=box_data,
                title=f'{dimension} - 薪资分布',
                xlabel=dimension,
                ylabel='薪资'
            )
        except Exception as e:
            self.logger.exception(f"创建箱线图失败: {str(e)}")
            raise VisualizationError(f"创建箱线图失败: {str(e)}")
    
    def create_histogram(self, column: str, bins: int = 20) -> Figure:
        data = self.data_manager.get_data()
        if data is None:
            raise VisualizationError("没有可可视化的数据")
        
        try:
            col_data = data[column].dropna().values
            return self.visualizer.create_histogram(
                data=col_data,
                bins=bins,
                title=f'{column} 分布直方图',
                xlabel=column
            )
        except Exception as e:
            self.logger.exception(f"创建直方图失败: {str(e)}")
            raise VisualizationError(f"创建直方图失败: {str(e)}")
    
    def create_heatmap(self, columns: Optional[List[str]] = None) -> Figure:
        data = self.data_manager.get_data()
        if data is None:
            raise VisualizationError("没有可可视化的数据")
        
        try:
            import numpy as np
            if columns is None:
                columns = data.select_dtypes(include=[np.number]).columns.tolist()
            
            corr_matrix = data[columns].corr().round(3)
            return self.visualizer.create_heatmap(
                data=corr_matrix,
                title='相关性热力图'
            )
        except Exception as e:
            self.logger.exception(f"创建热力图失败: {str(e)}")
            raise VisualizationError(f"创建热力图失败: {str(e)}")
    
    def save_chart(self, output_path: str, dpi: int = 300) -> Tuple[bool, str]:
        try:
            self.visualizer.save_chart(output_path, dpi)
            self.logger.info(f"图表已保存到: {output_path}")
            return True, f"图表已保存到: {output_path}"
        except VisualizationError as e:
            self.logger.error(f"保存图表失败: {str(e)}")
            return False, str(e)
    
    def get_current_figure(self) -> Optional[Figure]:
        return self.visualizer.get_current_figure()
