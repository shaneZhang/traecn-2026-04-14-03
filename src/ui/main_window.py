import tkinter as tk
from tkinter import ttk
import pandas as pd
from typing import Optional
from .base import BaseWidget
from .factory import WidgetFactory
from .dialogs import DataCleanDialog, DataGroupDialog
from src.controllers import AppController
from src.core.exceptions import SalaryAnalysisError


class MainWindow(BaseWidget):
    def __init__(self, root: tk.Tk):
        self.root = root
        self.app_controller = AppController(root)
        self.data_controller = self.app_controller.data_controller
        self.analysis_controller = self.app_controller.analysis_controller
        self.viz_controller = self.app_controller.visualization_controller

        self.app_controller.set_status_callback(self._update_status)

        super().__init__(root)

        self.root.title(self.app_controller.get_app_title())
        self.root.geometry(self.app_controller.get_window_size())
        self.root.configure(bg='#f5f5f5')

    def _create_variables(self, **kwargs):
        self.dimension_var = tk.StringVar()
        self.salary_var = tk.StringVar(value='pre_tax_salary')
        self.chart_type_var = tk.StringVar(value='bar')
        self.viz_dimension_var = tk.StringVar()

    def _build_ui(self):
        self._create_menu()

        main_frame = WidgetFactory.create_frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        self._create_left_panel(left_panel)

        right_panel = WidgetFactory.create_frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._create_right_panel(right_panel)

        self.status_bar = WidgetFactory.set_status_bar(self.root, '就绪')

    def _create_menu(self):
        menus = {
            '文件': [
                ('打开Excel文件', self.load_file),
                ('打开文件夹', self.load_folder),
                ('---', None),
                ('导出数据', self.export_data),
                ('导出图表', self.export_chart),
                ('---', None),
                ('退出', self.app_controller.exit)
            ],
            '数据处理': [
                ('数据清洗', self.clean_data),
                ('数据筛选', self.filter_data),
                ('数据分组', self.group_data),
                ('重置数据', self.reset_data)
            ],
            '分析': [
                ('描述性统计', self.show_descriptive_stats),
                ('频率分析', self.show_frequency_analysis),
                ('交叉分析', self.show_crosstab),
                ('相关性分析', self.show_correlation)
            ],
            '帮助': [
                ('使用说明', self.app_controller.show_help),
                ('关于', self.app_controller.show_about)
            ]
        }

        menubar = WidgetFactory.create_menu_bar(self.root, menus)
        self.root.config(menu=menubar)

    def _create_left_panel(self, parent):
        WidgetFactory.create_label(
            parent, '功能菜单', font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        buttons = [
            ('📂 数据导入', self.load_file),
            ('📊 数据概览', self.show_data_overview),
            ('🧹 数据清洗', self.clean_data),
            ('📈 统计分析', self.show_analysis),
            ('📉 可视化', self.show_visualization),
            ('📋 数据导出', self.export_data)
        ]

        WidgetFactory.create_button_group(parent, buttons, vertical=True)

        info_frame = WidgetFactory.create_labelframe(parent, '数据信息')
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)

        self.info_text = WidgetFactory.create_text(info_frame, height=15, width=25, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)

    def _create_right_panel(self, parent):
        self.notebook = WidgetFactory.create_notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.overview_frame = WidgetFactory.create_frame(self.notebook)
        self.analysis_frame = WidgetFactory.create_frame(self.notebook)
        self.visualization_frame = WidgetFactory.create_frame(self.notebook)

        self.notebook.add(self.overview_frame, text='数据概览')
        self.notebook.add(self.analysis_frame, text='统计分析')
        self.notebook.add(self.visualization_frame, text='可视化')

        self._create_overview_tab()
        self._create_analysis_tab()
        self._create_visualization_tab()

    def _create_overview_tab(self):
        control_frame = WidgetFactory.create_frame(self.overview_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(control_frame, text='刷新', command=self.show_data_overview).pack(side=tk.LEFT, padx=5)

        self.overview_tree = WidgetFactory.create_treeview(self.overview_frame)

        scrollbar_y = WidgetFactory.create_scrollbar(self.overview_frame, tk.VERTICAL, self.overview_tree.yview)
        scrollbar_x = WidgetFactory.create_scrollbar(self.overview_frame, tk.HORIZONTAL, self.overview_tree.xview)

        self.overview_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.overview_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_analysis_tab(self):
        control_frame = WidgetFactory.create_frame(self.analysis_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(control_frame, text='分析维度:').pack(side=tk.LEFT, padx=5)
        self.dimension_combo = WidgetFactory.create_combobox(control_frame, self.dimension_var)
        self.dimension_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text='薪资字段:').pack(side=tk.LEFT, padx=5)
        self.salary_combo = WidgetFactory.create_combobox(control_frame, self.salary_var)
        self.salary_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text='执行分析', command=self.execute_analysis).pack(side=tk.LEFT, padx=10)

        self.analysis_result_text = WidgetFactory.create_text(self.analysis_frame, height=30)
        self.analysis_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_visualization_tab(self):
        control_frame = WidgetFactory.create_frame(self.visualization_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(control_frame, text='图表类型:').pack(side=tk.LEFT, padx=5)

        chart_types = ['bar', 'line', 'pie', 'scatter', 'boxplot', 'histogram']
        self.chart_type_combo = WidgetFactory.create_combobox(
            control_frame, self.chart_type_var, values=chart_types
        )
        self.chart_type_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text='分组维度:').pack(side=tk.LEFT, padx=5)
        self.viz_dimension_combo = WidgetFactory.create_combobox(control_frame, self.viz_dimension_var)
        self.viz_dimension_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text='生成图表', command=self.generate_chart).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text='保存图表', command=self.export_chart).pack(side=tk.LEFT, padx=5)

        self.chart_frame = WidgetFactory.create_frame(self.visualization_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _bind_events(self):
        pass

    def _update_status(self, message: str):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def _check_data(self) -> bool:
        if not self.data_controller.has_data():
            self.show_message('警告', '请先加载数据', 'warning')
            return False
        return True

    def load_file(self):
        try:
            self._update_status('正在加载文件...')
            if self.data_controller.load_file(self.root):
                self._on_data_loaded()
                self.show_message('成功', f'数据加载成功！\n共 {len(self.data_controller.get_data())} 条记录', 'info')
        except SalaryAnalysisError as e:
            self.handle_exception(e, '加载失败')
        finally:
            self._update_status('就绪')

    def load_folder(self):
        try:
            self._update_status('正在加载文件夹...')
            if self.data_controller.load_folder(self.root):
                self._on_data_loaded()
                self.show_message('成功', f'数据加载成功！\n共 {len(self.data_controller.get_data())} 条记录', 'info')
        except SalaryAnalysisError as e:
            self.handle_exception(e, '加载失败')
        finally:
            self._update_status('就绪')

    def _on_data_loaded(self):
        self._update_info_text()
        self._update_comboboxes()
        self.show_data_overview()

    def _update_info_text(self):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)

        info = self.data_controller.get_data_info()
        if info:
            text = f"记录数: {info.get('rows', 0)}\n"
            text += f"字段数: {info.get('columns', 0)}\n\n"
            text += "字段列表:\n"
            for col in info.get('column_names', []):
                text += f"  - {col}\n"

            missing = info.get('missing_values', {})
            if missing:
                text += "\n缺失值:\n"
                for col, count in missing.items():
                    text += f"  - {col}: {count}\n"

            self.info_text.insert('1.0', text)

        self.info_text.config(state=tk.DISABLED)

    def _update_comboboxes(self):
        categorical_cols = self.data_controller.get_categorical_columns()
        salary_cols = self.data_controller.get_salary_columns()

        self.dimension_combo['values'] = categorical_cols
        self.viz_dimension_combo['values'] = categorical_cols

        self.salary_combo['values'] = salary_cols
        if salary_cols:
            self.salary_var.set(salary_cols[0])

    def show_data_overview(self):
        if not self._check_data():
            return

        self.overview_tree.delete(*self.overview_tree.get_children())
        data = self.data_controller.get_data()

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

    def clean_data(self):
        if not self._check_data():
            return

        dialog = DataCleanDialog(self.root)
        self.root.wait_window(dialog)

        operation = dialog.result
        if not operation:
            return

        try:
            self._update_status('正在执行数据清洗...')
            salary_col = self.salary_var.get() or 'pre_tax_salary'

            if operation == 'duplicates':
                count = self.data_controller.remove_duplicates()
                self.show_message('完成', f'删除了 {count} 条重复记录')

            elif operation == 'missing':
                self.data_controller.handle_missing_values('drop')
                self.show_message('完成', '已删除含缺失值记录')

            elif operation == 'fill_mean':
                self.data_controller.handle_missing_values('fill_mean')
                self.show_message('完成', '已用均值填充数值型缺失值')

            elif operation == 'outliers':
                count = self.data_controller.remove_outliers(salary_col)
                self.show_message('完成', f'移除了 {count} 条异常值记录')

            self._update_info_text()

        except SalaryAnalysisError as e:
            self.handle_exception(e, '清洗失败')
        finally:
            self._update_status('就绪')

    def filter_data(self):
        self.show_message('提示', '数据筛选功能开发中...\n可使用数据概览表格进行查看')

    def group_data(self):
        if not self._check_data():
            return

        dialog = DataGroupDialog(self.root)
        self.root.wait_window(dialog)

        group_type = dialog.result
        if not group_type:
            return

        try:
            self._update_status('正在创建分组...')
            salary_col = self.salary_var.get() or 'pre_tax_salary'

            if group_type == 'age':
                self.data_controller.create_age_group()
                self.show_message('完成', '已创建年龄分组字段: age_group')

            elif group_type == 'salary':
                self.data_controller.create_salary_group(salary_col)
                self.show_message('完成', '已创建薪资分组字段: salary_group')

            elif group_type == 'experience':
                self.data_controller.create_work_experience_group()
                self.show_message('完成', '已创建工作年限分组字段: experience_group')

            self._update_info_text()
            self._update_comboboxes()

        except SalaryAnalysisError as e:
            self.handle_exception(e, '分组失败')
        finally:
            self._update_status('就绪')

    def reset_data(self):
        if not self._check_data():
            return
        self.data_controller.reset_data()
        self._update_info_text()
        self.show_message('完成', '数据已重置')

    def show_descriptive_stats(self):
        if not self._check_data():
            return

        salary_col = self.salary_var.get() or 'pre_tax_salary'
        stats = self.analysis_controller.get_descriptive_stats(salary_col)
        result = self.analysis_controller.format_descriptive_stats(stats, salary_col)

        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)

    def show_frequency_analysis(self):
        if not self._check_data():
            return

        dimension = self.dimension_var.get()
        if not dimension:
            self.show_message('警告', '请选择分析维度', 'warning')
            return

        freq = self.analysis_controller.get_frequency_analysis(dimension)
        result = self.analysis_controller.format_frequency(freq, dimension)

        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)

    def show_crosstab(self):
        if not self._check_data():
            return

        dimension = self.dimension_var.get()
        if not dimension:
            self.show_message('警告', '请选择分析维度', 'warning')
            return

        data = self.data_controller.get_data()
        col_col = 'gender' if 'gender' in data.columns else data.columns[0]
        crosstab = self.analysis_controller.get_crosstab(dimension, col_col)
        result = self.analysis_controller.format_crosstab(crosstab, dimension)

        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)

    def show_correlation(self):
        if not self._check_data():
            return

        corr = self.analysis_controller.get_correlation_matrix()
        if corr.empty:
            self.show_message('警告', '没有数值型字段可用于相关性分析', 'warning')
            return

        result = self.analysis_controller.format_correlation(corr)

        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)

    def show_analysis(self):
        self.notebook.select(self.analysis_frame)
        self.show_descriptive_stats()

    def execute_analysis(self):
        if not self._check_data():
            return

        dimension = self.dimension_var.get()
        salary_col = self.salary_var.get() or 'pre_tax_salary'

        if not dimension:
            self.show_message('警告', '请选择分析维度', 'warning')
            return

        comparison = self.analysis_controller.compare_by_dimension(dimension, salary_col)
        result = self.analysis_controller.format_comparison(comparison, dimension, salary_col)

        self.analysis_result_text.delete('1.0', tk.END)
        self.analysis_result_text.insert('1.0', result)

    def show_visualization(self):
        self.notebook.select(self.visualization_frame)

    def generate_chart(self):
        if not self._check_data():
            return

        chart_type = self.chart_type_var.get()
        dimension = self.viz_dimension_var.get()
        salary_col = self.salary_var.get() or 'pre_tax_salary'

        charts_requiring_dimension = ['bar', 'pie', 'boxplot']
        if chart_type in charts_requiring_dimension and not dimension:
            self.show_message('警告', '请选择分组维度', 'warning')
            return

        try:
            self._update_status('正在生成图表...')

            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            self.viz_controller.create_chart(chart_type, dimension, salary_col, self.chart_frame)

        except SalaryAnalysisError as e:
            self.handle_exception(e, '图表生成失败')
        finally:
            self._update_status('就绪')

    def export_data(self):
        if not self._check_data():
            return

        try:
            if self.data_controller.export_data(self.root):
                self.show_message('成功', '数据导出成功')
        except SalaryAnalysisError as e:
            self.handle_exception(e, '导出失败')

    def export_chart(self):
        if not self.viz_controller.get_current_figure():
            self.show_message('警告', '没有可导出的图表', 'warning')
            return

        try:
            if self.viz_controller.export_chart(self.root):
                self.show_message('成功', '图表导出成功')
        except SalaryAnalysisError as e:
            self.handle_exception(e, '导出失败')
