import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, Dict, List, Tuple


class UIComponentFactory:
    """UI组件工厂类，统一创建UI组件"""
    
    @staticmethod
    def create_frame(parent, **kwargs) -> ttk.Frame:
        """创建框架"""
        defaults = {'padding': 10}
        defaults.update(kwargs)
        return ttk.Frame(parent, **defaults)
    
    @staticmethod
    def create_label_frame(parent, text: str = '', **kwargs) -> ttk.LabelFrame:
        """创建标签框架"""
        defaults = {'padding': 10}
        defaults.update(kwargs)
        return ttk.LabelFrame(parent, text=text, **defaults)
    
    @staticmethod
    def create_button(parent, text: str, command: Optional[Callable] = None,
                     width: int = 20, **kwargs) -> ttk.Button:
        """创建按钮"""
        defaults = {'width': width}
        defaults.update(kwargs)
        return ttk.Button(parent, text=text, command=command, **defaults)
    
    @staticmethod
    def create_label(parent, text: str = '', **kwargs) -> ttk.Label:
        """创建标签"""
        defaults = {}
        defaults.update(kwargs)
        return ttk.Label(parent, text=text, **defaults)
    
    @staticmethod
    def create_entry(parent, textvariable: Optional[tk.Variable] = None,
                    width: int = 20, **kwargs) -> ttk.Entry:
        """创建输入框"""
        defaults = {'width': width}
        defaults.update(kwargs)
        return ttk.Entry(parent, textvariable=textvariable, **defaults)
    
    @staticmethod
    def create_combobox(parent, textvariable: Optional[tk.Variable] = None,
                       values: Optional[List] = None, width: int = 15,
                       state: str = 'readonly', **kwargs) -> ttk.Combobox:
        """创建下拉框"""
        defaults = {'width': width, 'state': state}
        defaults.update(kwargs)
        combo = ttk.Combobox(parent, textvariable=textvariable, **defaults)
        if values:
            combo['values'] = values
        return combo
    
    @staticmethod
    def create_treeview(parent, columns: List[str], show: str = 'headings',
                       height: int = 10, **kwargs) -> ttk.Treeview:
        """创建树形视图"""
        defaults = {'height': height, 'show': show}
        defaults.update(kwargs)
        tree = ttk.Treeview(parent, columns=columns, **defaults)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, minwidth=50)
        
        return tree
    
    @staticmethod
    def create_text(parent, height: int = 10, width: int = 50,
                   state: str = tk.NORMAL, **kwargs) -> tk.Text:
        """创建文本框"""
        defaults = {'height': height, 'width': width}
        defaults.update(kwargs)
        text = tk.Text(parent, **defaults)
        if state != tk.NORMAL:
            text.config(state=state)
        return text
    
    @staticmethod
    def create_scrollbar(parent, orient: str = tk.VERTICAL,
                        command: Optional[Callable] = None, **kwargs) -> ttk.Scrollbar:
        """创建滚动条"""
        defaults = {'orient': orient}
        defaults.update(kwargs)
        return ttk.Scrollbar(parent, command=command, **defaults)
    
    @staticmethod
    def create_scrolled_treeview(parent, columns: List[str], **kwargs) -> Tuple[ttk.Treeview, ttk.Scrollbar, ttk.Scrollbar]:
        """创建带滚动条的树形视图"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tree = UIComponentFactory.create_treeview(frame, columns, **kwargs)
        
        vsb = UIComponentFactory.create_scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        hsb = UIComponentFactory.create_scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return tree, vsb, hsb
    
    @staticmethod
    def create_scrolled_text(parent, height: int = 10, width: int = 50,
                            **kwargs) -> tk.Text:
        """创建带滚动条的文本框"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        text = UIComponentFactory.create_text(frame, height=height, width=width, **kwargs)
        scrollbar = UIComponentFactory.create_scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return text
    
    @staticmethod
    def create_notebook(parent, **kwargs) -> ttk.Notebook:
        """创建标签页"""
        return ttk.Notebook(parent, **kwargs)
    
    @staticmethod
    def create_menu(parent) -> tk.Menu:
        """创建菜单"""
        return tk.Menu(parent)
    
    @staticmethod
    def create_status_bar(parent, text: str = '就绪', **kwargs) -> ttk.Label:
        """创建状态栏"""
        defaults = {'text': text, 'relief': tk.SUNKEN, 'anchor': tk.W}
        defaults.update(kwargs)
        return ttk.Label(parent, **defaults)
    
    @staticmethod
    def create_separator(parent, orient: str = tk.HORIZONTAL, **kwargs) -> ttk.Separator:
        """创建分隔线"""
        return ttk.Separator(parent, orient=orient, **kwargs)
    
    @staticmethod
    def create_radio_button(parent, text: str, variable: tk.Variable,
                           value: Any, **kwargs) -> ttk.Radiobutton:
        """创建单选按钮"""
        return ttk.Radiobutton(parent, text=text, variable=variable, value=value, **kwargs)
    
    @staticmethod
    def create_check_button(parent, text: str, variable: tk.Variable,
                           **kwargs) -> ttk.Checkbutton:
        """创建复选按钮"""
        return ttk.Checkbutton(parent, text=text, variable=variable, **kwargs)
    
    @staticmethod
    def create_spinbox(parent, from_: int = 0, to: int = 100,
                      textvariable: Optional[tk.Variable] = None,
                      width: int = 10, **kwargs) -> ttk.Spinbox:
        """创建数字选择框"""
        defaults = {'from_': from_, 'to': to, 'width': width}
        defaults.update(kwargs)
        return ttk.Spinbox(parent, textvariable=textvariable, **defaults)
    
    @staticmethod
    def create_progressbar(parent, mode: str = 'determinate',
                          length: int = 200, **kwargs) -> ttk.Progressbar:
        """创建进度条"""
        defaults = {'mode': mode, 'length': length}
        defaults.update(kwargs)
        return ttk.Progressbar(parent, **defaults)
    
    @staticmethod
    def apply_padding(widget, padx: int = 5, pady: int = 5):
        """为widget应用统一的padding"""
        if hasattr(widget, 'pack'):
            widget.pack_configure(padx=padx, pady=pady)
        elif hasattr(widget, 'grid'):
            widget.grid_configure(padx=padx, pady=pady)
    
    @staticmethod
    def create_form_row(parent, label_text: str, widget: tk.Widget,
                       label_width: int = 15, **kwargs) -> ttk.Frame:
        """创建表单一行（标签+控件）"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        label = ttk.Label(frame, text=label_text, width=label_width)
        label.pack(side=tk.LEFT)
        
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        return frame
