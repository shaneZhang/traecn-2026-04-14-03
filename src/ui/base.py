import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, Callable, List


class UIComponentFactory:
    _style_configured = False
    
    @classmethod
    def configure_styles(cls) -> None:
        if cls._style_configured:
            return
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10), relief='sunken')
        style.configure('Action.TButton', font=('Arial', 10), padding=5)
        style.configure('Menu.TButton', font=('Arial', 10), padding=10)
        
        cls._style_configured = True
    
    @classmethod
    def create_label(cls, parent: tk.Widget, text: str, style: str = None,
                    **kwargs) -> ttk.Label:
        if style:
            return ttk.Label(parent, text=text, style=style, **kwargs)
        return ttk.Label(parent, text=text, **kwargs)
    
    @classmethod
    def create_button(cls, parent: tk.Widget, text: str, command: Callable,
                     style: str = 'Action.TButton', width: int = None,
                     **kwargs) -> ttk.Button:
        if width:
            kwargs['width'] = width
        return ttk.Button(parent, text=text, command=command, style=style, **kwargs)
    
    @classmethod
    def create_entry(cls, parent: tk.Widget, textvariable: tk.StringVar = None,
                    width: int = 20, **kwargs) -> ttk.Entry:
        if textvariable:
            return ttk.Entry(parent, textvariable=textvariable, width=width, **kwargs)
        return ttk.Entry(parent, width=width, **kwargs)
    
    @classmethod
    def create_combobox(cls, parent: tk.Widget, textvariable: tk.StringVar = None,
                       values: List[str] = None, width: int = 15,
                       **kwargs) -> ttk.Combobox:
        cb_kwargs = {'width': width}
        if textvariable:
            cb_kwargs['textvariable'] = textvariable
        if values:
            cb_kwargs['values'] = values
        cb_kwargs.update(kwargs)
        return ttk.Combobox(parent, **cb_kwargs)
    
    @classmethod
    def create_text(cls, parent: tk.Widget, height: int = 10, width: int = 50,
                   state: str = 'normal', **kwargs) -> tk.Text:
        text = tk.Text(parent, height=height, width=width, **kwargs)
        if state == 'disabled':
            text.config(state=state)
        return text
    
    @classmethod
    def create_treeview(cls, parent: tk.Widget, columns: List[str] = None,
                       show: str = 'tree headings', **kwargs) -> ttk.Treeview:
        tree = ttk.Treeview(parent, show=show, **kwargs)
        if columns:
            tree['columns'] = columns
        return tree
    
    @classmethod
    def create_frame(cls, parent: tk.Widget, padding: int = 0,
                    **kwargs) -> ttk.Frame:
        if padding:
            kwargs['padding'] = padding
        return ttk.Frame(parent, **kwargs)
    
    @classmethod
    def create_labelframe(cls, parent: tk.Widget, text: str, padding: int = 10,
                         **kwargs) -> ttk.LabelFrame:
        return ttk.LabelFrame(parent, text=text, padding=padding, **kwargs)
    
    @classmethod
    def create_notebook(cls, parent: tk.Widget, **kwargs) -> ttk.Notebook:
        return ttk.Notebook(parent, **kwargs)
    
    @classmethod
    def create_scrollbar(cls, parent: tk.Widget, orient: str = 'vertical',
                        command: Callable = None, **kwargs) -> ttk.Scrollbar:
        sb = ttk.Scrollbar(parent, orient=orient, **kwargs)
        if command:
            sb.config(command=command)
        return sb
    
    @classmethod
    def create_menu_button_group(cls, parent: tk.Widget, 
                                buttons: List,
                                pack_kwargs: Dict = None) -> ttk.Frame:
        frame = cls.create_frame(parent)
        
        for btn_config in buttons:
            if isinstance(btn_config, tuple):
                text = btn_config[0] if len(btn_config) > 0 else ''
                command = btn_config[1] if len(btn_config) > 1 else None
                width = 20
            else:
                text = btn_config.get('text', '')
                command = btn_config.get('command', None)
                width = btn_config.get('width', 20)
            
            btn = cls.create_button(frame, text=text, command=command, width=width)
            btn.pack(pady=5, padx=10, fill=tk.X)
        
        if pack_kwargs:
            frame.pack(**pack_kwargs)
        
        return frame
    
    @classmethod
    def create_info_panel(cls, parent: tk.Widget, title: str = '信息',
                         height: int = 15, width: int = 25) -> Dict[str, tk.Widget]:
        frame = cls.create_labelframe(parent, text=title)
        text = cls.create_text(frame, height=height, width=width, state='disabled')
        text.pack(fill=tk.BOTH, expand=True)
        
        return {'frame': frame, 'text': text}
    
    @classmethod
    def create_status_bar(cls, parent: tk.Widget, initial_text: str = '就绪') -> ttk.Label:
        status = ttk.Label(parent, text=initial_text, style='Status.TLabel', 
                          relief='sunken', anchor='w')
        return status


class BaseDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, title: str, size: tuple = (400, 300)):
        super().__init__(parent)
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self._create_widgets()
        
        self.wait_window()
    
    def _create_widgets(self) -> None:
        pass
    
    def get_result(self) -> Any:
        return self.result


class BaseTab(ttk.Frame):
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        pass
    
    def refresh(self) -> None:
        pass
    
    def clear(self) -> None:
        pass


class ObservableMixin:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, callback: Callable) -> None:
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable) -> None:
        if callback in self._observers:
            self._observers.remove(callback)
    
    def notify_observers(self, *args, **kwargs) -> None:
        for callback in self._observers:
            try:
                callback(*args, **kwargs)
            except Exception:
                pass
