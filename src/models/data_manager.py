from typing import Optional, Callable, Dict, Any, List
import pandas as pd
from enum import Enum
import threading
import copy


class DataEventType(Enum):
    DATA_LOADED = "data_loaded"
    DATA_UPDATED = "data_updated"
    DATA_CLEARED = "data_cleared"
    DATA_RESET = "data_reset"


class DataEvent:
    def __init__(self, event_type: DataEventType, data: Optional[pd.DataFrame] = None, 
                 message: str = ""):
        self.event_type = event_type
        self.data = data
        self.message = message


class DataManager:
    def __init__(self):
        self._current_data: Optional[pd.DataFrame] = None
        self._original_data: Optional[pd.DataFrame] = None
        self._subscribers: List[Callable[[DataEvent], None]] = []
        self._lock = threading.RLock()
        self._metadata: Dict[str, Any] = {}
    
    def get_data(self) -> Optional[pd.DataFrame]:
        with self._lock:
            if self._current_data is not None:
                return self._current_data.copy()
            return None
    
    def get_original_data(self) -> Optional[pd.DataFrame]:
        with self._lock:
            if self._original_data is not None:
                return self._original_data.copy()
            return None
    
    def set_data(self, data: pd.DataFrame, is_original: bool = False, 
                 notify: bool = True, message: str = "") -> None:
        event = None
        with self._lock:
            self._current_data = data.copy()
            if is_original:
                self._original_data = data.copy()
            
            if notify:
                event_type = DataEventType.DATA_LOADED if is_original else DataEventType.DATA_UPDATED
                event = DataEvent(event_type, self._current_data.copy(), message)
        
        if event is not None:
            self._notify_subscribers(event)
    
    def update_data(self, data: pd.DataFrame, message: str = "") -> None:
        self.set_data(data, is_original=False, notify=True, message=message)
    
    def clear_data(self) -> None:
        event = None
        with self._lock:
            self._current_data = None
            self._original_data = None
            self._metadata.clear()
            event = DataEvent(DataEventType.DATA_CLEARED, None, "数据已清空")
        
        if event is not None:
            self._notify_subscribers(event)
    
    def reset_data(self) -> bool:
        event = None
        with self._lock:
            if self._original_data is not None:
                self._current_data = self._original_data.copy()
                event = DataEvent(DataEventType.DATA_RESET, self._current_data.copy(), "数据已重置")
                return True
            return False
        
        if event is not None:
            self._notify_subscribers(event)
        
        return event is not None
    
    def subscribe(self, callback: Callable[[DataEvent], None]) -> None:
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[DataEvent], None]) -> None:
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
    
    def _notify_subscribers(self, event: DataEvent) -> None:
        subscribers_copy = []
        with self._lock:
            subscribers_copy = self._subscribers.copy()
        
        for callback in subscribers_copy:
            try:
                callback(event)
            except Exception:
                pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        with self._lock:
            self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._metadata.get(key, default)
    
    def get_data_info(self) -> Dict[str, Any]:
        with self._lock:
            if self._current_data is None:
                return {
                    'has_data': False,
                    'rows': 0,
                    'columns': 0,
                    'column_names': [],
                    'missing_values': {}
                }
            
            return {
                'has_data': True,
                'rows': len(self._current_data),
                'columns': len(self._current_data.columns),
                'column_names': list(self._current_data.columns),
                'dtypes': self._current_data.dtypes.astype(str).to_dict(),
                'missing_values': self._current_data.isnull().sum().to_dict(),
                'memory_usage': self._current_data.memory_usage(deep=True).sum()
            }
    
    def has_data(self) -> bool:
        with self._lock:
            return self._current_data is not None and len(self._current_data) > 0
    
    def get_row_count(self) -> int:
        with self._lock:
            if self._current_data is not None:
                return len(self._current_data)
            return 0
    
    def get_column_names(self) -> List[str]:
        with self._lock:
            if self._current_data is not None:
                return list(self._current_data.columns)
            return []
    
    def get_categorical_columns(self) -> List[str]:
        with self._lock:
            if self._current_data is None:
                return []
            return self._current_data.select_dtypes(
                include=['object', 'category']
            ).columns.tolist()
    
    def get_numeric_columns(self) -> List[str]:
        with self._lock:
            if self._current_data is None:
                return []
            return self._current_data.select_dtypes(include=['number']).columns.tolist()
