"""
Универсальный детектор цвета на основе диапазонов RGB
"""

import numpy as np


class UniversalDetector:
    """Универсальный детектор (ОПТИМИЗИРОВАННЫЙ)"""
    
    def __init__(self, config):
        self.min_rgb = np.array(config.get("min_rgb", [0, 0, 0]), dtype=np.uint8)
        self.max_rgb = np.array(config.get("max_rgb", [255, 255, 255]), dtype=np.uint8)
        self.min_percent = config.get("min_percent", 0.01)
        self.trigger_key = config.get("trigger_key", "a")
        self._last_detected = False
        
        # Предварительное создание масок для скорости
        self._min_rgb_broadcast = self.min_rgb.reshape(1, 1, 3)
        self._max_rgb_broadcast = self.max_rgb.reshape(1, 1, 3)
    
    def get_name(self):
        return f"Universal [{self.min_rgb[0]}-{self.max_rgb[0]},{self.min_rgb[1]}-{self.max_rgb[1]},{self.min_rgb[2]}-{self.max_rgb[2]}]"
    
    def detect(self, r, g, b, frame=None):
        """БЫСТРАЯ ДЕТЕКЦИЯ (игнорируем r,g,b — работаем только с frame)"""
        if frame is None:
            return False
        
        # Векторизованная операция (максимально быстро)
        mask = np.all((frame >= self._min_rgb_broadcast) & (frame <= self._max_rgb_broadcast), axis=2)
        percent = np.mean(mask)
        detected = percent >= self.min_percent
        self._last_detected = detected
        
        return detected
    
    def get_detection_message(self, r, g, b):
        return f"Обнаружен цвет"
    
    def last_detected(self):
        return self._last_detected
