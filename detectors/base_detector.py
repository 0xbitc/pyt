"""
Базовый класс для детекторов цвета
"""

from abc import ABC, abstractmethod


class BaseColorDetector(ABC):
    """Абстрактный класс для детекторов цвета"""
    
    @abstractmethod
    def detect(self, r, g, b):
        """
        Проверка, соответствует ли цвет критериям детектора
        
        Args:
            r: Красный канал (0-255)
            g: Зеленый канал (0-255)
            b: Синий канал (0-255)
        
        Returns:
            bool: True если цвет соответствует, False иначе
        """
        pass
    
    @abstractmethod
    def get_detection_message(self, r, g, b):
        """
        Получить сообщение при обнаружении
        
        Args:
            r, g, b: RGB значения
        
        Returns:
            str: Сообщение для вывода
        """
        pass
    
    @abstractmethod
    def get_name(self):
        """
        Получить название детектора
        
        Returns:
            str: Название
        """
        pass
