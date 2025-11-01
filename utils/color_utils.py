"""
Утилиты для работы с цветом
"""

def rgb_to_hex(r, g, b):
    """Конвертация RGB в HEX"""
    return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))


def bgr_to_rgb(bgr_array):
    """Конвертация BGR в RGB (OpenCV использует BGR)"""
    return bgr_array[::-1]


def calculate_average_color(frame):
    """
    Вычисление среднего цвета кадра
    
    Args:
        frame: numpy array с изображением (RGB формат для dxcam)
    
    Returns:
        tuple: (r, g, b) значения в диапазоне 0-255
    """
    import numpy as np
    # dxcam возвращает RGB, поэтому берём как есть
    if len(frame.shape) == 3 and frame.shape[2] >= 3:
        avg_color_rgb = np.mean(frame[:, :, :3], axis=(0, 1)).astype(int)
        # Уже в RGB, конвертация не нужна
        r, g, b = int(avg_color_rgb[0]), int(avg_color_rgb[1]), int(avg_color_rgb[2])
        return (r, g, b)
    else:
        avg_color = np.mean(frame, axis=(0, 1)).astype(int)
        return tuple(map(int, avg_color))


def get_colored_text(r, g, b, text="███"):
    """
    Получить текст с цветом фона в формате ANSI
    
    Args:
        r, g, b: RGB значения (0-255)
        text: Текст для отображения
    
    Returns:
        str: Текст с ANSI кодами цвета
    """
    # ANSI escape код для RGB фона: \033[48;2;R;G;Bm
    # Сброс цвета: \033[0m
    return f"\033[48;2;{r};{g};{b}m{text}\033[0m"


def get_colored_rgb_string(r, g, b):
    """
    Получить строку RGB с цветным кубиком для консоли

    Args:
        r, g, b: RGB значения (0-255)

    Returns:
        str: Форматированная строка с цветным кубиком
    """
    color_cube = get_colored_text(r, g, b, text="  ")  # Два пробела для "кубика"
    return f"RGB: ({r:3d}, {g:3d}, {b:3d}) {color_cube}"


def print_color_block(r, g, b, width=8, height=3):
    """
    Рисует цветной прямоугольник в консоли с помощью ANSI escape-кодов.

    Args:
        r, g, b: RGB значения (0-255)
        width: ширина блока (в символах)
        height: высота блока (в строках)
    """
    line = f"\033[48;2;{r};{g};{b}m{'  ' * width}\033[0m"
    for _ in range(height):
        print(line)
