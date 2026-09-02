import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class AuditLogger:
    """
    Класс для логирования всех действий агента в структурированном JSON формате.
    """
    
    def __init__(self, log_file: str = "audit_logs.json", session_id: Optional[str] = None):
        """
        Инициализация AuditLogger.
        
        Args:
            log_file (str): Путь к файлу для сохранения логов
            session_id (str, optional): ID сессии. Если None, генерируется автоматически
        """
        self.log_file = log_file
        self.logs: List[Dict[str, Any]] = []
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self._load_existing_logs()
    
    def _load_existing_logs(self) -> None:
        """Загружает существующие логи из файла."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logs = data.get('logs', [])
            except (json.JSONDecodeError, IOError):
                self.logs = []
    
    def log_request(self, user_query: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Логирует запрос пользователя.
        
        Args:
            user_query (str): Текст запроса
            metadata (Dict, optional): Дополнительные метаданные
            
        Returns:
            Dict: Созданная запись лога
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": "USER_REQUEST",
            "data": {
                "query": user_query,
                "metadata": metadata or {}
            }
        }
        self.logs.append(log_entry)
        self._save_logs()
        return log_entry
    
    def log_plan(self, plan: List[Dict], metadata: Optional[Dict] = None) -> Dict:
        """
        Логирует план действий агента.
        
        Args:
            plan (List[Dict]): Список действий
            metadata (Dict, optional): Дополнительные метаданные
            
        Returns:
            Dict: Созданная запись лога
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": "ACTION_PLAN",
            "data": {
                "plan": plan,
                "steps_count": len(plan),
                "metadata": metadata or {}
            }
        }
        self.logs.append(log_entry)
        self._save_logs()
        return log_entry
    
    def log_tool_execution(self, tool_name: str, tool_input: str, 
                          result: Any, metadata: Optional[Dict] = None) -> Dict:
        """
        Логирует выполнение инструмента.
        
        Args:
            tool_name (str): Название инструмента
            tool_input (str): Входные данные инструмента
            result (Any): Результат выполнения
            metadata (Dict, optional): Дополнительные метаданные
            
        Returns:
            Dict: Созданная запись лога
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": "TOOL_EXECUTION",
            "data": {
                "tool_name": tool_name,
                "input": tool_input,
                "result": str(result)[:1000],
                "metadata": metadata or {}
            }
        }
        self.logs.append(log_entry)
        self._save_logs()
        return log_entry
    
    def log_final_response(self, response: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Логирует финальный ответ агента.
        
        Args:
            response (str): Текст ответа
            metadata (Dict, optional): Дополнительные метаданные
            
        Returns:
            Dict: Созданная запись лога
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": "FINAL_RESPONSE",
            "data": {
                "response": response,
                "response_length": len(response),
                "metadata": metadata or {}
            }
        }
        self.logs.append(log_entry)
        self._save_logs()
        return log_entry
    
    def log_error(self, error_message: str, error_type: str = "GENERAL", 
                  metadata: Optional[Dict] = None) -> Dict:
        """
        Логирует ошибку.
        
        Args:
            error_message (str): Сообщение об ошибке
            error_type (str): Тип ошибки
            metadata (Dict, optional): Дополнительные метаданные
            
        Returns:
            Dict: Созданная запись лога
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": "ERROR",
            "data": {
                "error_type": error_type,
                "error_message": error_message,
                "metadata": metadata or {}
            }
        }
        self.logs.append(log_entry)
        self._save_logs()
        return log_entry
    
    def _save_logs(self) -> None:
        """Сохраняет логи в файл."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": self.session_id,
                    "total_logs": len(self.logs),
                    "logs": self.logs
                }, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving logs: {e}")
    
    def get_logs(self) -> List[Dict]:
        """Получает все логи."""
        return self.logs
    
    def get_logs_by_event_type(self, event_type: str) -> List[Dict]:
        """Получает логи по типу события."""
        return [log for log in self.logs if log.get('event_type') == event_type]
    
    def clear_logs(self) -> None:
        """Очищает все логи."""
        self.logs = []
        self._save_logs()
    
    def get_statistics(self) -> Dict:
        """Получает статистику по логам."""
        stats = {
            "total_logs": len(self.logs),
            "event_types": {}
        }
        
        for log in self.logs:
            event_type = log.get('event_type', 'UNKNOWN')
            stats["event_types"][event_type] = stats["event_types"].get(event_type, 0) + 1
        
        return stats