class SalaryAnalysisError(Exception):
    pass


class DataError(SalaryAnalysisError):
    pass


class DataLoadError(DataError):
    pass


class DataValidationError(DataError):
    pass


class DataProcessingError(DataError):
    pass


class AnalysisError(SalaryAnalysisError):
    pass


class VisualizationError(SalaryAnalysisError):
    pass


class ExportError(SalaryAnalysisError):
    pass


class ConfigError(SalaryAnalysisError):
    pass
