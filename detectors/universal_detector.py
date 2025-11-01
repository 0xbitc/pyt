"""
Универсальный детектор цвета на основе диапазонов RGB
"""

import numpy as np


class UniversalDetector:
    """Универсальный детектор цвета из конфига (ОПТИМИЗИРОВАННЫЙ)"""
    
    def __init__(self, config):
        self.min_rgb = np.array(config.get("min_rgb", [0, 0, 0]), dtype=np.uint8)
        self.max_rgb = np.array(config.get("max_rgb", [255, 255, 255]), dtype=np.uint8)
        self.min_percent = config.get("min_percent", 0.01)
        self.trigger_key = config.get("trigger_key", "a")
        self._last_detected = False
    
    def get_name(self):
        return (f"Universal RGB["
                f"R:{self.min_rgb[0]}-{self.max_rgb[0]}, "
                f"G:{self.min_rgb[1]}-{self.max_rgb[1]}, "
                f"B:{self.min_rgb[2]}-{self.max_rgb[2]}]")
    
    def detect(self, r, g, b, frame=None):
        """БЫСТРАЯ ДЕТЕКЦИЯ"""
        if frame is None:
            return False
        
        # Векторизованная операция (БЫСТРО!)
        mask = np.all((frame >= self.min_rgb) & (frame <= self.max_rgb), axis=-1)
        percent = np.mean(mask)
        detected = percent >= self.min_percent
        self._last_detected = detected
        
        return detected
    
    def get_detection_message(self, r, g, b):
        return f"Обнаружен цвет RGB({r}, {g}, {b})"
    
    def last_detected(self):
        return self._last_detected
