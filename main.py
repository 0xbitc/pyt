"""
Главный файл приложения для захвата и анализа цвета на экране
"""

import config
from ui.overlay import DraggableOverlay
from capture.screen_capture import ScreenCapture
from detectors.blue_detector import BlueDetector
import json
from detectors.soft_pink_detector import SoftPinkDetector


def print_startup_info(detector):
    """Вывод информации при запуске"""
    print("=" * 60)
    print("Запуск программы детекции цвета на экране")
    print("=" * 60)
    print(f"\nАктивный детектор: {detector.get_name()}")
    print(f"Размер области: {config.CAPTURE_WIDTH}x{config.CAPTURE_HEIGHT}")
    print(f"Целевой FPS: {config.TARGET_FPS}")
    print("\nИнструкции:")
    print("- Перетащите рамку на нужную область экрана")
    print("- Цвет рамки меняется в зависимости от содержимого")
    print("- Справа отображается цветной квадрат и FPS")
    print("- При обнаружении целевого цвета появится сообщение")
    print("- Закройте окно для остановки программы")
    print("=" * 60)
    print()


def create_detector():
    """
    Создание детектора цвета
    
    Здесь можно легко заменить детектор на другой
    """
    # Загрузка настроек из detector_config.json
    with open("detector_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return SoftPinkDetector(config)
    
    # Примеры других детекторов (раскомментируйте нужный):
    # from detectors.red_detector import RedDetector
    # return RedDetector(config.RED_DETECTION)
    
    # from detectors.green_detector import GreenDetector
    # return GreenDetector(config.GREEN_DETECTION)


def main():
    """Главная функция приложения"""
    # Создание детектора
    detector = create_detector()
    
    # Вывод информации
    print_startup_info(detector)
    
    # Загрузка параметров окна из detector_config.json
    with open("detector_config.json", "r", encoding="utf-8") as f:
        detector_config = json.load(f)
    
    # Создание GUI с параметрами из конфига детектора
    overlay = DraggableOverlay(
        width=detector_config.get("capture_width", config.CAPTURE_WIDTH),
        height=detector_config.get("capture_height", config.CAPTURE_HEIGHT),
        border_width=detector_config.get("border_width", config.BORDER_WIDTH)
    )

    # Создание захватчика
    capture = ScreenCapture(
        overlay=overlay,
        detector=detector,
        target_fps=config.TARGET_FPS,
        log_interval=config.LOG_EVERY_N_FRAMES
    )

    # Передаем ссылку на захватчик в overlay для управления кнопкой
    overlay.set_capture_ref(capture)
    
    # Запуск захвата
    capture.start()
    
    # Запуск GUI (блокирующий вызов)
    try:
        overlay.run()
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    finally:
        capture.stop()
        overlay.destroy()
        print("Завершено")


if __name__ == "__main__":
    main()
