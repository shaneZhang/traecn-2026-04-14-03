import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Callable
import os

from ..models.data_manager import DataManager
from ..models.config_manager import ConfigManager
from ..models.logger import get_logger
from ..services.visualization_service import VisualizationService, VisualizationError
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class VisualizationController:
    def __init__(self, data_manager: DataManager, config: Optional[ConfigManager] = None):
        self.data_manager = data_manager
        self.config = config or ConfigManager()
        self.logger = get_logger('VisualizationController')
        self.visualization_service = VisualizationService(data_manager, self.config)
        
        self._canvas: Optional[FigureCanvasTkAgg] = None
        self._toolbar: Optional[NavigationToolbar2Tk] = None
    
    def create_bar_chart(self, dimension: str, value_col: str = 'pre_tax_salary',
                        horizontal: bool = False) -> Optional[Figure]:
        try:
            return self.visualization_service.create_bar_chart(dimension, value_col, horizontal)
        except VisualizationError as e:
            self.logger.error(f"创建柱状图失败: {str(e)}")
            return None
    
    def create_line_chart(self, time_col: str, value_col: str = 'pre_tax_salary') -> Optional[Figure]:
        try:
            return self.visualization_service.create_line_chart(time_col, value_col)
        except VisualizationError as e:
            self.logger.error(f"创建折线图失败: {str(e)}")
            return None
    
    def create_pie_chart(self, dimension: str, value_col: str = 'pre_tax_salary') -> Optional[Figure]:
        try:
            return self.visualization_service.create_pie_chart(dimension, value_col)
        except VisualizationError as e:
            self.logger.error(f"创建饼图失败: {str(e)}")
            return None
    
    def create_scatter_chart(self, x_col: str, y_col: str) -> Optional[Figure]:
        try:
            return self.visualization_service.create_scatter_chart(x_col, y_col)
        except VisualizationError as e:
            self.logger.error(f"创建散点图失败: {str(e)}")
            return None
    
    def create_boxplot(self, dimension: str, value_col: str = 'pre_tax_salary') -> Optional[Figure]:
        try:
            return self.visualization_service.create_boxplot(dimension, value_col)
        except VisualizationError as e:
            self.logger.error(f"创建箱线图失败: {str(e)}")
            return None
    
    def create_histogram(self, column: str, bins: int = 20) -> Optional[Figure]:
        try:
            return self.visualization_service.create_histogram(column, bins)
        except VisualizationError as e:
            self.logger.error(f"创建直方图失败: {str(e)}")
            return None
    
    def create_heatmap(self, columns: list = None) -> Optional[Figure]:
        try:
            return self.visualization_service.create_heatmap(columns)
        except VisualizationError as e:
            self.logger.error(f"创建热力图失败: {str(e)}")
            return None
    
    def embed_chart(self, parent: tk.Widget, figure: Figure) -> Optional[FigureCanvasTkAgg]:
        if figure is None:
            return None
        
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        if self._toolbar:
            self._toolbar.destroy()
            self._toolbar = None
        
        for widget in parent.winfo_children():
            widget.destroy()
        
        self._canvas = FigureCanvasTkAgg(figure, master=parent)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self._toolbar = NavigationToolbar2Tk(self._canvas, parent, pack_toolbar=False)
        self._toolbar.update()
        self._toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        return self._canvas
    
    def save_chart(self) -> bool:
        figure = self.visualization_service.get_current_figure()
        if figure is None:
            messagebox.showwarning('警告', '没有可导出的图表')
            return False
        
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG图片', '*.png'), ('JPG图片', '*.jpg'), ('PDF文档', '*.pdf')]
        )
        
        if not file_path:
            return False
        
        success, message = self.visualization_service.save_chart(file_path)
        
        if success:
            messagebox.showinfo('成功', message)
            return True
        else:
            messagebox.showerror('错误', message)
            return False
    
    def has_data(self) -> bool:
        return self.data_manager.has_data()
    
    def get_current_figure(self) -> Optional[Figure]:
        return self.visualization_service.get_current_figure()
