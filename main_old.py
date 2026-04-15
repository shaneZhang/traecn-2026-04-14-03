import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import DataLoader
from src.data_processor import DataProcessor
from src.data_analyzer import DataAnalyzer
from src.visualizer import DataVisualizer


class SalaryAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title('园区白领薪资数据分析工具')
        self.root.geometry('1400x800')
        
        self.data_loader = DataLoader()
        self.data_processor = DataProcessor()
        self.data_analyzer = DataAnalyzer()
        self.visualizer = DataVisualizer()
        
        self.current_data = None
        self.setup_ui()
    
    def setup_ui(self):
        self.root.configure(bg='#f5f5f5')
        
        self.create_menu()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_left_panel(left_panel)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_right_panel(right_panel)
        
        self.status_bar = ttk.Label(self.root, text='就绪', relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='打开Excel文件', command=self.load_file)
        file_menu.add_command(label='打开文件夹', command=self.load_folder)
        file_menu.add_separator()
        file_menu.add_command(label='导出数据', command=self.export_data)
        file_menu.add_command(label='导出图表', command=self.export_chart)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.root.quit)
        
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='数据处理', menu=data_menu)
        data_menu.add_command(label='数据清洗', command=self.clean_data)
        data_menu.add_command(label='数据筛选', command=self.filter_data)
        data_menu.add_command(label='数据分组', command=self.group_data)
        data_menu.add_command(label='重置数据', command=self.reset_data)
        
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='分析', menu=analysis_menu)
        analysis_menu.add_command(label='描述性统计', command=self.show_descriptive_stats)
        analysis_menu.add_command(label='频率分析', command=self.show_frequency_analysis)
        analysis_menu.add_command(label='交叉分析', command=self.show_crosstab)
        analysis_menu.add_command(label='相关性分析', command=self.show_correlation)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=help_menu)
        help_menu.add_command(label='使用说明', command=self.show_help)
        help_menu.add_command(label='关于', command=self.show_about)
    
    def create_left_panel(self, parent):
        title_label = ttk.Label(parent, text='功能菜单', font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        buttons = [
            ('📂 数据导入', self.load_file),
            ('📊 数据概览', self.show_data_overview),
            ('🧹 数据清洗', self.clean_data),
            ('📈 统计分析', self.show_analysis),
            ('📉 可视化', self.show_visualization),
            ('📋 数据导出', self.export_data),
        ]
        
        for text, command in buttons:
            btn = ttk.Button(parent, text=text, command=command, width=20)
            btn.pack(pady=5, padx=10, fill=tk.X)
        
        info_frame = ttk.LabelFrame(parent, text='数据信息', padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)
        
        self.info_text = tk.Text(info_frame, height=15, width=25, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
    
    def create_right_panel(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.overview_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)
        self.visualization_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.overview_frame, text='数据概览')
        self.notebook.add(self.analysis_frame, text='统计分析')
        self.notebook.add(self.visualization_frame, text='可视化')
        
        self.create_overview_tab()
        self.create_analysis_tab()
        self.create_visualization_tab()
    
    def create_overview_tab(self):
        control_frame = ttk.Frame(self.overview_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text='刷新', command=self.show_data_overview).pack(side=tk.LEFT, padx=5)
        
        self.overview_tree = ttk.Treeview(self.overview_frame, show='tree headings')
        
        scrollbar_y = ttk.Scrollbar(self.overview_frame, orient=tk.VERTICAL, command=self.overview_tree.yview)
        scrollbar_x = ttk.Scrollbar(self.overview_frame, orient=tk.HORIZONTAL, command=self.overview_tree.xview)
        
        self.overview_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.overview_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_analysis_tab(self):
        control_frame = ttk.Frame(self.analysis_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text='分析维度:').pack(side=tk.LEFT, padx=5)
        
        self.dimension_var = tk.StringVar()
        self.dimension_combo = ttk.Combobox(control_frame, textvariable=self.dimension_var, width=15)
        self.dimension_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text='薪资字段:').pack(side=tk.LEFT, padx=5)
        
        self.salary_var = tk.StringVar(value='pre_tax_salary')
        self.salary_combo = ttk.Combobox(control_frame, textvariable=self.salary_var, width=15)
        self.salary_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text='执行分析', command=self.execute_analysis).pack(side=tk.LEFT, padx=10)
        
        self.analysis_result_text = tk.Text(self.analysis_frame, height=30)
        self.analysis_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_visualization_tab(self):
        control_frame = ttk.Frame(self.visualization_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text='图表类型:').pack(side=tk.LEFT, padx=5)
        
        self.chart_type_var = tk.StringVar(value='bar')
        chart_types = ['bar', 'line', 'pie', 'scatter', 'boxplot', 'histogram']
        self.chart_type_combo = ttk.Combobox(control_frame, textvariable=self.chart_type_var, 
                                             values=chart_types, width=12)
        self.chart_type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text='分组维度:').pack(side=tk.LEFT, padx=5)
        
        self.viz_dimension_var = tk.StringVar()
        self.viz_dimension_combo = ttk.Combobox(control_frame, textvariable=self.viz_dimension_var, width=12)
        self.viz_dimension_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text='生成图表', command=self.generate_chart).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text='保存图表', command=self.export_chart).pack(side=tk.LEFT, padx=5)
        
        self.chart_frame = ttk.Frame(self.visualization_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_file(self):
        file_path = self.data_loader.select_file()
        if file_path:
            self.status_bar.config(text=f'正在加载: {file_path}')
            self.root.update()
            
            data = self.data_loader.load_excel(file_path)
            
            if data is not None:
                self.current_data = data
                self.data_processor.set_data(data)
                self.data_analyzer.set_data(data)
                self.visualizer.set_data(data)
                
                self.update_info_text()
                self.update_comboboxes()
                self.show_data_overview()
                
                messagebox.showinfo('成功', f'数据加载成功！\n共 {len(data)} 条记录')
                self.status_bar.config(text='数据加载成功')
            else:
                self.status_bar.config(text='数据加载失败')
    
    def load_folder(self):
        folder_path = self.data_loader.select_folder()
        if folder_path:
            self.status_bar.config(text=f'正在加载文件夹: {folder_path}')
            self.root.update()
            
            data = self.data_loader.load_folder(folder_path)
            
            if data is not None:
                self.current_data = data
                self.data_processor.set_data(data)
                self.data_analyzer.set_data(data)
                self.visualizer.set_data(data)
                
                self.update_info_text()
                self.update_comboboxes()
                self.show_data_overview()
                
                messagebox.showinfo('成功', f'数据加载成功！\n共 {len(data)} 条记录')
                self.status_bar.config(text='数据加载成功')
            else:
                self.status_bar.config(text='数据加载失败')
    
    def update_info_text(self):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)
        
        if self.current_data is not None:
            info = f'记录数: {len(self.current_data)}\n'
            info += f'字段数: {len(self.current_data.columns)}\n\n'
            info += '字段列表:\n'
            for col in self.current_data.columns:
                info += f'  - {col}\n'
            
            missing = self.current_data.isnull().sum()
            if missing.sum() > 0:
                info += '\n缺失值:\n'
                for col, count in missing[missing > 0].items():
                    info += f'  - {col}: {count}\n'
            
            self.info_text.insert('1.0', info)
        
        self.info_text.config(state=tk.DISABLED)
    
    def update_comboboxes(self):
        if self.current_data is not None:
            categorical_cols = self.current_data.select_dtypes(include=['object', 'category']).columns.tolist()
            numeric_cols = self.current_data.select_dtypes(include=['number']).columns.tolist()
            
            self.dimension_combo['values'] = categorical_cols
            self.viz_dimension_combo['values'] = categorical_cols
            
            salary_candidates = ['pre_tax_salary', 'post_tax_salary', 'base_salary', 'total_salary']
            available_salary = [col for col in numeric_cols if col.lower() in [s.lower() for s in salary_candidates]]
            if not available_salary:
                available_salary = numeric_cols
            
            self.salary_combo['values'] = available_salary
            if available_salary:
                self.salary_var.set(available_salary[0])
    
    def show_data_overview(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        self.overview_tree.delete(*self.overview_tree.get_children())
        
        columns = ['#'] + list(self.current_data.columns)
        self.overview_tree['columns'] = columns
        self.overview_tree['show'] = 'tree headings'
        
        self.overview_tree.heading('#', text='#')
        self.overview_tree.column('#', width=50, minwidth=50)
        
        for col in self.current_data.columns:
            self.overview_tree.heading(col, text=col)
            self.overview_tree.column(col, width=120, minwidth=80)
        
        for idx, row in self.current_data.head(100).iterrows():
            values = [str(idx)] + [str(v) for v in row.values]
            self.overview_tree.insert('', tk.END, values=values)
    
    def clean_data(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title('数据清洗')
        dialog.geometry('400x300')
        
        ttk.Label(dialog, text='选择清洗操作:').pack(pady=10)
        
        ttk.Button(dialog, text='删除重复数据', 
                  command=lambda: self._do_clean('duplicates', dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text='删除缺失值行', 
                  command=lambda: self._do_clean('missing', dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text='填充缺失值(均值)', 
                  command=lambda: self._do_clean('fill_mean', dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text='移除异常值', 
                  command=lambda: self._do_clean('outliers', dialog)).pack(fill=tk.X, padx=20, pady=5)
    
    def _do_clean(self, operation, dialog):
        if self.current_data is None:
            return
        
        if operation == 'duplicates':
            count = self.data_processor.remove_duplicates()
            messagebox.showinfo('完成', f'删除了 {count} 条重复记录')
        
        elif operation == 'missing':
            before = len(self.current_data)
            self.data_processor.handle_missing_values(strategy='drop')
            after = len(self.current_data)
            messagebox.showinfo('完成', f'删除了 {before - after} 条含缺失值记录')
        
        elif operation == 'fill_mean':
            self.data_processor.handle_missing_values(strategy='fill_mean')
            messagebox.showinfo('完成', '已用均值填充数值型缺失值')
        
        elif operation == 'outliers':
            salary_col = self.salary_var.get() or 'pre_tax_salary'
            count = self.data_processor.remove_outliers(salary_col)
            messagebox.showinfo('完成', f'移除了 {count} 条异常值记录')
        
        self.current_data = self.data_processor.get_current_data()
        self.data_analyzer.set_data(self.current_data)
        self.visualizer.set_data(self.current_data)
        self.update_info_text()
        dialog.destroy()
    
    def filter_data(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        messagebox.showinfo('提示', '数据筛选功能开发中...\n可使用数据概览表格进行查看')
    
    def group_data(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title('数据分组')
        dialog.geometry('400x250')
        
        ttk.Label(dialog, text='选择分组操作:').pack(pady=10)
        
        ttk.Button(dialog, text='年龄分组', 
                  command=lambda: self._do_group('age', dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text='薪资分组', 
                  command=lambda: self._do_group('salary', dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text='工作年限分组', 
                  command=lambda: self._do_group('experience', dialog)).pack(fill=tk.X, padx=20, pady=5)
    
    def _do_group(self, group_type, dialog):
        if self.current_data is None:
            return
        
        if group_type == 'age':
            if 'age' in self.current_data.columns:
                self.data_processor.create_age_group('age')
                messagebox.showinfo('完成', '已创建年龄分组字段: age_group')
            else:
                messagebox.showwarning('警告', '数据中没有年龄字段')
        
        elif group_type == 'salary':
            salary_col = self.salary_var.get() or 'pre_tax_salary'
            if salary_col in self.current_data.columns:
                self.data_processor.create_salary_group(salary_col)
                messagebox.showinfo('完成', '已创建薪资分组字段: salary_group')
            else:
                messagebox.showwarning('警告', '数据中没有薪资字段')
        
        elif group_type == 'experience':
            if 'work_years' in self.current_data.columns:
                self.data_processor.create_work_experience_group('work_years')
                messagebox.showinfo('完成', '已创建工作年限分组字段: experience_group')
            else:
                messagebox.showwarning('警告', '数据中没有工作年限字段')
        
        self.current_data = self.data_processor.get_current_data()
        self.data_analyzer.set_data(self.current_data)
        self.update_info_text()
        dialog.destroy()
    
    def reset_data(self):
        if self.current_data is not None:
            self.data_processor.reset_data()
            self.current_data = self.data_processor.get_current_data()
            self.data_analyzer.set_data(self.current_data)
            self.update_info_text()
            messagebox.showinfo('完成', '数据已重置')
    
    def show_descriptive_stats(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        stats = self.data_analyzer.get_descriptive_stats(salary_col)
        
        result = f'薪资字段: {salary_col}\n{"="*40}\n\n'
        for key, value in stats.items():
            if value is not None:
                if isinstance(value, float):
                    result += f'{key}: {value:,.2f}\n'
                else:
                    result += f'{key}: {value}\n'
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def show_frequency_analysis(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        dimension = self.dimension_var.get()
        if not dimension:
            messagebox.showwarning('警告', '请选择分析维度')
            return
        
        freq = self.data_analyzer.get_frequency_analysis(dimension)
        
        result = f'频率分析: {dimension}\n{"="*40}\n\n'
        result += freq.to_string(index=False)
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def show_crosstab(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        dimension = self.dimension_var.get()
        if not dimension:
            messagebox.showwarning('警告', '请选择分析维度')
            return
        
        crosstab = self.data_analyzer.get_crosstab(dimension, 'gender' if 'gender' in self.current_data.columns else self.current_data.columns[0])
        
        result = f'交叉分析: {dimension}\n{"="*40}\n\n'
        result += crosstab.to_string()
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def show_correlation(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        corr = self.data_analyzer.get_correlation_matrix()
        
        if corr.empty:
            messagebox.showwarning('警告', '没有数值型字段可用于相关性分析')
            return
        
        result = f'相关性矩阵\n{"="*40}\n\n'
        result += corr.to_string()
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def show_analysis(self):
        self.notebook.select(self.analysis_frame)
        self.show_descriptive_stats()
    
    def execute_analysis(self):
        dimension = self.dimension_var.get()
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        
        if not dimension:
            messagebox.showwarning('警告', '请选择分析维度')
            return
        
        comparison = self.data_analyzer.compare_by_dimension(dimension, salary_col)
        
        result = f'维度分析: {dimension}\n薪资字段: {salary_col}\n{"="*50}\n\n'
        result += comparison.to_string(index=False)
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def show_visualization(self):
        self.notebook.select(self.visualization_frame)
    
    def generate_chart(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        chart_type = self.chart_type_var.get()
        dimension = self.viz_dimension_var.get()
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        
        # 只有部分图表类型需要分组维度
        charts_requiring_dimension = ['bar', 'horizontal', 'pie', 'boxplot']
        if chart_type in charts_requiring_dimension and not dimension:
            messagebox.showwarning('警告', '请选择分组维度')
            return
        
        try:
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            self.visualizer.create_figure(figsize=(10, 6))
            
            if chart_type == 'bar':
                grouped = self.current_data.groupby(dimension)[salary_col].mean().sort_values(ascending=False)
                self.visualizer.create_bar_chart(
                    x_data=grouped.index.tolist(),
                    y_data=grouped.values.tolist(),
                    title=f'{dimension} - 平均薪资对比',
                    xlabel=dimension,
                    ylabel='平均薪资'
                )
            
            elif chart_type == 'horizontal':
                grouped = self.current_data.groupby(dimension)[salary_col].mean().sort_values(ascending=False)
                self.visualizer.create_bar_chart(
                    x_data=grouped.index.tolist(),
                    y_data=grouped.values.tolist(),
                    title=f'{dimension} - 平均薪资对比',
                    xlabel='平均薪资',
                    ylabel=dimension,
                    horizontal=True
                )
            
            elif chart_type == 'pie':
                grouped = self.current_data.groupby(dimension)[salary_col].sum().sort_values(ascending=False)
                top_n = min(8, len(grouped))
                grouped = grouped.head(top_n)
                self.visualizer.create_pie_chart(
                    data=grouped.values.tolist(),
                    labels=grouped.index.tolist(),
                    title=f'{dimension} - 薪资占比'
                )
            
            elif chart_type == 'line':
                if 'join_year' in self.current_data.columns:
                    trend = self.current_data.groupby('join_year')[salary_col].mean().reset_index()
                    self.visualizer.create_line_chart(
                        x_data=trend['join_year'].tolist(),
                        y_data_list=[trend[salary_col].tolist()],
                        title='薪资趋势变化',
                        xlabel='年份',
                        ylabel='平均薪资'
                    )
                else:
                    messagebox.showwarning('警告', '数据中没有时间字段')
                    return
            
            elif chart_type == 'scatter':
                if 'work_years' in self.current_data.columns:
                    valid_data = self.current_data[['work_years', salary_col]].dropna()
                    self.visualizer.create_scatter_chart(
                        x_data=valid_data['work_years'].tolist(),
                        y_data=valid_data[salary_col].tolist(),
                        title='工作年限与薪资关系',
                        xlabel='工作年限',
                        ylabel='薪资'
                    )
                else:
                    messagebox.showwarning('警告', '数据中没有工作年限字段')
                    return
            
            elif chart_type == 'boxplot':
                box_data = {}
                for cat in self.current_data[dimension].unique():
                    values = self.current_data[self.current_data[dimension] == cat][salary_col].dropna().values
                    if len(values) > 0:
                        box_data[str(cat)] = values
                
                if box_data:
                    self.visualizer.create_boxplot(
                        data_dict=box_data,
                        title=f'{dimension} - 薪资分布',
                        xlabel=dimension,
                        ylabel='薪资'
                    )
            
            elif chart_type == 'histogram':
                salary_data = self.current_data[salary_col].dropna().values
                self.visualizer.create_histogram(
                    data=salary_data,
                    bins=20,
                    title='薪资分布直方图',
                    xlabel='薪资'
                )
            
            self.visualizer.embed_in_tkinter(self.chart_frame)
            
        except Exception as e:
            messagebox.showerror('错误', f'图表生成失败: {str(e)}')
    
    def export_data(self):
        if self.current_data is None:
            messagebox.showwarning('警告', '没有可导出的数据')
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel文件', '*.xlsx'), ('CSV文件', '*.csv')]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.current_data.to_csv(file_path, index=False, encoding='utf-8-sig')
                else:
                    self.current_data.to_excel(file_path, index=False)
                messagebox.showinfo('成功', f'数据已导出到:\n{file_path}')
            except Exception as e:
                messagebox.showerror('错误', f'导出失败: {str(e)}')
    
    def export_chart(self):
        if self.visualizer.figure is None:
            messagebox.showwarning('警告', '没有可导出的图表')
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG图片', '*.png'), ('JPG图片', '*.jpg'), ('PDF文档', '*.pdf')]
        )
        
        if file_path:
            try:
                fmt = file_path.split('.')[-1]
                self.visualizer.save_chart(file_path, format=fmt)
                messagebox.showinfo('成功', f'图表已保存到:\n{file_path}')
            except Exception as e:
                messagebox.showerror('错误', f'保存失败: {str(e)}')
    
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
        messagebox.showinfo('使用说明', help_text)
    
    def show_about(self):
        messagebox.showinfo('关于', '园区白领薪资数据分析工具\n\n版本: 1.0.0\n\n基于 Python + Pandas + Matplotlib 构建')


def main():
    root = tk.Tk()
    
    try:
        root.tk.call('tk', 'scaling', 1.5)
    except:
        pass
    
    app = SalaryAnalysisApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
