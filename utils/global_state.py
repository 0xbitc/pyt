"""
Модуль для управления глобальным состоянием между экземплярами
"""

import json
import os
import threading
import time


class GlobalState:
    """Класс для синхронизации состояния между экземплярами программы"""
    
    STATE_FILE = "global_state.json"
    
    def __init__(self):
        self.observers = []
        self.monitoring = False
        self.monitor_thread = None
        self._last_state = None
    
    def get_active(self):
        """Получить текущее состояние активности"""
        try:
            if os.path.exists(self.STATE_FILE):
                with open(self.STATE_FILE, "r") as f:
                    data = json.load(f)
                return data.get("active", True)
        except:
            pass
        return True
    
    def set_active(self, active):
        """Установить состояние активности"""
        try:
            with open(self.STATE_FILE, "w") as f:
                json.dump({"active": active}, f)
        except:
            pass
    
    def toggle_active(self):
        """Переключить состояние активности"""
        current = self.get_active()
        new_state = not current
        self.set_active(new_state)
        return new_state
    
    def add_observer(self, callback):
        """Добавить наблюдателя за изменениями состояния"""
        self.observers.append(callback)
    
    def start_monitoring(self):
        """Запустить мониторинг изменений файла состояния"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.monitoring = False
    
    def _monitor_loop(self):
        """Цикл мониторинга изменений состояния"""
        while self.monitoring:
            current_state = self.get_active()
            if current_state != self._last_state:
                self._last_state = current_state
                # Уведомляем всех наблюдателей
                for callback in self.observers:
                    try:
                        callback(current_state)
                    except:
                        pass
            time.sleep(1.0)  # Проверяем раз в секунду (меньше нагрузка)
