"""
Детектор синего цвета
"""

from detectors.base_detector import BaseColorDetector


class BlueDetector(BaseColorDetector):
    """Детектор синего цвета"""
    
    def __init__(self, config):
        """
        Args:
            config: Словарь с настройками детекции
        """
        self.min_blue = config['min_blue']
        self.max_red = config['max_red']
        self.max_green = config['max_green']
        self.blue_dominance = config['blue_dominance']
    
    def detect(self, r, g, b):
        """Проверка, является ли цвет синим"""
        # Синий канал должен быть достаточно высоким
        if b < self.min_blue:
            return False
        
        # Красный и зеленый каналы должны быть низкими
        if r > self.max_red or g > self.max_green:
            return False
        
        # Синий должен доминировать
        if b < r + self.blue_dominance or b < g + self.blue_dominance:
            return False
        
        return True
    
    def get_detection_message(self, r, g, b):
        """Сообщение при обнаружении синего"""
        return f"🔵🔵🔵 СИНИЙ! RGB: ({r}, {g}, {b}) 🔵🔵🔵"
    
    def get_name(self):
        """Название детектора"""
        return "Синий"
