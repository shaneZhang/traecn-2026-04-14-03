import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Dict, Any
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from .factory import UIComponentFactory
from .base import DialogMixin, StatusBarMixin, DataViewMixin
from ..controllers.data_controller import DataController
from ..controllers.analysis_controller import AnalysisController
from ..controllers.visualization_controller import VisualizationController
from ..models.data_manager import DataManager, DataChangeEvent
from ..models.config_manager import ConfigManager


class MainWindow(DialogMixin, StatusBarMixin, DataViewMixin):
    """主窗口"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.config_manager = ConfigManager.get_instance()
        self.data_manager = DataManager.get_instance()

        ui_config = self.config_manager.get('ui', {})
        self.root.title(ui_config.get('window_title', '园区白领薪资数据分析工具'))
        self.root.geometry(ui_config.get('window_size', '1400x800'))

        self.data_controller = DataController()
        self.analysis_controller = AnalysisController()
        self.visualization_controller = VisualizationController()

        self._setup_controllers()
        self._create_ui()
        self._subscribe_to_data_changes()

    def _setup_controllers(self):
        """设置控制器回调"""
        self.data_controller.add_error_handler(lambda msg: self.show_error('错误', msg))
        self.data_controller.add_success_handler(lambda msg: self.show_info('成功', msg))

        self.analysis_controller.add_error_handler(lambda msg: self.show_error('错误', msg))
        self.analysis_controller.add_result_handler(self._display_analysis_result)

        self.visualization_controller.add_error_handler(lambda msg: self.show_error('错误', msg))
        self.visualization_controller.add_figure_handler(self._display_chart)

    def _subscribe_to_data_changes(self):
        """订阅数据变更"""
        self.data_manager.subscribe(self._on_data_changed)

    def _on_data_changed(self, event: DataChangeEvent):
        """数据变更回调"""
        self._update_info_panel()
        self._update_comboboxes()
        self._refresh_data_view()

    def _create_ui(self):
        """创建UI界面"""
        self.root.configure(bg='#f5f5f5')

        self._create_menu()

        main_frame = UIComponentFactory.create_frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = UIComponentFactory.create_frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        left_panel.configure(width=250)

        self._create_left_panel(left_panel)

        right_panel = UIComponentFactory.create_frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._create_right_panel(right_panel)

        self.create_status_bar(self.root)

    def _create_menu(self):
        """创建菜单"""
        menubar = UIComponentFactory.create_menu(self.root)
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
        data_menu.add_command(label='删除重复数据', command=self._on_clean_duplicates)
        data_menu.add_command(label='删除缺失值行', command=lambda: self._on_clean_missing('drop'))
        data_menu.add_command(label='填充缺失值(均值)', command=lambda: self._on_clean_missing('fill_mean'))
        data_menu.add_separator()
        data_menu.add_command(label='年龄分组', command=self._on_age_group)
        data_menu.add_command(label='薪资分组', command=self._on_salary_group)
        data_menu.add_command(label='工作年限分组', command=self._on_experience_group)
        data_menu.add_separator()
        data_menu.add_command(label='重置数据', command=self._on_reset_data)

        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='分析', menu=analysis_menu)
        analysis_menu.add_command(label='描述性统计', command=self._on_descriptive_stats)
        analysis_menu.add_command(label='频率分析', command=self._on_frequency_analysis)
        analysis_menu.add_command(label='交叉分析', command=self._on_crosstab)
        analysis_menu.add_command(label='相关性分析', command=self._on_correlation)
        analysis_menu.add_separator()
        analysis_menu.add_command(label='薪资汇总报告', command=self._on_summary_report)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=help_menu)
        help_menu.add_command(label='使用说明', command=self._on_show_help)
        help_menu.add_command(label='关于', command=self._on_show_about)

    def _create_left_panel(self, parent):
        """创建左侧面板"""
        title_label = UIComponentFactory.create_label(
            parent, text='功能菜单', font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))

        buttons = [
            ('📂 数据导入', self._on_load_file),
            ('📊 数据概览', self._on_show_overview),
            ('🧹 数据清洗', self._on_show_clean_dialog),
            ('📈 统计分析', self._on_show_analysis),
            ('📉 可视化', self._on_show_visualization),
            ('📋 数据导出', self._on_export_data),
        ]

        for text, command in buttons:
            btn = UIComponentFactory.create_button(parent, text=text, command=command, width=20)
            btn.pack(pady=5, padx=10, fill=tk.X)

        info_frame = UIComponentFactory.create_label_frame(parent, text='数据信息', padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)

        self.info_text = UIComponentFactory.create_text(
            info_frame, height=15, width=25, state=tk.DISABLED
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)

    def _create_right_panel(self, parent):
        """创建右侧面板"""
        self.notebook = UIComponentFactory.create_notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.overview_frame = UIComponentFactory.create_frame(self.notebook)
        self.analysis_frame = UIComponentFactory.create_frame(self.notebook)
        self.visualization_frame = UIComponentFactory.create_frame(self.notebook)

        self.notebook.add(self.overview_frame, text='数据概览')
        self.notebook.add(self.analysis_frame, text='统计分析')
        self.notebook.add(self.visualization_frame, text='可视化')

        self._create_overview_tab()
        self._create_analysis_tab()
        self._create_visualization_tab()

    def _create_overview_tab(self):
        """创建数据概览标签页"""
        control_frame = UIComponentFactory.create_frame(self.overview_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        UIComponentFactory.create_button(
            control_frame, text='刷新', command=self._on_show_overview
        ).pack(side=tk.LEFT, padx=5)

        self.overview_tree = UIComponentFactory.create_treeview(
            self.overview_frame, columns=['#'], height=20
        )

        scrollbar_y = UIComponentFactory.create_scrollbar(
            self.overview_frame, orient=tk.VERTICAL, command=self.overview_tree.yview
        )
        scrollbar_x = UIComponentFactory.create_scrollbar(
            self.overview_frame, orient=tk.HORIZONTAL, command=self.overview_tree.xview
        )

        self.overview_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.overview_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_analysis_tab(self):
        """创建统计分析标签页"""
        control_frame = UIComponentFactory.create_frame(self.analysis_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        UIComponentFactory.create_label(control_frame, text='分析维度:').pack(side=tk.LEFT, padx=5)

        self.dimension_var = tk.StringVar()
        self.dimension_combo = UIComponentFactory.create_combobox(
            control_frame, textvariable=self.dimension_var, width=15
        )
        self.dimension_combo.pack(side=tk.LEFT, padx=5)

        UIComponentFactory.create_label(control_frame, text='薪资字段:').pack(side=tk.LEFT, padx=5)

        self.salary_var = tk.StringVar(value='pre_tax_salary')
        self.salary_combo = UIComponentFactory.create_combobox(
            control_frame, textvariable=self.salary_var, width=15
        )
        self.salary_combo.pack(side=tk.LEFT, padx=5)

        UIComponentFactory.create_button(
            control_frame, text='执行分析', command=self._on_execute_analysis
        ).pack(side=tk.LEFT, padx=10)

        self.analysis_result_text = UIComponentFactory.create_scrolled_text(
            self.analysis_frame, height=30
        )
        self.analysis_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_visualization_tab(self):
        """创建可视化标签页"""
        control_frame = UIComponentFactory.create_frame(self.visualization_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        UIComponentFactory.create_label(control_frame, text='图表类型:').pack(side=tk.LEFT, padx=5)

        self.chart_type_var = tk.StringVar(value='bar')
        chart_types = ['bar', 'horizontal', 'pie', 'line', 'scatter', 'boxplot', 'histogram', 'heatmap']
        self.chart_type_combo = UIComponentFactory.create_combobox(
            control_frame, textvariable=self.chart_type_var, values=chart_types, width=12
        )
        self.chart_type_combo.pack(side=tk.LEFT, padx=5)

        UIComponentFactory.create_label(control_frame, text='分组维度:').pack(side=tk.LEFT, padx=5)

        self.viz_dimension_var = tk.StringVar()
        self.viz_dimension_combo = UIComponentFactory.create_combobox(
            control_frame, textvariable=self.viz_dimension_var, width=12
        )
        self.viz_dimension_combo.pack(side=tk.LEFT, padx=5)

        UIComponentFactory.create_button(
            control_frame, text='生成图表', command=self._on_generate_chart
        ).pack(side=tk.LEFT, padx=10)

        UIComponentFactory.create_button(
            control_frame, text='保存图表', command=self._on_export_chart
        ).pack(side=tk.LEFT, padx=5)

        self.chart_frame = UIComponentFactory.create_frame(self.visualization_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.current_figure: Optional[Figure] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar: Optional[NavigationToolbar2Tk] = None

    def _update_info_panel(self):
        """更新信息面板"""
        summary = self.data_controller.get_data_summary()

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)

        if summary.get('has_data'):
            info = f"记录数: {summary['row_count']}\n"
            info += f"字段数: {summary['column_count']}\n\n"
            info += "字段列表:\n"
            for col in summary['columns']:
                info += f"  - {col}\n"

            if summary.get('null_count', 0) > 0:
                info += f"\n缺失值总数: {summary['null_count']}\n"

            self.info_text.insert('1.0', info)

        self.info_text.config(state=tk.DISABLED)

    def _update_comboboxes(self):
        """更新下拉框选项"""
        summary = self.data_controller.get_data_summary()

        if summary.get('has_data'):
            categorical_cols = summary.get('categorical_columns', [])
            numeric_cols = summary.get('numeric_columns', [])

            self.dimension_combo['values'] = categorical_cols
            self.viz_dimension_combo['values'] = categorical_cols

            salary_candidates = ['pre_tax_salary', 'post_tax_salary', 'base_salary', 'total_salary']
            available_salary = [col for col in numeric_cols
                              if col.lower() in [s.lower() for s in salary_candidates]]
            if not available_salary:
                available_salary = numeric_cols

            self.salary_combo['values'] = available_salary
            if available_salary and not self.salary_var.get():
                self.salary_var.set(available_salary[0])

    def _refresh_data_view(self):
        """刷新数据视图"""
        self._on_show_overview()

    def _display_analysis_result(self, result: str, title: str = ""):
        """显示分析结果"""
        self.notebook.select(self.analysis_frame)
        self.display_result(self.analysis_result_text, result)

    def _display_chart(self, figure: Figure):
        """显示图表"""
        self.current_figure = figure
        self.notebook.select(self.visualization_frame)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.chart_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_load_file(self):
        """加载文件"""
        file_path = self.ask_open_file()
        if file_path:
            self.set_status(f'正在加载: {file_path}')
            success = self.data_controller.load_file(file_path)
            if success:
                self.set_status('数据加载成功')
            else:
                self.set_status('数据加载失败')

    def _on_load_folder(self):
        """加载文件夹"""
        folder_path = self.ask_open_folder()
        if folder_path:
            self.set_status(f'正在加载文件夹: {folder_path}')
            success = self.data_controller.load_folder(folder_path)
            if success:
                self.set_status('数据加载成功')
            else:
                self.set_status('数据加载失败')

    def _on_export_data(self):
        """导出数据"""
        file_path = self.ask_save_file(defaultextension='.xlsx')
        if file_path:
            format_type = 'csv' if file_path.endswith('.csv') else 'excel'
            self.data_controller.export_data(file_path, format_type)

    def _on_export_chart(self):
        """导出图表"""
        if self.current_figure is None:
            self.show_warning('警告', '没有可导出的图表')
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG图片', '*.png'), ('JPG图片', '*.jpg'), ('PDF文档', '*.pdf')]
        )

        if file_path:
            fmt = file_path.split('.')[-1]
            self.visualization_controller.save_chart(self.current_figure, file_path, format=fmt)

    def _on_show_overview(self):
        """显示数据概览"""
        data = self.data_manager.get_data()
        if data is None:
            self.show_warning('警告', '请先加载数据')
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

    def _on_show_clean_dialog(self):
        """显示清洗对话框"""
        if not self.data_controller.has_data():
            self.show_warning('警告', '请先加载数据')
            return

        dialog = tk.Toplevel(self.root)
        dialog.title('数据清洗')
        dialog.geometry('400x300')
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text='选择清洗操作:').pack(pady=10)

        ttk.Button(dialog, text='删除重复数据',
                  command=lambda: [self._on_clean_duplicates(), dialog.destroy()]).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(dialog, text='删除缺失值行',
                  command=lambda: [self._on_clean_missing('drop'), dialog.destroy()]).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(dialog, text='填充缺失值(均值)',
                  command=lambda: [self._on_clean_missing('fill_mean'), dialog.destroy()]).pack(fill=tk.X, padx=20, pady=5)

        salary_col = self.salary_var.get() or 'pre_tax_salary'
        ttk.Button(dialog, text='移除异常值',
                  command=lambda: [self._on_remove_outliers(salary_col), dialog.destroy()]).pack(fill=tk.X, padx=20, pady=5)

    def _on_clean_duplicates(self):
        """清洗重复数据"""
        self.data_controller.clean_duplicates()

    def _on_clean_missing(self, strategy: str):
        """清洗缺失值"""
        self.data_controller.clean_missing_values(strategy)

    def _on_remove_outliers(self, column: str):
        """移除异常值"""
        self.data_controller.remove_outliers(column)

    def _on_age_group(self):
        """年龄分组"""
        self.data_controller.create_age_group()

    def _on_salary_group(self):
        """薪资分组"""
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        self.data_controller.create_salary_group(salary_col)

    def _on_experience_group(self):
        """工作年限分组"""
        self.data_controller.create_experience_group()

    def _on_reset_data(self):
        """重置数据"""
        self.data_controller.reset_data()

    def _on_descriptive_stats(self):
        """描述性统计"""
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        self.analysis_controller.get_descriptive_stats(salary_col)

    def _on_frequency_analysis(self):
        """频率分析"""
        dimension = self.dimension_var.get()
        if not dimension:
            self.show_warning('警告', '请选择分析维度')
            return
        self.analysis_controller.get_frequency_analysis(dimension)

    def _on_crosstab(self):
        """交叉分析"""
        dimension = self.dimension_var.get()
        if not dimension:
            self.show_warning('警告', '请选择分析维度')
            return

        data = self.data_manager.get_data()
        if data is None:
            return

        col_col = 'gender' if 'gender' in data.columns else data.columns[0]
        self.analysis_controller.get_crosstab(dimension, col_col)

    def _on_correlation(self):
        """相关性分析"""
        self.analysis_controller.get_correlation_matrix()

    def _on_summary_report(self):
        """汇总报告"""
        salary_col = self.salary_var.get() or 'pre_tax_salary'
        self.analysis_controller.get_summary_report(salary_col)

    def _on_execute_analysis(self):
        """执行分析"""
        dimension = self.dimension_var.get()
        salary_col = self.salary_var.get() or 'pre_tax_salary'

        if dimension:
            self.analysis_controller.compare_by_dimension(dimension, salary_col)
        else:
            self.analysis_controller.get_descriptive_stats(salary_col)

    def _on_generate_chart(self):
        """生成图表"""
        chart_type = self.chart_type_var.get()
        dimension = self.viz_dimension_var.get()
        salary_col = self.salary_var.get() or 'pre_tax_salary'

        if chart_type == 'bar':
            if not dimension:
                self.show_warning('警告', '请选择分组维度')
                return
            self.visualization_controller.create_bar_chart(dimension, salary_col)
        elif chart_type == 'horizontal':
            if not dimension:
                self.show_warning('警告', '请选择分组维度')
                return
            self.visualization_controller.create_horizontal_bar_chart(dimension, salary_col)
        elif chart_type == 'pie':
            if not dimension:
                self.show_warning('警告', '请选择分组维度')
                return
            self.visualization_controller.create_pie_chart(dimension, salary_col)
        elif chart_type == 'line':
            time_col = 'join_year' if 'join_year' in self.data_manager.get_columns() else dimension
            if not time_col:
                self.show_warning('警告', '没有时间字段可用于趋势分析')
                return
            self.visualization_controller.create_line_chart(time_col, salary_col)
        elif chart_type == 'scatter':
            x_col = 'work_years' if 'work_years' in self.data_manager.get_columns() else dimension
            if not x_col:
                self.show_warning('警告', '请选择X轴字段')
                return
            self.visualization_controller.create_scatter_chart(x_col, salary_col)
        elif chart_type == 'boxplot':
            if not dimension:
                self.show_warning('警告', '请选择分组维度')
                return
            self.visualization_controller.create_boxplot(dimension, salary_col)
        elif chart_type == 'histogram':
            self.visualization_controller.create_histogram(salary_col)
        elif chart_type == 'heatmap':
            self.visualization_controller.create_heatmap()

    def _on_show_analysis(self):
        """显示分析标签页"""
        self.notebook.select(self.analysis_frame)

    def _on_show_visualization(self):
        """显示可视化标签页"""
        self.notebook.select(self.visualization_frame)

    def _on_show_help(self):
        """显示帮助"""
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
        self.show_info('使用说明', help_text)

    def _on_show_about(self):
        """显示关于"""
        self.show_info('关于', '园区白领薪资数据分析工具\n\n版本: 2.0.0\n\n基于 Python + Pandas + Matplotlib 构建\n采用MVC架构重构')
