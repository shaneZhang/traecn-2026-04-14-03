import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional
from src.models import Logger


class BaseWidget:
    def __init__(self, parent: tk.Widget, **kwargs):
        self.parent = parent
        self.logger = Logger()
        self._create_variables(**kwargs)
        self._build_ui()
        self._bind_events()

    def _create_variables(self, **kwargs):
        pass

    def _build_ui(self):
        pass

    def _bind_events(self):
        pass

    def show_message(self, title: str, message: str, message_type: str = 'info'):
        from tkinter import messagebox
        if message_type == 'info':
            messagebox.showinfo(title, message)
        elif message_type == 'warning':
            messagebox.showwarning(title, message)
        elif message_type == 'error':
            messagebox.showerror(title, message)
        elif message_type == 'question':
            return messagebox.askyesno(title, message)

    def handle_exception(self, e: Exception, title: str = "错误"):
        self.logger.error(f"{title}: {str(e)}", exc_info=True)
        self.show_message(title, str(e), 'error')


class DialogBase(tk.Toplevel, BaseWidget):
    def __init__(self, parent: tk.Widget, title: str, width: int = 400, height: int = 300, **kwargs):
        tk.Toplevel.__init__(self, parent)
        self.title(title)
        self.geometry(f'{width}x{height}')
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.result: Any = None
        BaseWidget.__init__(self, self, **kwargs)
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def close(self, result: Any = None):
        self.result = result
        self._on_close()
