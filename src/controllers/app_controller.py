import tkinter as tk
from typing import Optional
from src.models import Logger, ConfigManager, DataManager
from .data_controller import DataController
from .analysis_controller import AnalysisController
from .visualization_controller import VisualizationController


class AppController:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.logger = Logger()
        self.config_manager = ConfigManager()
        self.data_manager = DataManager()

        self.data_controller = DataController()
        self.analysis_controller = AnalysisController()
        self.visualization_controller = VisualizationController()

        self.status_callback = None
        self.data_controller.register_callback('data_changed', self._on_data_changed)

        self.logger.info("应用控制器初始化完成")

    def _on_data_changed(self, metadata):
        if self.status_callback:
            self.status_callback(f"数据已更新: {metadata.get('rows', 0)} 条记录")

    def set_status_callback(self, callback):
        self.status_callback = callback

    def update_status(self, message: str):
        if self.status_callback:
            self.status_callback(message)

    def get_app_title(self) -> str:
        return self.config_manager.get('app.title', '园区白领薪资数据分析工具')

    def get_window_size(self) -> str:
        return self.config_manager.get('app.window_size', '1400x800')

    def show_help(self):
        help_text = '''
数据导入:
  - 支持打开单个Excel文件或整个文件夹
  - 自动识别常见字段名称并映射

数据处理:
  - 删除重复数据、缺失值处理
  - 数据分组（年龄、薪资、工作年限）
  - 异常值检测与处理

分析功能:
  - 描述性统计（均值、中位数、标准差等）
  - 频率分析、交叉分析
  - 相关性分析

可视化:
  - 柱状图、折线图、饼图
  - 散点图、箱线图、直方图
  - 支持图表导出
'''
        from tkinter import messagebox
        messagebox.showinfo('使用说明', help_text)

    def show_about(self):
        version = self.config_manager.get('app.version', '2.0.0')
        from tkinter import messagebox
        messagebox.showinfo(
            '关于',
            f'园区白领薪资数据分析工具\n\n版本: {version}\n\n架构: MVC + 服务层\n基于 Python + Pandas + Matplotlib 构建'
        )

    def exit(self):
        self.logger.info("应用退出")
        self.root.quit()
