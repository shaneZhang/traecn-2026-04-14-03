from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from typing import List, Dict, Tuple, Optional
import pandas as pd
from src.models import DataManager, ConfigManager, Logger
from src.core import VisualizerCore
from src.core.exceptions import VisualizationError


class VisualizationService:
    def __init__(self):
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.visualizer_core = VisualizerCore()
        self.current_figure: Optional[Figure] = None
        self.canvas = None
        self.toolbar = None

        viz_config = self.config_manager.get('visualization', {})
        if viz_config:
            self.visualizer_core.config.update(viz_config)

    def _get_data(self) -> pd.DataFrame:
        if not self.data_manager.has_data:
            raise VisualizationError("没有可可视化的数据")
        return self.data_manager.get_data()

    def create_figure(self, figsize: Tuple[float, float] = None) -> Figure:
        if figsize is None:
            figsize = self.config_manager.get('visualization.figure_size', (10, 6))
        self.current_figure = self.visualizer_core.create_figure(figsize)
        return self.current_figure

    def create_bar_chart(self, dimension: str, value_col: str,
                         title: Optional[str] = None,
                         horizontal: bool = False) -> Figure:
        data = self._get_data()
        grouped = data.groupby(dimension)[value_col].mean().sort_values(ascending=False)

        if title is None:
            title = f'{dimension} - 平均薪资对比'

        self.current_figure = self.visualizer_core.create_bar_chart(
            self.create_figure(),
            x_data=grouped.index.tolist(),
            y_data=grouped.values.tolist(),
            title=title,
            xlabel='平均薪资' if horizontal else dimension,
            ylabel=dimension if horizontal else '平均薪资',
            horizontal=horizontal
        )
        self.logger.info(f"生成柱状图: {dimension} vs {value_col}")
        return self.current_figure

    def create_pie_chart(self, dimension: str, value_col: str,
                         title: Optional[str] = None, top_n: int = 8) -> Figure:
        data = self._get_data()
        grouped = data.groupby(dimension)[value_col].sum().sort_values(ascending=False)
        grouped = grouped.head(top_n)

        if title is None:
            title = f'{dimension} - 薪资占比'

        self.current_figure = self.visualizer_core.create_pie_chart(
            self.create_figure(),
            data=grouped.values.tolist(),
            labels=grouped.index.tolist(),
            title=title
        )
        self.logger.info(f"生成饼图: {dimension}")
        return self.current_figure

    def create_line_chart(self, time_col: str, value_col: str,
                          title: Optional[str] = None) -> Figure:
        data = self._get_data()
        if time_col not in data.columns:
            raise VisualizationError(f"数据中没有 {time_col} 字段")

        trend = data.groupby(time_col)[value_col].mean().reset_index()

        if title is None:
            title = '薪资趋势变化'

        self.current_figure = self.visualizer_core.create_line_chart(
            self.create_figure(),
            x_data=trend[time_col].tolist(),
            y_data_list=[trend[value_col].tolist()],
            title=title,
            xlabel=time_col,
            ylabel='平均薪资'
        )
        self.logger.info(f"生成趋势图: {time_col}")
        return self.current_figure

    def create_scatter_chart(self, x_col: str, y_col: str,
                             title: Optional[str] = None) -> Figure:
        data = self._get_data()
        if x_col not in data.columns:
            raise VisualizationError(f"数据中没有 {x_col} 字段")

        valid_data = data[[x_col, y_col]].dropna()

        if title is None:
            title = f'{x_col}与{y_col}关系'

        self.current_figure = self.visualizer_core.create_scatter_chart(
            self.create_figure(),
            x_data=valid_data[x_col].tolist(),
            y_data=valid_data[y_col].tolist(),
            title=title,
            xlabel=x_col,
            ylabel=y_col
        )
        self.logger.info(f"生成散点图: {x_col} vs {y_col}")
        return self.current_figure

    def create_boxplot(self, dimension: str, value_col: str,
                       title: Optional[str] = None) -> Figure:
        data = self._get_data()
        from src.services import AnalysisService
        analysis_service = AnalysisService()
        box_data = analysis_service.get_boxplot_data(dimension, value_col)

        box_data_dict = {k: [v['min'], v['q1'], v['median'], v['q3'], v['max']]
                         for k, v in box_data.items()}

        if title is None:
            title = f'{dimension} - 薪资分布'

        self.current_figure = self.visualizer_core.create_boxplot(
            self.create_figure(),
            data_dict={k: data[data[dimension] == k][value_col].dropna().values
                       for k in box_data.keys()},
            title=title,
            xlabel=dimension,
            ylabel='薪资'
        )
        self.logger.info(f"生成箱线图: {dimension}")
        return self.current_figure

    def create_histogram(self, column: str, bins: int = 20,
                         title: Optional[str] = None) -> Figure:
        data = self._get_data()
        hist_data = data[column].dropna().values

        if title is None:
            title = f'{column}分布直方图'

        self.current_figure = self.visualizer_core.create_histogram(
            self.create_figure(),
            data=hist_data,
            bins=bins,
            title=title,
            xlabel=column
        )
        self.logger.info(f"生成直方图: {column}")
        return self.current_figure

    def embed_in_tkinter(self, parent):
        if self.current_figure is None:
            self.create_figure()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None

        self.canvas = FigureCanvasTkAgg(self.current_figure, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, parent, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        return self.canvas

    def save_chart(self, output_path: str, dpi: int = 300, format: str = 'png') -> bool:
        if self.current_figure is None:
            raise VisualizationError("没有可保存的图表")
        success = self.visualizer_core.save_figure(self.current_figure, output_path, dpi, format)
        if success:
            self.logger.info(f"图表已保存到: {output_path}")
        return success

    def get_current_figure(self) -> Optional[Figure]:
        return self.current_figure
