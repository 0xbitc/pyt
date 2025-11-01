"""
Конфигурация приложения
"""

# Параметры окна захвата
CAPTURE_WIDTH = 80
CAPTURE_HEIGHT = 10
BORDER_WIDTH = 3

# Параметры захвата
TARGET_FPS = 240  # Максимальная скорость (было 120)
LOG_EVERY_N_FRAMES = 300  # Логировать каждые 300 кадров (вместо 30) — в 10 раз реже

# Настройки детекции синего цвета
BLUE_DETECTION = {
    'min_blue': 100,
    'max_red': 100,
    'max_green': 100,
    'blue_dominance': 50
}

# Параметры overlay (окна) - убраны, теперь в detector_config.json
# OVERLAY_RIGHT_PANEL_WIDTH и OVERLAY_COLOR_SQUARE_SIZE теперь в detector_config.json

# Параметры производительности
UI_UPDATE_INTERVAL = 5  # Обновляем UI каждые 5 кадров (вместо 3)
