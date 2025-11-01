"""
Запуск 4 экземпляров детекторов с индивидуальными оверлеями
"""

import json
import os
import threading
import keyboard
from ui.overlay import DraggableOverlay


class MultiDetectorCapture:
    """Класс для управления одним детектором"""
    
    def __init__(self, detector_id, config):
        self.detector_id = detector_id
        self.config = config
        self.active = config['active']
        self.trigger_key = config['trigger_key']
        self.min_rgb = tuple(config['min_rgb'])
        self.max_rgb = tuple(config['max_rgb'])
        
        self.overlay = None
        self.running = False
    
    def create_overlay(self, border_width):
        """Создать оверлей для этого детектора"""
        self.overlay = DraggableOverlay(
            width=self.config['width'],
            height=self.config['height'],
            border_width=border_width
        )
        self.overlay.set_capture_ref(self)
        
        # Загружаем позицию для этого детектора
        self._load_overlay_position()
    
    def _load_overlay_position(self):
        """Загрузить позицию оверлея для этого детектора"""
        try:
            filename = f"detector_{self.detector_id}_position.json"
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    pos = json.load(f)
                x = pos.get("x", 100 + (self.detector_id - 1) * 250)
                y = pos.get("y", 100 + (self.detector_id - 1) * 50)
                self.overlay.root.geometry(f'+{x}+{y}')
            else:
                # Расположим детекторы по умолчанию со смещением
                x = 100 + (self.detector_id - 1) * 250
                y = 100 + (self.detector_id - 1) * 50
                self.overlay.root.geometry(f'+{x}+{y}')
        except:
            pass
    
    def save_overlay_position(self):
        """Сохранить позицию оверлея"""
        if self.overlay:
            try:
                x = self.overlay.root.winfo_x()
                y = self.overlay.root.winfo_y()
                filename = f"detector_{self.detector_id}_position.json"
                with open(filename, "w") as f:
                    json.dump({"x": x, "y": y}, f)
            except:
                pass
    
    def get_position(self):
        """Получить позицию области захвата"""
        if self.overlay:
            return self.overlay.get_position()
        return None
    
    def update_color_display(self, rgb):
        """Обновить отображение цвета"""
        if self.overlay:
            self.overlay.update_border_color(None, rgb)
    
    def toggle_active(self):
        """Переключить активность детектора"""
        self.active = not self.active
        if self.overlay and hasattr(self.overlay, 'active_var'):
            self.overlay.active_var.set(self.active)


class MultiDetectorSystem:
    """Система управления 4 детекторами"""
    
    def __init__(self, config_file="multi_detector_config.json"):
        # Загрузка конфигурации
        with open(config_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.detectors = []
        self.running = True
        
        # Создание детекторов
        for detector_config in self.config['detectors']:
            detector = MultiDetectorCapture(
                detector_config['id'],
                detector_config
            )
            self.detectors.append(detector)
        
        # Настройка горячей клавиши F8 для переключения всех детекторов
        keyboard.add_hotkey('f8', self._toggle_all_detectors)
    
    def _toggle_all_detectors(self):
        """Переключить все детекторы по F8"""
        # Переключаем состояние (если хоть один активен - выключаем все, иначе включаем все)
        any_active = any(d.active for d in self.detectors)
        new_state = not any_active
        
        for detector in self.detectors:
            detector.active = new_state
            if detector.overlay and hasattr(detector.overlay, 'active_var'):
                detector.overlay.active_var.set(new_state)
    
    def start(self):
        """Запустить систему"""
        border_width = self.config['global_settings']['border_width']
        
        # Создаём оверлеи для каждого детектора
        for detector in self.detectors:
            detector.create_overlay(border_width)
        
        # Запускаем главный цикл первого оверлея (все остальные будут работать параллельно)
        try:
            if self.detectors:
                self.detectors[0].overlay.run()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.running = False
        
        # Удаляем горячую клавишу
        try:
            keyboard.remove_hotkey('f8')
        except:
            pass
        
        # Сохраняем позиции всех оверлеев
        for detector in self.detectors:
            detector.save_overlay_position()
        
        # Закрываем оверлеи
        for detector in self.detectors:
            if detector.overlay:
                detector.overlay.destroy()


def main():
    """Точка входа"""
    # Проверяем наличие конфигурации
    if not os.path.exists("multi_detector_config.json"):
        print("Создание конфигурации по умолчанию...")
        default_config = {
            "detectors": [
                {
                    "id": i,
                    "name": f"Detector {i}",
                    "width": 200,
                    "height": 200,
                    "trigger_key": str(i),
                    "min_rgb": [200, 0, 0] if i == 1 else [0, 200, 0] if i == 2 else [0, 0, 200] if i == 3 else [200, 200, 0],
                    "max_rgb": [255, 50, 50] if i == 1 else [50, 255, 50] if i == 2 else [50, 50, 255] if i == 3 else [255, 255, 50],
                    "active": True
                } for i in range(1, 5)
            ],
            "global_settings": {
                "border_width": 6,
                "fps_limit": 90
            }
        }
        with open("multi_detector_config.json", "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
    
    # Запуск системы
    system = MultiDetectorSystem()
    system.start()


if __name__ == "__main__":
    main()
