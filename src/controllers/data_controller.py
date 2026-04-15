import tkinter as tk
from tkinter import filedialog
from typing import Optional, Dict, Any
from src.services import DataService, ProcessingService
from src.models import DataManager, Logger, DataEventType


class DataController:
    def __init__(self):
        self.data_service = DataService()
        self.processing_service = ProcessingService()
        self.data_manager = DataManager()
        self.logger = Logger()
        self._callbacks = {}

        self.data_manager.subscribe(DataEventType.LOADED, self._on_data_loaded)
        self.data_manager.subscribe(DataEventType.UPDATED, self._on_data_updated)
        self.data_manager.subscribe(DataEventType.RESET, self._on_data_reset)

    def register_callback(self, event: str, callback):
        self._callbacks[event] = callback

    def _trigger_callback(self, event: str, *args, **kwargs):
        if event in self._callbacks:
            self._callbacks[event](*args, **kwargs)

    def _on_data_loaded(self, event):
        self._trigger_callback('data_changed', event.metadata)

    def _on_data_updated(self, event):
        self._trigger_callback('data_changed', event.metadata)

    def _on_data_reset(self, event):
        self._trigger_callback('data_changed', event.metadata)

    def load_file(self, parent_window=None) -> bool:
        file_path = filedialog.askopenfilename(
            title='选择Excel文件',
            filetypes=[('Excel文件', '*.xlsx *.xls'), ('所有文件', '*.*')],
            parent=parent_window
        )

        if file_path:
            try:
                return self.data_service.load_excel_file(file_path)
            except Exception as e:
                self.logger.error(f"加载文件失败: {str(e)}")
                raise
        return False

    def load_folder(self, parent_window=None) -> bool:
        folder_path = filedialog.askdirectory(
            title='选择文件夹',
            parent=parent_window
        )

        if folder_path:
            try:
                return self.data_service.load_folder(folder_path)
            except Exception as e:
                self.logger.error(f"加载文件夹失败: {str(e)}")
                raise
        return False

    def export_data(self, parent_window=None) -> bool:
        if not self.has_data():
            return False

        file_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel文件', '*.xlsx'), ('CSV文件', '*.csv')],
            parent=parent_window
        )

        if file_path:
            try:
                fmt = 'csv' if file_path.endswith('.csv') else 'excel'
                return self.data_service.export_data(file_path, fmt)
            except Exception as e:
                self.logger.error(f"导出数据失败: {str(e)}")
                raise
        return False

    def has_data(self) -> bool:
        return self.data_service.has_data()

    def get_data_info(self) -> Dict[str, Any]:
        return self.data_service.get_data_info()

    def get_data(self):
        return self.data_service.get_data()

    def get_categorical_columns(self):
        return self.data_service.get_categorical_columns()

    def get_numeric_columns(self):
        return self.data_service.get_numeric_columns()

    def get_salary_columns(self) -> list:
        numeric_cols = self.get_numeric_columns()
        salary_candidates = ['pre_tax_salary', 'post_tax_salary', 'base_salary', 'total_salary']
        available = [col for col in numeric_cols
                     if col.lower() in [s.lower() for s in salary_candidates]]
        return available if available else numeric_cols

    def remove_duplicates(self) -> int:
        return self.processing_service.remove_duplicates()

    def handle_missing_values(self, strategy: str) -> Dict[str, int]:
        return self.processing_service.handle_missing_values(strategy=strategy)

    def remove_outliers(self, column: str) -> int:
        return self.processing_service.remove_outliers(column)

    def create_age_group(self) -> bool:
        return self.processing_service.create_age_group()

    def create_salary_group(self, salary_column: str) -> bool:
        return self.processing_service.create_salary_group(salary_column)

    def create_work_experience_group(self) -> bool:
        return self.processing_service.create_work_experience_group()

    def reset_data(self):
        self.processing_service.reset_data()
