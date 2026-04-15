import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import DataManager, ConfigManager, get_logger
from src.controllers import DataController, AnalysisController, VisualizationController
from src.ui import UIComponentFactory


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.logger = get_logger('MainWindow')
        
        self.config = ConfigManager()
        self.data_manager = DataManager()
        
        self._setup_controllers()
        self._setup_ui()
        self._setup_data_observer()
    
    def _setup_controllers(self) -> None:
        self.data_controller = DataController(self.data_manager, self.config)
        self.analysis_controller = AnalysisController(self.data_manager, self.config)
        self.visualization_controller = VisualizationController(self.data_manager, self.config)
        
        self.data_controller.set_root(self.root)
        self.data_controller.set_status_callback(self._update_status)
        self.data_controller.set_info_callback(self._update_info_panel)
    
    def _setup_ui(self) -> None:
        window_config = self.config.get_window_config()
        self.root.title(window_config.get('title', '园区白领薪资数据分析工具'))
        self.root.geometry(f"{window_config.get('width', 1400)}x{window_config.get('height', 800)}")
        self.root.configure(bg='#f5f5f5')
        
        UIComponentFactory.configure_styles()
        
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
    
    def _create_menu(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='打开Excel文件', command=self._on_load_file)
        file_menu.add_command(label='打开文件夹', command=self._on_load_folder)
        file_menu.add_separator()
        file_menu.add_command(label='导出数据', command=self._on_export_data)
        file_menu.add_command(label='导出图表', command=self._on_export_chart)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.root.quit)
        
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='数据处理', menu=data_menu)
        data_menu.add_command(label='数据清洗', command=self._show_clean_dialog)
        data_menu.add_command(label='数据分组', command=self._show_group_dialog)
        data_menu.add_command(label='重置数据', command=self._on_reset_data)
        
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='分析', menu=analysis_menu)
        analysis_menu.add_command(label='描述性统计', command=self._on_descriptive_stats)
        analysis_menu.add_command(label='频率分析', command=self._on_frequency_analysis)
        analysis_menu.add_command(label='交叉分析', command=self._on_crosstab)
        analysis_menu.add_command(label='相关性分析', command=self._on_correlation)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=help_menu)
        help_menu.add_command(label='使用说明', command=self._show_help)
        help_menu.add_command(label='关于', command=self._show_about)
    
    def _create_main_layout(self) -> None:
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self._create_left_panel(left_panel)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self._create_right_panel(right_panel)
    
    def _create_left_panel(self, parent: ttk.Frame) -> None:
        title_label = UIComponentFactory.create_label(parent, '功能菜单', style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        buttons = [
            ('📂 数据导入', self._on_load_file),
            ('📊 数据概览', self._on_data_overview),
            ('🧹 数据清洗', self._show_clean_dialog),
            ('📈 统计分析', self._on_analysis_tab),
            ('📉 可视化', self._on_visualization_tab),
            ('📋 数据导出', self._on_export_data),
        ]
        
        UIComponentFactory.create_menu_button_group(parent, buttons, pack_kwargs={'fill': tk.X})
        
        info_panel = UIComponentFactory.create_info_panel(parent, '数据信息', height=15)
        self.info_text = info_panel['text']
        info_panel['frame'].pack(fill=tk.BOTH, expand=True, pady=20, padx=10)
    
    def _create_right_panel(self, parent: ttk.Frame) -> None:
        self.notebook = UIComponentFactory.create_notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.overview_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)
        self.visualization_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.overview_frame, text='数据概览')
        self.notebook.add(self.analysis_frame, text='统计分析')
        self.notebook.add(self.visualization_frame, text='可视化')
        
        self._create_overview_tab()
        self._create_analysis_tab()
        self._create_visualization_tab()
    
    def _create_overview_tab(self) -> None:
        control_frame = ttk.Frame(self.overview_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        UIComponentFactory.create_button(control_frame, '刷新', self._on_data_overview).pack(side=tk.LEFT, padx=5)
        
        self.overview_tree = UIComponentFactory.create_treeview(self.overview_frame, show='tree headings')
        
        scrollbar_y = UIComponentFactory.create_scrollbar(self.overview_frame, orient='vertical',
                                                          command=self.overview_tree.yview)
        scrollbar_x = UIComponentFactory.create_scrollbar(self.overview_frame, orient='horizontal',
                                                          command=self.overview_tree.xview)
        
        self.overview_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.overview_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_analysis_tab(self) -> None:
        control_frame = ttk.Frame(self.analysis_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        UIComponentFactory.create_label(control_frame, '分析维度:').pack(side=tk.LEFT, padx=5)
        
        self.dimension_var = tk.StringVar()
        self.dimension_combo = UIComponentFactory.create_combobox(control_frame, self.dimension_var, width=15)
        self.dimension_combo.pack(side=tk.LEFT, padx=5)
        
        UIComponentFactory.create_label(control_frame, '薪资字段:').pack(side=tk.LEFT, padx=5)
        
        self.salary_var = tk.StringVar(value='pre_tax_salary')
        self.salary_combo = UIComponentFactory.create_combobox(control_frame, self.salary_var, width=15)
        self.salary_combo.pack(side=tk.LEFT, padx=5)
        
        UIComponentFactory.create_button(control_frame, '执行分析', self._on_execute_analysis).pack(side=tk.LEFT, padx=10)
        
        self.analysis_result_text = UIComponentFactory.create_text(self.analysis_frame, height=30)
        self.analysis_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_visualization_tab(self) -> None:
        control_frame = ttk.Frame(self.visualization_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        UIComponentFactory.create_label(control_frame, '图表类型:').pack(side=tk.LEFT, padx=5)
        
        self.chart_type_var = tk.StringVar(value='bar')
        chart_types = ['bar', 'line', 'pie', 'scatter', 'boxplot', 'histogram']
        self.chart_type_combo = UIComponentFactory.create_combobox(control_frame, self.chart_type_var,
                                                                   chart_types, width=12)
        self.chart_type_combo.pack(side=tk.LEFT, padx=5)
        
        UIComponentFactory.create_label(control_frame, '分组维度:').pack(side=tk.LEFT, padx=5)
        
        self.viz_dimension_var = tk.StringVar()
        self.viz_dimension_combo = UIComponentFactory.create_combobox(control_frame, self.viz_dimension_var, width=12)
        self.viz_dimension_combo.pack(side=tk.LEFT, padx=5)
        
        UIComponentFactory.create_button(control_frame, '生成图表', self._on_generate_chart).pack(side=tk.LEFT, padx=10)
        UIComponentFactory.create_button(control_frame, '保存图表', self._on_export_chart).pack(side=tk.LEFT, padx=5)
        
        self.chart_frame = ttk.Frame(self.visualization_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_status_bar(self) -> None:
        self.status_bar = UIComponentFactory.create_status_bar(self.root, '就绪')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_data_observer(self) -> None:
        self.data_manager.subscribe(self._on_data_changed)
    
    def _on_data_changed(self, event) -> None:
        self._update_comboboxes()
    
    def _update_status(self, message: str) -> None:
        self.status_bar.config(text=message)
        self.root.update()
    
    def _update_info_panel(self, info: dict) -> None:
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)
        
        if info.get('has_data'):
            text = f"记录数: {info['rows']}\n"
            text += f"字段数: {info['columns']}\n\n"
            text += '字段列表:\n'
            for col in info['column_names']:
                text += f'  - {col}\n'
            
            missing = info.get('missing_values', {})
            if missing:
                text += '\n缺失值:\n'
                for col, count in missing.items():
                    if count > 0:
                        text += f'  - {col}: {count}\n'
            
            self.info_text.insert('1.0', text)
        
        self.info_text.config(state=tk.DISABLED)
    
    def _update_comboboxes(self) -> None:
        categorical_cols = self.data_manager.get_categorical_columns()
        numeric_cols = self.data_manager.get_numeric_columns()
        
        self.dimension_combo['values'] = categorical_cols
        self.viz_dimension_combo['values'] = categorical_cols
        
        salary_candidates = self.config.get('data.salary_fields', [])
        available_salary = [col for col in numeric_cols if col.lower() in [s.lower() for s in salary_candidates]]
        if not available_salary:
            available_salary = numeric_cols
        
        self.salary_combo['values'] = available_salary
        if available_salary:
            self.salary_var.set(available_salary[0])
    
    def _on_load_file(self) -> None:
        self.data_controller.select_and_load_file()
    
    def _on_load_folder(self) -> None:
        self.data_controller.select_and_load_folder()
    
    def _on_export_data(self) -> None:
        self.data_controller.export_data()
    
    def _on_export_chart(self) -> None:
        self.visualization_controller.save_chart()
    
    def _on_data_overview(self) -> None:
        if not self.data_controller.has_data():
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        data = self.data_manager.get_data()
        if data is None:
            return
        
        self.overview_tree.delete(*self.overview_tree.get_children())
        
        columns = ['#'] + list(data.columns)
        self.overview_tree['columns'] = columns
        self.overview_tree['show'] = 'tree headings'
        
        self.overview_tree.heading('#', text='#')
        self.overview_tree.column('#', width=50, minwidth=50)
        
        for col in data.columns:
            self.overview_tree.heading(col, text=col)
            self.overview_tree.column(col, width=120, minwidth=80)
        
        for idx, row in data.head(100).iterrows():
            values = [str(idx)] + [str(v) for v in row.values]
            self.overview_tree.insert('', tk.END, values=values)
    
    def _show_clean_dialog(self) -> None:
        if not self.data_controller.has_data():
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
    
    def _do_clean(self, operation: str, dialog: tk.Toplevel) -> None:
        if operation == 'duplicates':
            self.data_controller.clean_duplicates()
        elif operation == 'missing':
            self.data_controller.clean_missing_values('drop')
        elif operation == 'fill_mean':
            self.data_controller.clean_missing_values('fill_mean')
        elif operation == 'outliers':
            salary_col = self.salary_var.get() or 'pre_tax_salary'
            self.data_controller.remove_outliers(salary_col)
        
        dialog.destroy()
    
    def _show_group_dialog(self) -> None:
        if not self.data_controller.has_data():
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
    
    def _do_group(self, group_type: str, dialog: tk.Toplevel) -> None:
        if group_type == 'age':
            self.data_controller.create_age_group()
        elif group_type == 'salary':
            salary_col = self.salary_var.get() or 'pre_tax_salary'
            self.data_controller.create_salary_group(salary_col)
        elif group_type == 'experience':
            self.data_controller.create_experience_group()
        
        dialog.destroy()
    
    def _on_reset_data(self) -> None:
        self.data_controller.reset_data()
    
    def _on_descriptive_stats(self) -> None:
        if not self.analysis_controller.has_data():
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        stats = self.analysis_controller.get_descriptive_stats(salary_col)
        result = self.analysis_controller.format_stats_result(stats, salary_col)
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def _on_frequency_analysis(self) -> None:
        if not self.analysis_controller.has_data():
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        dimension = self.dimension_var.get()
        if not dimension:
            messagebox.showwarning('警告', '请选择分析维度')
            return
        
        freq = self.analysis_controller.get_frequency_analysis(dimension)
        result = self.analysis_controller.format_frequency_result(freq, dimension)
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def _on_crosstab(self) -> None:
        if not self.analysis_controller.has_data():
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        dimension = self.dimension_var.get()
        if not dimension:
            messagebox.showwarning('警告', '请选择分析维度')
            return
        
        col_col = 'gender' if 'gender' in self.data_manager.get_column_names() else self.data_manager.get_column_names()[0]
        crosstab = self.analysis_controller.get_crosstab(dimension, col_col)
        result = self.analysis_controller.format_crosstab_result(crosstab, dimension)
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def _on_correlation(self) -> None:
        if not self.analysis_controller.has_data():
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        corr = self.analysis_controller.get_correlation_matrix()
        
        if corr.empty:
            result = "没有足够的数值列进行相关性分析"
        else:
            result = "相关性矩阵:\n" + "="*40 + "\n\n"
            result += corr.to_string()
        
        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)
    
    def _on_execute_analysis(self) -> None:
        self._on_descriptive_stats()
    
    def _on_analysis_tab(self) -> None:
        self.notebook.select(self.analysis_frame)
    
    def _on_visualization_tab(self) -> None:
        self.notebook.select(self.visualization_frame)
    
    def _on_generate_chart(self) -> None:
        if not self.visualization_controller.has_data():
            messagebox.showwarning('警告', '请先加载数据')
            return
        
        chart_type = self.chart_type_var.get()
        dimension = self.viz_dimension_var.get()
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        
        charts_requiring_dimension = ['bar', 'pie', 'boxplot']
        if chart_type in charts_requiring_dimension and not dimension:
            messagebox.showwarning('警告', '请选择分组维度')
            return
        
        try:
            figure = None
            
            if chart_type == 'bar':
                figure = self.visualization_controller.create_bar_chart(dimension, salary_col)
            elif chart_type == 'line':
                if 'join_year' in self.data_manager.get_column_names():
                    figure = self.visualization_controller.create_line_chart('join_year', salary_col)
                else:
                    messagebox.showwarning('警告', '数据中没有时间字段')
                    return
            elif chart_type == 'pie':
                figure = self.visualization_controller.create_pie_chart(dimension, salary_col)
            elif chart_type == 'scatter':
                if 'work_years' in self.data_manager.get_column_names():
                    figure = self.visualization_controller.create_scatter_chart('work_years', salary_col)
                else:
                    messagebox.showwarning('警告', '数据中没有工作年限字段')
                    return
            elif chart_type == 'boxplot':
                figure = self.visualization_controller.create_boxplot(dimension, salary_col)
            elif chart_type == 'histogram':
                figure = self.visualization_controller.create_histogram(salary_col, bins=20)
            
            if figure:
                self.visualization_controller.embed_chart(self.chart_frame, figure)
            
        except Exception as e:
            messagebox.showerror('错误', f'图表生成失败: {str(e)}')
    
    def _show_help(self) -> None:
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
    
    def _show_about(self) -> None:
        messagebox.showinfo('关于', f'{self.config.get("app.name")}\n\n版本: {self.config.get("app.version")}\n\n基于 Python + Pandas + Matplotlib 构建')


def main():
    root = tk.Tk()
    
    try:
        root.tk.call('tk', 'scaling', 1.5)
    except:
        pass
    
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
