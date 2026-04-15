class SalaryAnalysisError(Exception):
    """基础异常类"""
    pass


class DataLoadError(SalaryAnalysisError):
    """数据加载异常"""
    pass


class DataProcessError(SalaryAnalysisError):
    """数据处理异常"""
    pass


class DataAnalysisError(SalaryAnalysisError):
    """数据分析异常"""
    pass


class VisualizationError(SalaryAnalysisError):
    """可视化异常"""
    pass


class ConfigError(SalaryAnalysisError):
    """配置异常"""
    pass
