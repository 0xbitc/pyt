"""
Конфигурация приложения
"""

# Параметры окна захвата
CAPTURE_WIDTH = 80
CAPTURE_HEIGHT = 10
BORDER_WIDTH = 3

# Параметры захвата (МАКСИМАЛЬНАЯ СКОРОСТЬ)
TARGET_FPS = 300  # Увеличили до 300 для минимальной задержки

# Параметры логирования (ОТКЛЮЧЕНО)
LOG_EVERY_N_FRAMES = 99999  # Практически не логируем

# Настройки детекции синего цвета
BLUE_DETECTION = {
    'min_blue': 100,
    'max_red': 100,
    'max_green': 100,
    'blue_dominance': 50
}

# Параметры overlay (окна) - убраны, теперь в detector_config.json
# OVERLAY_RIGHT_PANEL_WIDTH и OVERLAY_COLOR_SQUARE_SIZE теперь в detector_config.json

# Параметры производительности (УБРАНО - не используется)
# UI_UPDATE_INTERVAL = 5
