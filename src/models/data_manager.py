import pandas as pd
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class DataChangeType(Enum):
    LOADED = "loaded"
    UPDATED = "updated"
    FILTERED = "filtered"
    CLEANED = "cleaned"
    GROUPED = "grouped"
    RESET = "reset"


@dataclass
class DataChangeEvent:
    change_type: DataChangeType
    data: Optional[pd.DataFrame]
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if DataManager._initialized:
            return

        self._data: Optional[pd.DataFrame] = None
        self._original_data: Optional[pd.DataFrame] = None
        self._subscribers: List[Callable[[DataChangeEvent], None]] = []
        self._metadata: Dict[str, Any] = {}
        
        DataManager._initialized = True

    def load_data(self, data: pd.DataFrame, source: Optional[str] = None) -> 'DataManager':
        self._original_data = data.copy()
        self._data = data.copy()
        self._metadata = {
            'source': source,
            'original_rows': len(data),
            'original_columns': list(data.columns)
        }
        
        self._notify_subscribers(DataChangeEvent(
            change_type=DataChangeType.LOADED,
            data=self._data.copy(),
            metadata=self._metadata.copy()
        ))
        
        return self

    def update_data(self, data: pd.DataFrame, change_type: DataChangeType = DataChangeType.UPDATED,
                    metadata: Optional[Dict[str, Any]] = None) -> 'DataManager':
        self._data = data.copy()
        
        event_metadata = metadata or {}
        event_metadata.update({
            'current_rows': len(data),
            'current_columns': list(data.columns)
        })
        
        self._notify_subscribers(DataChangeEvent(
            change_type=change_type,
            data=self._data.copy(),
            metadata=event_metadata
        ))
        
        return self

    def get_data(self) -> Optional[pd.DataFrame]:
        return self._data.copy() if self._data is not None else None

    def get_original_data(self) -> Optional[pd.DataFrame]:
        return self._original_data.copy() if self._original_data is not None else None

    def reset_data(self) -> 'DataManager':
        if self._original_data is not None:
            self._data = self._original_data.copy()
            
            self._notify_subscribers(DataChangeEvent(
                change_type=DataChangeType.RESET,
                data=self._data.copy(),
                metadata={'reset_to_original': True}
            ))
        
        return self

    def has_data(self) -> bool:
        return self._data is not None and not self._data.empty

    def get_row_count(self) -> int:
        return len(self._data) if self._data is not None else 0

    def get_column_count(self) -> int:
        return len(self._data.columns) if self._data is not None else 0

    def get_columns(self) -> List[str]:
        return list(self._data.columns) if self._data is not None else []

    def get_numeric_columns(self) -> List[str]:
        if self._data is None:
            return []
        return self._data.select_dtypes(include=['number']).columns.tolist()

    def get_categorical_columns(self) -> List[str]:
        if self._data is None:
            return []
        return self._data.select_dtypes(include=['object', 'category']).columns.tolist()

    def get_column_info(self) -> Dict[str, Dict[str, Any]]:
        if self._data is None:
            return {}
        
        info = {}
        for col in self._data.columns:
            info[col] = {
                'dtype': str(self._data[col].dtype),
                'null_count': int(self._data[col].isnull().sum()),
                'unique_count': int(self._data[col].nunique())
            }
        
        return info

    def get_data_summary(self) -> Dict[str, Any]:
        if self._data is None:
            return {
                'has_data': False,
                'row_count': 0,
                'column_count': 0,
                'columns': []
            }
        
        return {
            'has_data': True,
            'row_count': len(self._data),
            'column_count': len(self._data.columns),
            'columns': list(self._data.columns),
            'numeric_columns': self.get_numeric_columns(),
            'categorical_columns': self.get_categorical_columns(),
            'null_count': int(self._data.isnull().sum().sum()),
            'memory_usage': self._data.memory_usage(deep=True).sum()
        }

    def subscribe(self, callback: Callable[[DataChangeEvent], None]) -> Callable[[], None]:
        self._subscribers.append(callback)
        
        def unsubscribe():
            if callback in self._subscribers:
                self._subscribers.remove(callback)
        
        return unsubscribe

    def _notify_subscribers(self, event: DataChangeEvent):
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                print(f"通知订阅者时出错: {e}")

    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def set_metadata(self, key: str, value: Any):
        self._metadata[key] = value

    @classmethod
    def get_instance(cls) -> 'DataManager':
        if cls._instance is None:
            return cls()
        return cls._instance


def get_data_manager() -> DataManager:
    return DataManager.get_instance()
