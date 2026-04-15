"""
园区白领薪资数据分析工具 - 重构版本

采用MVC + 服务层架构模式：
- models: 数据模型层（DataManager, ConfigManager, Logger）
- services: 服务层（DataService, ProcessingService, AnalysisService, VisualizationService）
- controllers: 控制器层（DataController, AnalysisController, VisualizationController）
- ui: 视图层（MainWindow, UIComponentFactory等）
- utils: 工具类（异常类等）
"""

__version__ = '2.0.0'
__author__ = 'Salary Analysis Team'
