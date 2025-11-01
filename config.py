"""
Конфигурация приложения
"""

# Параметры окна захвата
CAPTURE_WIDTH = 80
CAPTURE_HEIGHT = 10
BORDER_WIDTH = 3

# Параметры захвата
TARGET_FPS = 120
LOG_EVERY_N_FRAMES = 30

# Настройки детекции синего цвета
BLUE_DETECTION = {
    'min_blue': 100,
    'max_red': 100,
    'max_green': 100,
    'blue_dominance': 50
}

# Параметры overlay (окна)
OVERLAY_RIGHT_PANEL_WIDTH = 180  # Ширина правой панели с информацией
OVERLAY_COLOR_SQUARE_SIZE = 60   # Размер цветного квадрата
