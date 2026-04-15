import pandas as pd
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class DataEventType(Enum):
    LOADED = "data_loaded"
    UPDATED = "data_updated"
    CLEANED = "data_cleaned"
    FILTERED = "data_filtered"
    RESET = "data_reset"
    CLEARED = "data_cleared"


@dataclass
class DataEvent:
    event_type: DataEventType
    data_id: str
    timestamp: datetime
    metadata: Dict[str, Any]


class DataManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if DataManager._initialized:
            return

        self._data: Optional[pd.DataFrame] = None
        self._original_data: Optional[pd.DataFrame] = None
        self._subscribers: Dict[DataEventType, List[Callable[[DataEvent], None]]] = {
            event_type: [] for event_type in DataEventType
        }
        self._data_id: str = ""
        self._version: int = 0
        DataManager._initialized = True

    @property
    def has_data(self) -> bool:
        return self._data is not None and not self._data.empty

    @property
    def version(self) -> int:
        return self._version

    def get_data(self) -> Optional[pd.DataFrame]:
        return self._data.copy() if self._data is not None else None

    def get_original_data(self) -> Optional[pd.DataFrame]:
        return self._original_data.copy() if self._original_data is not None else None

    def set_data(self, data: pd.DataFrame, source: str = "unknown"):
        self._data = data.copy()
        self._original_data = data.copy()
        self._version += 1
        self._data_id = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._notify(DataEventType.LOADED, {"source": source, "rows": len(data)})

    def update_data(self, data: pd.DataFrame, reason: str = "update"):
        self._data = data.copy()
        self._version += 1
        self._notify(DataEventType.UPDATED, {"reason": reason, "rows": len(data)})

    def reset_data(self):
        if self._original_data is not None:
            self._data = self._original_data.copy()
            self._version += 1
            self._notify(DataEventType.RESET, {"rows": len(self._data)})

    def clear_data(self):
        self._data = None
        self._original_data = None
        self._version += 1
        self._notify(DataEventType.CLEARED, {})

    def get_column_names(self) -> List[str]:
        if self._data is None:
            return []
        return list(self._data.columns)

    def get_numeric_columns(self) -> List[str]:
        if self._data is None:
            return []
        return self._data.select_dtypes(include=['number']).columns.tolist()

    def get_categorical_columns(self) -> List[str]:
        if self._data is None:
            return []
        return self._data.select_dtypes(include=['object', 'category']).columns.tolist()

    def get_data_info(self) -> Dict[str, Any]:
        if self._data is None:
            return {}

        missing = self._data.isnull().sum()
        return {
            'rows': len(self._data),
            'columns': len(self._data.columns),
            'column_names': list(self._data.columns),
            'missing_values': missing[missing > 0].to_dict(),
            'numeric_columns': self.get_numeric_columns(),
            'categorical_columns': self.get_categorical_columns(),
            'memory_usage': float(self._data.memory_usage(deep=True).sum()),
            'version': self._version
        }

    def subscribe(self, event_type: DataEventType, callback: Callable[[DataEvent], None]):
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: DataEventType, callback: Callable[[DataEvent], None]):
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def _notify(self, event_type: DataEventType, metadata: Dict[str, Any]):
        event = DataEvent(
            event_type=event_type,
            data_id=self._data_id,
            timestamp=datetime.now(),
            metadata=metadata
        )
        for callback in self._subscribers[event_type]:
            try:
                callback(event)
            except Exception as e:
                from .logger import Logger
                Logger().error(f"通知订阅者失败 ({event_type}): {str(e)}", exc_info=True)
