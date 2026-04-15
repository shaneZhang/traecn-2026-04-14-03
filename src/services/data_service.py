import pandas as pd
import os
from typing import Optional, List, Dict, Tuple
from pathlib import Path

from ..utils.exceptions import DataLoadError
from ..models.config_manager import ConfigManager
from ..models.logger import Logger


class DataService:
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager.get_instance()
        self.logger = Logger.get_instance()
        self.field_mapping = self.config.get_field_mapping()

    def load_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        try:
            if sheet_name:
                data = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                data = pd.read_excel(file_path)
            
            self._auto_map_fields(data)
            self.logger.info(f"成功加载Excel文件: {file_path}, 记录数: {len(data)}")
            return data
            
        except Exception as e:
            self.logger.error(f"读取Excel文件失败: {str(e)}")
            raise DataLoadError(f"读取Excel文件失败: {str(e)}")

    def load_multiple_files(self, file_paths: List[str]) -> pd.DataFrame:
        try:
            dfs = []
            for file_path in file_paths:
                df = pd.read_excel(file_path)
                dfs.append(df)
            
            if not dfs:
                raise DataLoadError("没有可加载的文件")
            
            data = pd.concat(dfs, ignore_index=True)
            self._auto_map_fields(data)
            self.logger.info(f"成功批量加载 {len(file_paths)} 个文件, 总记录数: {len(data)}")
            return data
            
        except Exception as e:
            self.logger.error(f"批量导入失败: {str(e)}")
            raise DataLoadError(f"批量导入失败: {str(e)}")

    def load_folder(self, folder_path: str) -> pd.DataFrame:
        try:
            excel_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(('.xlsx', '.xls')):
                        excel_files.append(os.path.join(root, file))
            
            if not excel_files:
                raise DataLoadError(f"文件夹中没有找到Excel文件: {folder_path}")
            
            return self.load_multiple_files(excel_files)
            
        except Exception as e:
            self.logger.error(f"读取文件夹失败: {str(e)}")
            raise DataLoadError(f"读取文件夹失败: {str(e)}")

    def get_sheet_names(self, file_path: str) -> List[str]:
        try:
            xl_file = pd.ExcelFile(file_path)
            return xl_file.sheet_names
        except Exception as e:
            self.logger.error(f"读取工作表失败: {str(e)}")
            raise DataLoadError(f"读取工作表失败: {str(e)}")

    def _auto_map_fields(self, data: pd.DataFrame):
        new_columns = {}
        for col in data.columns:
            col_stripped = col.strip()
            col_lower = col_stripped.lower()
            
            for chinese, english in self.field_mapping.items():
                if chinese == col_stripped or col_lower == chinese.lower():
                    new_columns[col] = english
                    break
            else:
                for chinese, english in self.field_mapping.items():
                    if english.lower() == col_lower:
                        new_columns[col] = english
                        break
        
        if new_columns:
            data.rename(columns=new_columns, inplace=True)
            self.logger.info(f"自动映射字段: {new_columns}")

    def export_data(self, data: pd.DataFrame, output_path: str, format: str = 'excel') -> bool:
        try:
            if format == 'excel':
                data.to_excel(output_path, index=False)
            elif format == 'csv':
                data.to_csv(output_path, index=False, encoding='utf-8-sig')
            else:
                raise DataLoadError(f"不支持的格式: {format}")
            
            self.logger.info(f"数据已导出到: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出失败: {str(e)}")
            raise DataLoadError(f"导出失败: {str(e)}")

    def validate_data(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        
        numeric_cols = ['age', 'work_years', 'base_salary', 'performance_bonus', 
                       'allowance', 'pre_tax_salary', 'post_tax_salary', 'join_year']
        
        for col in numeric_cols:
            if col in data.columns:
                non_numeric = pd.to_numeric(data[col], errors='coerce')
                null_count = non_numeric.isnull().sum()
                if null_count > 0:
                    errors.append(f"字段 '{col}' 存在 {null_count} 个无效数值")
        
        if errors:
            return False, errors
        return True, []

    def get_data_info(self, data: pd.DataFrame) -> Dict:
        return {
            'rows': len(data),
            'columns': len(data.columns),
            'column_names': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'missing_values': data.isnull().sum().to_dict()
        }

    def get_preview(self, data: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return data.head(n)
