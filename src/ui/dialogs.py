import tkinter as tk
from tkinter import ttk
from typing import Callable
from .base import DialogBase
from .factory import WidgetFactory


class DataCleanDialog(DialogBase):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, '数据清洗', width=400, height=320)

    def _build_ui(self):
        ttk.Label(self, text='选择清洗操作:', font=('Arial', 12)).pack(pady=15)

        buttons = [
            ('删除重复数据', 'duplicates'),
            ('删除缺失值行', 'missing'),
            ('填充缺失值(均值)', 'fill_mean'),
            ('移除异常值', 'outliers')
        ]

        for text, op in buttons:
            btn = ttk.Button(
                self, text=text,
                command=lambda o=op: self.close(o),
                width=30
            )
            btn.pack(pady=5, padx=30, fill=tk.X)


class DataGroupDialog(DialogBase):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, '数据分组', width=400, height=280)

    def _build_ui(self):
        ttk.Label(self, text='选择分组操作:', font=('Arial', 12)).pack(pady=15)

        buttons = [
            ('年龄分组', 'age'),
            ('薪资分组', 'salary'),
            ('工作年限分组', 'experience')
        ]

        for text, op in buttons:
            btn = ttk.Button(
                self, text=text,
                command=lambda o=op: self.close(o),
                width=30
            )
            btn.pack(pady=5, padx=30, fill=tk.X)
