import pandas as pd
from typing import Optional, List, Dict
from src.models import DataManager, ConfigManager, Logger
from src.core import DataLoaderCore
from src.core.exceptions import DataLoadError


class DataService:
    def __init__(self):
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.loader_core = DataLoaderCore(
            field_mapping=self.config_manager.get('field_mapping')
        )

    def load_excel_file(self, file_path: str) -> bool:
        try:
            self.logger.info(f"开始加载文件: {file_path}")
            data = self.loader_core.load_excel(file_path)
            self.data_manager.set_data(data, source=file_path)
            self.logger.info(f"数据加载成功，共 {len(data)} 条记录")
            return True
        except DataLoadError as e:
            self.logger.error(f"数据加载失败: {str(e)}")
            raise

    def load_folder(self, folder_path: str) -> bool:
        try:
            self.logger.info(f"开始加载文件夹: {folder_path}")
            data = self.loader_core.load_folder(folder_path)
            self.data_manager.set_data(data, source=folder_path)
            self.logger.info(f"文件夹加载成功，共 {len(data)} 条记录")
            return True
        except DataLoadError as e:
            self.logger.error(f"文件夹加载失败: {str(e)}")
            raise

    def export_data(self, output_path: str, format: str = 'excel') -> bool:
        if not self.data_manager.has_data:
            raise DataLoadError("没有可导出的数据")

        data = self.data_manager.get_data()
        try:
            self.logger.info(f"导出数据到: {output_path}")
            self.loader_core.export_data(data, output_path, format)
            self.logger.info("数据导出成功")
            return True
        except DataLoadError as e:
            self.logger.error(f"数据导出失败: {str(e)}")
            raise

    def get_data_info(self) -> Dict:
        return self.data_manager.get_data_info()

    def has_data(self) -> bool:
        return self.data_manager.has_data

    def get_data(self) -> Optional[pd.DataFrame]:
        return self.data_manager.get_data()

    def get_column_names(self) -> List[str]:
        return self.data_manager.get_column_names()

    def get_numeric_columns(self) -> List[str]:
        return self.data_manager.get_numeric_columns()

    def get_categorical_columns(self) -> List[str]:
        return self.data_manager.get_categorical_columns()

    def validate_data(self) -> tuple[bool, List[str]]:
        if not self.data_manager.has_data:
            return False, ['没有加载数据']
        data = self.data_manager.get_data()
        self.loader_core.data = data
        return self.loader_core.validate_data()
