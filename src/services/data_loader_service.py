import pandas as pd
import os
from typing import Optional, List, Dict, Tuple
from ..models.config_manager import ConfigManager


class DataLoadError(Exception):
    pass


class DataValidationError(Exception):
    pass


class DataLoader:
    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()
        self.data: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        self.sheet_names: List[str] = []
    
    def load_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        if not os.path.exists(file_path):
            raise DataLoadError(f"文件不存在: {file_path}")
        
        try:
            if sheet_name:
                self.data = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                self.data = pd.read_excel(file_path)
            
            self.file_path = file_path
            self._auto_map_fields()
            return self.data
            
        except Exception as e:
            raise DataLoadError(f"读取Excel文件失败: {str(e)}")
    
    def load_multiple_files(self, file_paths: List[str]) -> pd.DataFrame:
        try:
            dfs = []
            for file_path in file_paths:
                if os.path.exists(file_path):
                    df = pd.read_excel(file_path)
                    dfs.append(df)
            
            if dfs:
                self.data = pd.concat(dfs, ignore_index=True)
                self._auto_map_fields()
                return self.data
            
            raise DataLoadError("没有有效的数据文件")
            
        except DataLoadError:
            raise
        except Exception as e:
            raise DataLoadError(f"批量导入失败: {str(e)}")
    
    def load_folder(self, folder_path: str) -> pd.DataFrame:
        if not os.path.isdir(folder_path):
            raise DataLoadError(f"文件夹不存在: {folder_path}")
        
        excel_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.xlsx', '.xls')):
                    excel_files.append(os.path.join(root, file))
        
        if not excel_files:
            raise DataLoadError("文件夹中没有找到Excel文件")
        
        return self.load_multiple_files(excel_files)
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        try:
            xl_file = pd.ExcelFile(file_path)
            self.sheet_names = xl_file.sheet_names
            return self.sheet_names
        except Exception as e:
            raise DataLoadError(f"读取工作表失败: {str(e)}")
    
    def _auto_map_fields(self) -> None:
        if self.data is None:
            return
        
        field_mapping = self.config.get_field_mapping()
        new_columns = {}
        
        for col in self.data.columns:
            col_stripped = col.strip()
            col_lower = col_stripped.lower()
            
            for chinese, english in field_mapping.items():
                if chinese == col_stripped or col_lower == chinese.lower():
                    new_columns[col] = english
                    break
            else:
                for chinese, english in field_mapping.items():
                    if english.lower() == col_lower:
                        new_columns[col] = english
                        break
        
        if new_columns:
            self.data.rename(columns=new_columns, inplace=True)
    
    def get_preview(self, n: int = 10) -> Optional[pd.DataFrame]:
        if self.data is None:
            return None
        return self.data.head(n)
    
    def get_data_info(self) -> Dict:
        if self.data is None:
            return {}
        
        return {
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'column_names': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict()
        }
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        if self.data is None:
            return False, ['没有加载数据']
        
        errors = []
        numeric_fields = self.config.get('data.numeric_fields', [])
        
        for col in numeric_fields:
            if col in self.data.columns:
                non_numeric = pd.to_numeric(self.data[col], errors='coerce')
                null_count = non_numeric.isnull().sum()
                original_nulls = self.data[col].isnull().sum()
                invalid_count = null_count - original_nulls
                
                if invalid_count > 0:
                    errors.append(f"字段 '{col}' 存在 {invalid_count} 个无效数值")
        
        if errors:
            return False, errors
        return True, []
    
    def export_data(self, data: pd.DataFrame, output_path: str, format: str = 'excel') -> bool:
        if data is None or len(data) == 0:
            raise DataValidationError("没有可导出的数据")
        
        try:
            if format == 'excel' or output_path.endswith(('.xlsx', '.xls')):
                data.to_excel(output_path, index=False)
            elif format == 'csv' or output_path.endswith('.csv'):
                data.to_csv(output_path, index=False, encoding='utf-8-sig')
            else:
                raise DataValidationError(f"不支持的格式: {format}")
            
            return True
            
        except DataValidationError:
            raise
        except Exception as e:
            raise DataLoadError(f"导出失败: {str(e)}")
    
    def get_current_data(self) -> Optional[pd.DataFrame]:
        return self.data
