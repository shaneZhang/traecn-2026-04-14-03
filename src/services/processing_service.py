import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from src.models import DataManager, ConfigManager, Logger
from src.core import DataProcessorCore
from src.core.exceptions import DataProcessingError


class ProcessingService:
    def __init__(self):
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.processor_core = DataProcessorCore()

        grouping_config = self.config_manager.get('grouping', {})
        if grouping_config:
            self.processor_core.config.update(grouping_config)

    def _update_data(self, new_data: pd.DataFrame, reason: str):
        self.data_manager.update_data(new_data, reason)

    def remove_duplicates(self, subset: Optional[List[str]] = None) -> int:
        if not self.data_manager.has_data:
            raise DataProcessingError("没有可处理的数据")

        data = self.data_manager.get_data()
        result, count = self.processor_core.remove_duplicates(data, subset)
        self._update_data(result, f"remove_duplicates: removed {count} rows")
        self.logger.info(f"删除了 {count} 条重复记录")
        return count

    def handle_missing_values(self, strategy: str = 'drop',
                              columns: Optional[List[str]] = None,
                              fill_value: Any = None) -> Dict[str, int]:
        if not self.data_manager.has_data:
            raise DataProcessingError("没有可处理的数据")

        data = self.data_manager.get_data()
        result, processed = self.processor_core.handle_missing_values(
            data, strategy, columns, fill_value
        )
        self._update_data(result, f"handle_missing_values: {strategy}")
        self.logger.info(f"缺失值处理完成: {list(processed.keys())}")
        return processed

    def remove_outliers(self, column: str) -> int:
        if not self.data_manager.has_data:
            raise DataProcessingError("没有可处理的数据")

        data = self.data_manager.get_data()
        method = self.config_manager.get('processing.outlier_method', 'iqr')
        threshold = self.config_manager.get('processing.outlier_threshold', 1.5)

        result, count = self.processor_core.remove_outliers(
            data, column, method, threshold
        )
        self._update_data(result, f"remove_outliers: {column}")
        self.logger.info(f"移除了 {count} 条 {column} 异常值记录")
        return count

    def create_age_group(self, age_column: str = 'age') -> bool:
        if not self.data_manager.has_data:
            raise DataProcessingError("没有可处理的数据")

        data = self.data_manager.get_data()
        result = self.processor_core.create_age_group(data, age_column)
        self._update_data(result, "create_age_group")
        self.logger.info("创建年龄分组完成")
        return True

    def create_salary_group(self, salary_column: str = 'pre_tax_salary') -> bool:
        if not self.data_manager.has_data:
            raise DataProcessingError("没有可处理的数据")

        data = self.data_manager.get_data()
        result = self.processor_core.create_salary_group(data, salary_column)
        self._update_data(result, "create_salary_group")
        self.logger.info("创建薪资分组完成")
        return True

    def create_work_experience_group(self, years_column: str = 'work_years') -> bool:
        if not self.data_manager.has_data:
            raise DataProcessingError("没有可处理的数据")

        data = self.data_manager.get_data()
        result = self.processor_core.create_work_experience_group(data, years_column)
        self._update_data(result, "create_work_experience_group")
        self.logger.info("创建工作年限分组完成")
        return True

    def reset_data(self):
        self.data_manager.reset_data()
        self.logger.info("数据已重置")

    def get_data_summary(self) -> Dict[str, Any]:
        if not self.data_manager.has_data:
            return {}
        data = self.data_manager.get_data()
        return self.processor_core.get_data_summary(data)

    def filter_data(self, conditions: Dict[str, Any]) -> pd.DataFrame:
        if not self.data_manager.has_data:
            return pd.DataFrame()
        data = self.data_manager.get_data()
        return self.processor_core.filter_data(data, conditions)
