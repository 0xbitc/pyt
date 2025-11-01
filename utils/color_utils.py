"""
Утилиты для работы с цветом (ОПТИМИЗИРОВАННЫЕ)
"""

import numpy as np


def rgb_to_hex(r, g, b):
    """Конвертация RGB в HEX (быстро)"""
    return f'#{r:02x}{g:02x}{b:02x}'


def calculate_average_color(frame):
    """
    Вычисление среднего цвета (ОПТИМИЗИРОВАНО)
    НЕ ИСПОЛЬЗУЕТСЯ в критическом пути — можно убрать
    """
    avg = np.mean(frame, axis=(0, 1), dtype=np.int32)
    return int(avg[0]), int(avg[1]), int(avg[2])
