"""
Модуль захвата и анализа экрана
"""

import time
import threading
from collections import deque
import dxcam
from utils.color_utils import calculate_average_color, rgb_to_hex
import keyboard
from utils.global_state import GlobalState
import os
import threading
import config as app_config

# Глобальный счётчик для уникальных device_idx
_device_idx_lock = threading.Lock()
_device_idx_counter = 0

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
        
        # Получаем уникальный device_idx для каждого экземпляра
        global _device_idx_counter
        with _device_idx_lock:
            device_idx = _device_idx_counter % 4  # 0, 1, 2, 3
            _device_idx_counter += 1
        
        print(f"[ScreenCapture] Используется device_idx={device_idx}")
        
        try:
            self.camera = dxcam.create(device_idx=device_idx, output_idx=0)
        except Exception as e:
            print(f"[ERROR] Не удалось создать dxcam device_idx={device_idx}: {e}")
            print("[INFO] Возможно, превышен лимит экземпляров (макс. 4)")
            raise
        
        self.running = False
        self.fps_counter = deque(maxlen=30)
        self.frame_count = 0
        self.start_time = None
        self.capture_thread = None
        
        # Используем глобальное состояние
        self.global_state = GlobalState()
        self.active = self.global_state.get_active()
        self.a_pressed = False
        self.trigger_key = getattr(detector, "trigger_key", "a")
        
        # Регистрируем только ОДИН обработчик F8 (через threading.Lock)
        if not hasattr(keyboard, '_f8_registered'):
            keyboard.add_hotkey('f8', self._on_global_toggle)
            keyboard._f8_registered = True
        
        # Подписываемся на изменения глобального состояния
        self.global_state.add_observer(self._on_state_changed)
        self.global_state.start_monitoring()
        
        # Убираем интервал обновления UI - обновляем каждый кадр для мгновенного отклика
        self.ui_update_counter = 0
        self.ui_update_interval = 1  # Обновляем каждый кадр (не 5!)

        # Кэш для предотвращения избыточных обновлений
        self._last_key_pressed_state = None
        self._last_fps_update = 0
        self.fps_update_interval = 1.0  # FPS обновляем раз в секунду (не важен для реакции)
    
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
    
    def _on_global_toggle(self):
        """Обработчик глобальной клавиши F8"""
        new_state = self.global_state.toggle_active()
        print(f"[GLOBAL] Все экземпляры: {'Включено' if new_state else 'Выключено'}")
    
    def _on_state_changed(self, new_state):
        """Callback при изменении глобального состояния"""
        self.active = new_state
        # Обновляем чекбокс в UI
        if self.overlay and hasattr(self.overlay, 'active_var'):
            self.overlay.root.after(0, lambda: self.overlay.active_var.set(new_state))
        print(f"[ScreenCapture] Состояние обновлено: {'Включено' if new_state else 'Выключено'}")
    
    def toggle_active(self):
        """Переключение активности (из UI чекбокса)"""
        # Обновляем глобальное состояние
        self.global_state.set_active(not self.active)
    
    def stop(self):
        """Остановка захвата"""
        self.running = False
        self.global_state.stop_monitoring()
        self.camera.stop() 
        self._print_statistics()
    
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
        # УБРАЛИ DEBUG лог — он замедляет при перемещении
        self.camera.start(target_fps=self.target_fps, region=region)
    
    def _process_frame(self):
        """Обработка одного кадра (МАКСИМАЛЬНАЯ СКОРОСТЬ)"""
        frame_start = time.time()
        frame = self.camera.get_latest_frame()
        
        if frame is None:
            return
        
        # Получаем размеры кадра
        height, width = frame.shape[:2]
        cy = height // 2
        cx = width // 2
        
        # dxcam возвращает RGB
        pixel = frame[cy, cx]
        center_rgb = (int(pixel[0]), int(pixel[1]), int(pixel[2]))

        # Вычисляем средний цвет (для детектора и UI)
        r_avg, g_avg, b_avg = calculate_average_color(frame)

        # --- ДЕТЕКЦИЯ (КРИТИЧЕСКИЙ ПУТЬ - БЕЗ ЗАДЕРЖЕК) ---
        detected = False
        if hasattr(self.detector, "detect"):
            try:
                detected = self.detector.detect(r_avg, g_avg, b_avg, frame=frame)
            except TypeError:
                detected = self.detector.detect(r_avg, g_avg, b_avg)
        
        # --- УПРАВЛЕНИЕ КЛАВИШЕЙ (МГНОВЕННО!) ---
        if self.active:
            if detected and not self.a_pressed:
                keyboard.press(self.trigger_key)
                self.a_pressed = True
               
                if self._last_key_pressed_state != True:
                    self._last_key_pressed_state = True
                    self.overlay.root.after(0, self.overlay.update_key_pressed_indicator, True)
            elif not detected and self.a_pressed:
                keyboard.release(self.trigger_key)
                self.a_pressed = False
            
                if self._last_key_pressed_state != False:
                    self._last_key_pressed_state = False
                    self.overlay.root.after(0, self.overlay.update_key_pressed_indicator, False)
        else:
            if self.a_pressed:
                keyboard.release(self.trigger_key)
                self.a_pressed = False
                if self._last_key_pressed_state != False:
                    self._last_key_pressed_state = False
                    self.overlay.root.after(0, self.overlay.update_key_pressed_indicator, False)

        # Обновление FPS счётчика
        self._update_fps(frame_start)
        self.frame_count += 1

        # Обновление UI (каждый кадр для квадрата, FPS реже)
        self.overlay.update_border_color('', pixel_rgb=center_rgb)
        
        current_time = time.time()
        if current_time - self._last_fps_update >= self.fps_update_interval:
            self._last_fps_update = current_time
            avg_fps = self._calculate_average_fps()
            self.overlay.root.after(0, self.overlay.update_fps, avg_fps)
    
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
        """Регулярное логирование (ОТКЛЮЧЕНО для производительности)"""
        # Закомментировано — замедляет программу
        pass
    
    def _log_detection(self, r, g, b):
        """Логирование при обнаружении"""
        elapsed = time.time() - self.start_time
        message = self.detector.get_detection_message(r, g, b)
        print(f"[{elapsed:.3f}s] {message}")
    
    def _calculate_average_fps(self):
        """Вычисление среднего FPS"""
        if not self.fps_counter or len(self.fps_counter) == 0:
            return 0
        avg = sum(self.fps_counter) / len(self.fps_counter)
        return avg
    
    def _print_statistics(self):
        """Вывод финальной статистики"""
        total_time = time.time() - self.start_time
        avg_fps = self.frame_count / total_time if total_time > 0 else 0
        
        print("\n=== СТАТИСТИКА ===")
        print(f"Всего кадров: {self.frame_count}")

        print(f"Время работы: {total_time:.2f} секунд")      
        print(f"Средний FPS: {avg_fps:.1f}")
