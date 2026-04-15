import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Callable

from ..models.data_manager import DataManager, DataEvent, DataEventType
from ..models.config_manager import ConfigManager
from ..models.logger import get_logger
from ..services.data_service import DataService
from ..services.processing_service import ProcessingService


class DataController:
    def __init__(self, data_manager: DataManager, config: Optional[ConfigManager] = None):
        self.data_manager = data_manager
        self.config = config or ConfigManager()
        self.logger = get_logger('DataController')
        
        self.data_service = DataService(data_manager, self.config)
        self.processing_service = ProcessingService(data_manager, self.config)
        
        self._status_callback: Optional[Callable] = None
        self._info_callback: Optional[Callable] = None
        self._root: Optional[tk.Tk] = None
    
    def set_root(self, root: tk.Tk) -> None:
        self._root = root
    
    def set_status_callback(self, callback: Callable) -> None:
        self._status_callback = callback
    
    def set_info_callback(self, callback: Callable) -> None:
        self._info_callback = callback
    
    def _update_status(self, message: str) -> None:
        if self._status_callback:
            self._status_callback(message)
    
    def _update_info(self) -> None:
        if self._info_callback:
            info = self.data_manager.get_data_info()
            self._info_callback(info)
    
    def select_and_load_file(self) -> bool:
        if self._root:
            file_path = filedialog.askopenfilename(
                parent=self._root,
                title='选择Excel文件',
                filetypes=[('Excel文件', '*.xlsx *.xls'), ('所有文件', '*.*')]
            )
        else:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title='选择Excel文件',
                filetypes=[('Excel文件', '*.xlsx *.xls'), ('所有文件', '*.*')]
            )
        
        if not file_path:
            return False
        
        self._update_status(f'正在加载: {file_path}')
        
        success, message = self.data_service.load_file(file_path)
        
        if success:
            self._update_status('数据加载成功')
            self._update_info()
            messagebox.showinfo('成功', message)
            return True
        else:
            self._update_status('数据加载失败')
            messagebox.showerror('错误', message)
            return False
    
    def select_and_load_folder(self) -> bool:
        if self._root:
            folder_path = filedialog.askdirectory(parent=self._root, title='选择文件夹')
        else:
            root = tk.Tk()
            root.withdraw()
            folder_path = filedialog.askdirectory(title='选择文件夹')
        
        if not folder_path:
            return False
        
        self._update_status(f'正在加载文件夹: {folder_path}')
        
        success, message = self.data_service.load_folder(folder_path)
        
        if success:
            self._update_status('数据加载成功')
            self._update_info()
            messagebox.showinfo('成功', message)
            return True
        else:
            self._update_status('数据加载失败')
            messagebox.showerror('错误', message)
            return False
    
    def export_data(self) -> bool:
        data = self.data_manager.get_data()
        if data is None:
            messagebox.showwarning('警告', '没有可导出的数据')
            return False
        
        if self._root:
            file_path = filedialog.asksaveasfilename(
                parent=self._root,
                defaultextension='.xlsx',
                filetypes=[('Excel文件', '*.xlsx'), ('CSV文件', '*.csv')]
            )
        else:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel文件', '*.xlsx'), ('CSV文件', '*.csv')]
            )
        
        if not file_path:
            return False
        
        format_type = 'csv' if file_path.endswith('.csv') else 'excel'
        success, message = self.data_service.export_data(file_path, format_type)
        
        if success:
            messagebox.showinfo('成功', message)
            return True
        else:
            messagebox.showerror('错误', message)
            return False
    
    def clean_duplicates(self) -> bool:
        success, message, count = self.processing_service.remove_duplicates()
        
        if success:
            self._update_info()
            messagebox.showinfo('完成', message)
            return True
        else:
            messagebox.showerror('错误', message)
            return False
    
    def clean_missing_values(self, strategy: str = 'drop') -> bool:
        success, message = self.processing_service.handle_missing_values(strategy)
        
        if success:
            self._update_info()
            messagebox.showinfo('完成', message)
            return True
        else:
            messagebox.showerror('错误', message)
            return False
    
    def remove_outliers(self, column: str) -> bool:
        success, message, count = self.processing_service.remove_outliers(column)
        
        if success:
            self._update_info()
            messagebox.showinfo('完成', message)
            return True
        else:
            messagebox.showerror('错误', message)
            return False
    
    def create_age_group(self, age_column: str = 'age') -> bool:
        success, message = self.processing_service.create_age_group(age_column)
        
        if success:
            self._update_info()
            messagebox.showinfo('完成', message)
            return True
        else:
            messagebox.showwarning('警告', message)
            return False
    
    def create_salary_group(self, salary_column: str = 'pre_tax_salary') -> bool:
        success, message = self.processing_service.create_salary_group(salary_column)
        
        if success:
            self._update_info()
            messagebox.showinfo('完成', message)
            return True
        else:
            messagebox.showwarning('警告', message)
            return False
    
    def create_experience_group(self, years_column: str = 'work_years') -> bool:
        success, message = self.processing_service.create_experience_group(years_column)
        
        if success:
            self._update_info()
            messagebox.showinfo('完成', message)
            return True
        else:
            messagebox.showwarning('警告', message)
            return False
    
    def reset_data(self) -> bool:
        success, message = self.processing_service.reset_data()
        
        if success:
            self._update_info()
            messagebox.showinfo('完成', message)
            return True
        else:
            messagebox.showwarning('警告', message)
            return False
    
    def has_data(self) -> bool:
        return self.data_manager.has_data()
    
    def get_categorical_columns(self) -> list:
        return self.data_manager.get_categorical_columns()
    
    def get_numeric_columns(self) -> list:
        return self.data_manager.get_numeric_columns()
    
    def get_column_names(self) -> list:
        return self.data_manager.get_column_names()
