import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import MainWindow
from src.models.config_manager import ConfigManager
from src.models.logger import Logger


def main():
    # 初始化配置管理器
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    config_manager = ConfigManager(config_path)
    
    # 初始化日志管理器
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    logger = Logger(
        name='salary_analysis',
        log_level='INFO',
        log_dir=log_dir,
        console_output=True,
        file_output=True
    )
    
    logger.info("应用启动")
    
    # 创建主窗口
    root = tk.Tk()
    
    # 设置DPI缩放
    try:
        root.tk.call('tk', 'scaling', 1.5)
    except:
        pass
    
    # 创建应用
    app = MainWindow(root)
    
    # 运行主循环
    root.mainloop()
    
    logger.info("应用关闭")


if __name__ == '__main__':
    main()
