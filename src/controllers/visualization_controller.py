import tkinter as tk
from tkinter import filedialog
from typing import Optional
from src.services import VisualizationService
from src.models import Logger


class VisualizationController:
    def __init__(self):
        self.visualization_service = VisualizationService()
        self.logger = Logger()

    def has_data(self) -> bool:
        try:
            self.visualization_service._get_data()
            return True
        except Exception:
            return False

    def create_chart(self, chart_type: str, dimension: str, salary_col: str, parent):
        try:
            if chart_type == 'bar':
                self.visualization_service.create_bar_chart(dimension, salary_col)
            elif chart_type == 'horizontal':
                self.visualization_service.create_bar_chart(dimension, salary_col, horizontal=True)
            elif chart_type == 'pie':
                self.visualization_service.create_pie_chart(dimension, salary_col)
            elif chart_type == 'line':
                self.visualization_service.create_line_chart('join_year', salary_col)
            elif chart_type == 'scatter':
                self.visualization_service.create_scatter_chart('work_years', salary_col)
            elif chart_type == 'boxplot':
                self.visualization_service.create_boxplot(dimension, salary_col)
            elif chart_type == 'histogram':
                self.visualization_service.create_histogram(salary_col)

            self.visualization_service.embed_in_tkinter(parent)
            return True
        except Exception as e:
            self.logger.error(f"图表生成失败: {str(e)}")
            raise

    def export_chart(self, parent_window=None) -> bool:
        if not self.visualization_service.get_current_figure():
            return False

        file_path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG图片', '*.png'), ('JPG图片', '*.jpg'), ('PDF文档', '*.pdf')],
            parent=parent_window
        )

        if file_path:
            try:
                fmt = file_path.split('.')[-1]
                return self.visualization_service.save_chart(file_path, format=fmt)
            except Exception as e:
                self.logger.error(f"导出图表失败: {str(e)}")
                raise
        return False

    def get_current_figure(self):
        return self.visualization_service.get_current_figure()
