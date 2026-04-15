import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, Any, Dict, List


class BaseView:
    """视图基类"""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.frame: Optional[ttk.Frame] = None
    
    def create(self) -> ttk.Frame:
        """创建视图框架，子类需要重写此方法"""
        raise NotImplementedError("子类必须实现create方法")
    
    def show(self):
        """显示视图"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """隐藏视图"""
        if self.frame:
            self.frame.pack_forget()
    
    def destroy(self):
        """销毁视图"""
        if self.frame:
            self.frame.destroy()
            self.frame = None
    
    def update(self, **kwargs):
        """更新视图，子类可以重写此方法"""
        pass


class DialogMixin:
    """对话框混入类"""
    
    @staticmethod
    def show_info(title: str, message: str):
        """显示信息对话框"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str):
        """显示警告对话框"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_error(title: str, message: str):
        """显示错误对话框"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """询问是/否"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def ask_ok_cancel(title: str, message: str) -> bool:
        """询问确定/取消"""
        return messagebox.askokcancel(title, message)
    
    @staticmethod
    def ask_open_file(title: str = '选择文件',
                     filetypes: Optional[List[tuple]] = None) -> Optional[str]:
        """询问打开文件"""
        if filetypes is None:
            filetypes = [('Excel文件', '*.xlsx *.xls'), ('所有文件', '*.*')]
        
        return filedialog.askopenfilename(title=title, filetypes=filetypes)
    
    @staticmethod
    def ask_open_folder(title: str = '选择文件夹') -> Optional[str]:
        """询问打开文件夹"""
        return filedialog.askdirectory(title=title)
    
    @staticmethod
    def ask_save_file(title: str = '保存文件',
                     defaultextension: str = '.xlsx',
                     filetypes: Optional[List[tuple]] = None) -> Optional[str]:
        """询问保存文件"""
        if filetypes is None:
            filetypes = [('Excel文件', '*.xlsx'), ('CSV文件', '*.csv'), ('所有文件', '*.*')]
        
        return filedialog.asksaveasfilename(
            title=title,
            defaultextension=defaultextension,
            filetypes=filetypes
        )
    
    @staticmethod
    def show_custom_dialog(parent: tk.Widget, title: str, 
                          content_widget: tk.Widget,
                          ok_callback: Optional[Callable] = None,
                          cancel_callback: Optional[Callable] = None):
        """显示自定义对话框"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry('400x300')
        dialog.transient(parent)
        dialog.grab_set()
        
        content_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_ok():
            if ok_callback:
                ok_callback()
            dialog.destroy()
        
        def on_cancel():
            if cancel_callback:
                cancel_callback()
            dialog.destroy()
        
        ttk.Button(button_frame, text='确定', command=on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text='取消', command=on_cancel).pack(side=tk.RIGHT, padx=5)
        
        dialog.wait_window()


class StatusBarMixin:
    """状态栏混入类"""
    
    def __init__(self):
        self._status_bar: Optional[ttk.Label] = None
    
    def create_status_bar(self, parent: tk.Widget, text: str = '就绪') -> ttk.Label:
        """创建状态栏"""
        self._status_bar = ttk.Label(
            parent,
            text=text,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        return self._status_bar
    
    def set_status(self, text: str):
        """设置状态栏文本"""
        if self._status_bar:
            self._status_bar.config(text=text)
    
    def clear_status(self):
        """清除状态栏文本"""
        if self._status_bar:
            self._status_bar.config(text='就绪')


class DataViewMixin:
    """数据视图混入类"""
    
    def create_data_tree(self, parent: tk.Widget, columns: List[str],
                        height: int = 20) -> ttk.Treeview:
        """创建数据表格"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=height)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, minwidth=50)
        
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return tree
    
    def populate_tree(self, tree: ttk.Treeview, data: Any, max_rows: int = 100):
        """填充树形视图数据"""
        tree.delete(*tree.get_children())
        
        if hasattr(data, 'iterrows'):
            for idx, row in list(data.iterrows())[:max_rows]:
                values = [str(v) for v in row.values]
                tree.insert('', tk.END, values=values)
        elif isinstance(data, list):
            for row in data[:max_rows]:
                values = [str(v) for v in row]
                tree.insert('', tk.END, values=values)
    
    def create_result_text(self, parent: tk.Widget, height: int = 20) -> tk.Text:
        """创建结果显示文本框"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(frame, height=height, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return text
    
    def display_result(self, text_widget: tk.Text, content: str):
        """在文本框中显示结果"""
        text_widget.delete('1.0', tk.END)
        text_widget.insert('1.0', content)
