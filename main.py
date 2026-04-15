import tkinter as tk
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui import MainWindow


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
