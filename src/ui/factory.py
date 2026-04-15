import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Any, Optional, Tuple, Dict


class WidgetFactory:
    @staticmethod
    def create_button(parent: tk.Widget, text: str, command: Optional[Callable] = None,
                      width: int = None, style: str = None) -> ttk.Button:
        kwargs = {}
        if width:
            kwargs['width'] = width
        if style:
            kwargs['style'] = style
        if command:
            kwargs['command'] = command
        return ttk.Button(parent, text=text, **kwargs)

    @staticmethod
    def create_label(parent: tk.Widget, text: str, font: Tuple = None,
                     anchor: str = None) -> ttk.Label:
        kwargs = {}
        if font:
            kwargs['font'] = font
        if anchor:
            kwargs['anchor'] = anchor
        return ttk.Label(parent, text=text, **kwargs)

    @staticmethod
    def create_combobox(parent: tk.Widget, textvariable: tk.StringVar = None,
                        values: List[str] = None, width: int = 15,
                        state: str = 'readonly') -> ttk.Combobox:
        kwargs = {'width': width, 'state': state}
        if textvariable:
            kwargs['textvariable'] = textvariable
        if values:
            kwargs['values'] = values
        return ttk.Combobox(parent, **kwargs)

    @staticmethod
    def create_text(parent: tk.Widget, height: int = 10, width: int = 50,
                    wrap: str = tk.WORD, state: str = tk.NORMAL) -> tk.Text:
        return tk.Text(parent, height=height, width=width, wrap=wrap, state=state)

    @staticmethod
    def create_frame(parent: tk.Widget, padding: int = 10) -> ttk.Frame:
        return ttk.Frame(parent, padding=padding)

    @staticmethod
    def create_labelframe(parent: tk.Widget, text: str, padding: int = 10) -> ttk.LabelFrame:
        return ttk.LabelFrame(parent, text=text, padding=padding)

    @staticmethod
    def create_scrollbar(parent: tk.Widget, orient: str, command: Callable) -> ttk.Scrollbar:
        return ttk.Scrollbar(parent, orient=orient, command=command)

    @staticmethod
    def create_treeview(parent: tk.Widget, columns: List[str] = None,
                        show: str = 'tree headings') -> ttk.Treeview:
        tree = ttk.Treeview(parent, show=show)
        if columns:
            tree['columns'] = columns
        return tree

    @staticmethod
    def create_notebook(parent: tk.Widget) -> ttk.Notebook:
        return ttk.Notebook(parent)

    @staticmethod
    def create_separator(parent: tk.Widget, orient: str = tk.HORIZONTAL) -> ttk.Separator:
        return ttk.Separator(parent, orient=orient)

    @staticmethod
    def create_button_group(parent: tk.Widget, buttons: List[Tuple[str, Callable]],
                            vertical: bool = True, padding: int = 5) -> ttk.Frame:
        frame = ttk.Frame(parent)
        for text, command in buttons:
            btn = ttk.Button(frame, text=text, command=command, width=20)
            if vertical:
                btn.pack(pady=padding, padx=10, fill=tk.X)
            else:
                btn.pack(side=tk.LEFT, padx=padding, pady=10)
        return frame

    @staticmethod
    def create_menu_bar(parent: tk.Widget, menus: Dict[str, List[Tuple[str, Callable]]]) -> tk.Menu:
        menubar = tk.Menu(parent)

        for menu_label, items in menus.items():
            menu = tk.Menu(menubar, tearoff=0)
            for item_label, command in items:
                if item_label == '---':
                    menu.add_separator()
                else:
                    menu.add_command(label=item_label, command=command)
            menubar.add_cascade(label=menu_label, menu=menu)

        return menubar

    @staticmethod
    def set_status_bar(parent: tk.Widget, text: str) -> ttk.Label:
        status_bar = ttk.Label(parent, text=text, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        return status_bar
