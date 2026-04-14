import pandas as pd
import os
from typing import Optional, List, Dict, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox


class DataLoader:
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        self.sheet_names: List[str] = []
        
        self.field_mapping = {
            '姓名': 'name',
            '性别': 'gender',
            '年龄': 'age',
            '学历': 'education',
            '工作年限': 'work_years',
            '所在行业': 'industry',
            '岗位类型': 'position_type',
            '职级': 'level',
            '基本工资': 'base_salary',
            '绩效奖金': 'performance_bonus',
            '补贴总和': 'allowance',
            '税前薪资': 'pre_tax_salary',
            '税后薪资': 'post_tax_salary',
            '所属企业规模': 'company_size',
            '入职年份': 'join_year'
        }
    
    def select_file(self) -> Optional[str]:
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title='选择Excel文件',
            filetypes=[('Excel文件', '*.xlsx *.xls'), ('所有文件', '*.*')]
        )
        
        if file_path:
            self.file_path = file_path
            return file_path
        return None
    
    def select_folder(self) -> Optional[str]:
        root = tk.Tk()
        root.withdraw()
        
        folder_path = filedialog.askdirectory(title='选择文件夹')
        
        if folder_path:
            return folder_path
        return None
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        try:
            xl_file = pd.ExcelFile(file_path)
            self.sheet_names = xl_file.sheet_names
            return self.sheet_names
        except Exception as e:
            messagebox.showerror('错误', f'读取工作表失败: {str(e)}')
            return []
    
    def load_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        try:
            if sheet_name:
                self.data = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                self.data = pd.read_excel(file_path)
            
            self.file_path = file_path
            self._auto_map_fields()
            return self.data
            
        except Exception as e:
            messagebox.showerror('错误', f'读取Excel文件失败: {str(e)}')
            return None
    
    def load_multiple_files(self, file_paths: List[str]) -> Optional[pd.DataFrame]:
        try:
            dfs = []
            for file_path in file_paths:
                df = pd.read_excel(file_path)
                dfs.append(df)
            
            if dfs:
                self.data = pd.concat(dfs, ignore_index=True)
                self._auto_map_fields()
                return self.data
            return None
            
        except Exception as e:
            messagebox.showerror('错误', f'批量导入失败: {str(e)}')
            return None
    
    def load_folder(self, folder_path: str) -> Optional[pd.DataFrame]:
        try:
            excel_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(('.xlsx', '.xls')):
                        excel_files.append(os.path.join(root, file))
            
            if not excel_files:
                messagebox.showwarning('警告', '文件夹中没有找到Excel文件')
                return None
            
            return self.load_multiple_files(excel_files)
            
        except Exception as e:
            messagebox.showerror('错误', f'读取文件夹失败: {str(e)}')
            return None
    
    def _auto_map_fields(self):
        if self.data is None:
            return
        
        new_columns = {}
        for col in self.data.columns:
            col_stripped = col.strip()
            col_lower = col_stripped.lower()
            
            # 检查中文列名映射
            for chinese, english in self.field_mapping.items():
                if chinese == col_stripped or col_lower == chinese.lower():
                    new_columns[col] = english
                    break
            else:
                # 检查是否已经是英文列名（反向查找）
                for chinese, english in self.field_mapping.items():
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
        
        numeric_cols = ['age', 'work_years', 'base_salary', 'performance_bonus', 
                       'allowance', 'pre_tax_salary', 'post_tax_salary', 'join_year']
        
        for col in numeric_cols:
            if col in self.data.columns:
                non_numeric = pd.to_numeric(self.data[col], errors='coerce')
                null_count = non_numeric.isnull().sum()
                if null_count > 0:
                    errors.append(f"字段 '{col}' 存在 {null_count} 个无效数值")
        
        if errors:
            return False, errors
        return True, []
    
    def get_field_mapping(self) -> Dict[str, str]:
        return self.field_mapping.copy()
    
    def apply_field_mapping(self, mapping: Dict[str, str]):
        if self.data is not None and mapping:
            self.data.rename(columns=mapping, inplace=True)
    
    def export_data(self, output_path: str, format: str = 'excel') -> bool:
        if self.data is None:
            messagebox.showwarning('警告', '没有可导出的数据')
            return False
        
        try:
            if format == 'excel':
                self.data.to_excel(output_path, index=False)
            elif format == 'csv':
                self.data.to_csv(output_path, index=False, encoding='utf-8-sig')
            else:
                messagebox.showerror('错误', f'不支持的格式: {format}')
                return False
            
            messagebox.showinfo('成功', f'数据已导出到: {output_path}')
            return True
            
        except Exception as e:
            messagebox.showerror('错误', f'导出失败: {str(e)}')
            return False
