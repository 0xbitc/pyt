"""
Модуль захвата и анализа экрана
"""

import time
import threading
from collections import deque
import dxcam
from utils.color_utils import calculate_average_color, rgb_to_hex
import keyboard


class ScreenCapture:
    """Класс для захвата и анализа экрана"""
    
    def __init__(self, overlay, detector, target_fps=120, log_interval=30):
        """
        Args:
            overlay: Объект DraggableOverlay
            detector: Объект детектора цвета (BaseColorDetector)
            target_fps: Целевой FPS захвата
            log_interval: Интервал логирования (в кадрах)
        """
        self.overlay = overlay
        self.detector = detector
        self.target_fps = target_fps
        self.log_interval = log_interval
        
        self.camera = dxcam.create()
        self.running = False
        self.fps_counter = deque(maxlen=30)
        self.frame_count = 0
        self.start_time = None
        self.capture_thread = None
        
        self.active = True
        self.a_pressed = False
        # Получаем trigger_key из detector, если есть
        self.trigger_key = getattr(detector, "trigger_key", "a")
        keyboard.add_hotkey('f8', self.toggle_active)
    
    def start(self):
        """Запуск захвата в отдельном потоке"""
        if self.running:
            return
        
        self.running = True
        self.start_time = time.time()
        self.capture_thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )
        self.capture_thread.start()
    
    def stop(self):
        """Остановка захвата"""
        self.running = False
        self.camera.stop() 
        self._print_statistics()
    
    def toggle_active(self):
        """Переключение активности захвата"""
        self.active = not self.active
        print(f"[ScreenCapture] {'Включено' if self.active else 'Выключено'}")
    
    def _capture_loop(self):
        """Основной цикл захвата"""
        region = None
        
        while self.running:
            # Получаем текущую позицию области захвата
            current_region = self.overlay.get_position()
            
            # Перезапуск камеры при изменении региона
            if region != current_region:
                self._restart_camera(current_region)
                region = current_region
            
            # Захват и анализ кадра
            self._process_frame()
    
    def _restart_camera(self, region):
        """Перезапуск камеры с новым регионом"""
        self.camera.stop()
        print(f"[DEBUG] Захватываемая область: {region}")
        self.camera.start(target_fps=self.target_fps, region=region)
    
    def _process_frame(self):
        """Обработка одного кадра"""
        frame_start = time.time()
        frame = self.camera.get_latest_frame()
        
        if frame is None:
            return
        
        # Получаем размеры кадра
        height, width = frame.shape[:2]
        cy = height // 2
        cx = width // 2
        
        # dxcam возвращает RGB (НЕ BGR как OpenCV!)
        pixel = frame[cy, cx]
        center_rgb = (int(pixel[0]), int(pixel[1]), int(pixel[2]))  # RGB как есть

        # Вычисляем средний цвет всей области (уже в RGB)
        r_avg, g_avg, b_avg = calculate_average_color(frame)
        hex_color_avg = rgb_to_hex(r_avg, g_avg, b_avg)

        # --- Используем frame для детектора ---
        detected = False
        if hasattr(self.detector, "detect"):
            try:
                detected = self.detector.detect(r_avg, g_avg, b_avg, frame=frame)
            except TypeError:
                detected = self.detector.detect(r_avg, g_avg, b_avg)
        # --- Управление клавишей ---
        if self.active:
            if detected and not self.a_pressed:
                keyboard.press(self.trigger_key)
                self.a_pressed = True
                self.overlay.root.after(0, self.overlay.update_key_pressed_indicator, True)
            elif not detected and self.a_pressed:
                keyboard.release(self.trigger_key)
                self.a_pressed = False
                self.overlay.root.after(0, self.overlay.update_key_pressed_indicator, False)
        else:
            if self.a_pressed:
                keyboard.release(self.trigger_key)
                self.a_pressed = False
                self.overlay.root.after(0, self.overlay.update_key_pressed_indicator, False)

        # Обновление UI
        # Рамка - белая (всегда видна)
        # Квадрат - цвет центрального пикселя
        self.overlay.update_border_color('', pixel_rgb=center_rgb)
        
        # Обновление FPS через безопасный вызов Tkinter
        self._update_fps(frame_start)
        avg_fps = self._calculate_average_fps()
        self.overlay.root.after(0, self.overlay.update_fps, avg_fps)
        
        self.frame_count += 1
        
        # Логирование (логируем средний цвет)
        self._log_frame(r_avg, g_avg, b_avg, hex_color_avg, detected)
    
    def _update_fps(self, frame_start):
        """Обновление счетчика FPS"""
        frame_time = time.time() - frame_start
        if frame_time > 0:
            current_fps = 1 / frame_time
            self.fps_counter.append(current_fps)
    
    def _log_frame(self, r, g, b, hex_color, is_detected):
        """Логирование кадра"""
        # Регулярные логи
        if self.frame_count % self.log_interval == 0:
            self._log_regular(r, g, b, hex_color, is_detected)
        
        # Логи при детекции
        if is_detected:
            self._log_detection(r, g, b)
    
    def _log_regular(self, r, g, b, hex_color, is_detected):
        """Регулярное логирование"""
        avg_fps = self._calculate_average_fps()
        elapsed = time.time() - self.start_time
        
        status = f"✓ {self.detector.get_name()}" if is_detected else ""
        
        # Цветной блок в консоли
        color_block = f"\033[48;2;{r};{g};{b}m   \033[0m"
        
        print(f"[{elapsed:.2f}s] FPS: {avg_fps:.1f} | "
              f"RGB: ({r:3d}, {g:3d}, {b:3d}) {color_block} | "
              f"HEX: {hex_color} | "
              f"Кадров: {self.frame_count} {status}")
    
    def _log_detection(self, r, g, b):
        """Логирование при обнаружении"""
        elapsed = time.time() - self.start_time
        message = self.detector.get_detection_message(r, g, b)
        print(f"[{elapsed:.3f}s] {message}")
    
    def _calculate_average_fps(self):
        """Вычисление среднего FPS"""
        if not self.fps_counter:
            return 0
        return sum(self.fps_counter) / len(self.fps_counter)
    
    def _print_statistics(self):
        """Вывод финальной статистики"""
        total_time = time.time() - self.start_time
        avg_fps = self.frame_count / total_time if total_time > 0 else 0
        
        print("\n=== СТАТИСТИКА ===")
        print(f"Всего кадров: {self.frame_count}")
        print(f"Время работы: {total_time:.2f} секунд")
        print(f"Средний FPS: {avg_fps:.1f}")
