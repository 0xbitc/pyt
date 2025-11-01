"""
Модуль захвата через MSS (без ограничений на количество экземпляров)
"""

import time
import threading
from collections import deque
import numpy as np
from mss import mss
from utils.color_utils import calculate_average_color, rgb_to_hex
import keyboard
from utils.global_state import GlobalState


class ScreenCaptureMSS:
    """Класс для захвата через MSS (неограниченное количество экземпляров)"""
    
    def __init__(self, overlay, detector, target_fps=120, log_interval=30):
        self.overlay = overlay
        self.detector = detector
        self.target_fps = target_fps
        self.log_interval = log_interval
        self.target_frame_time = 1.0 / target_fps
        
        self.sct = mss()
        self.running = False
        self.fps_counter = deque(maxlen=30)
        self.frame_count = 0
        self.start_time = None
        self.capture_thread = None
        
        # Глобальное состояние
        self.global_state = GlobalState()
        self.active = self.global_state.get_active()
        self.a_pressed = False
        self.trigger_key = getattr(detector, "trigger_key", "a")
        
        if not hasattr(keyboard, '_f8_registered'):
            keyboard.add_hotkey('f8', self._on_global_toggle)
            keyboard._f8_registered = True
        
        self.global_state.add_observer(self._on_state_changed)
        self.global_state.start_monitoring()
        
        self.ui_update_counter = 0
        self.ui_update_interval = 3
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.start_time = time.time()
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    
    def _on_global_toggle(self):
        new_state = self.global_state.toggle_active()
        print(f"[GLOBAL] Все экземпляры: {'Включено' if new_state else 'Выключено'}")
    
    def _on_state_changed(self, new_state):
        self.active = new_state
        if self.overlay and hasattr(self.overlay, 'active_var'):
            self.overlay.root.after(0, lambda: self.overlay.active_var.set(new_state))
    
    def toggle_active(self):
        self.global_state.set_active(not self.active)
    
    def stop(self):
        self.running = False
        self.global_state.stop_monitoring()
    
    def _capture_loop(self):
        while self.running:
            loop_start = time.time()
            
            x1, y1, x2, y2 = self.overlay.get_position()
            monitor = {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}
            
            screenshot = self.sct.grab(monitor)
            frame = np.array(screenshot)[:, :, :3]  # BGRA -> BGR
            frame = frame[:, :, ::-1]  # BGR -> RGB
            
            self._process_frame(frame, loop_start)
            
            # Ограничиваем FPS
            elapsed = time.time() - loop_start
            if elapsed < self.target_frame_time:
                time.sleep(self.target_frame_time - elapsed)
    
    def _process_frame(self, frame, frame_start):
        height, width = frame.shape[:2]
        cy, cx = height // 2, width // 2
        center_rgb = tuple(map(int, frame[cy, cx]))
        
        r_avg, g_avg, b_avg = calculate_average_color(frame)
        hex_color_avg = rgb_to_hex(r_avg, g_avg, b_avg)
        
        detected = False
        if hasattr(self.detector, "detect"):
            try:
                detected = self.detector.detect(r_avg, g_avg, b_avg, frame=frame)
            except TypeError:
                detected = self.detector.detect(r_avg, g_avg, b_avg)
        
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
        
        self._update_fps(frame_start)
        self.frame_count += 1
        
        self.ui_update_counter += 1
        if self.ui_update_counter >= self.ui_update_interval:
            self.ui_update_counter = 0
            self.overlay.update_border_color('', pixel_rgb=center_rgb)
            avg_fps = self._calculate_average_fps()
            self.overlay.root.after(0, self.overlay.update_fps, avg_fps)
    
    def _update_fps(self, frame_start):
        frame_time = time.time() - frame_start
        if frame_time > 0:
            self.fps_counter.append(1 / frame_time)
    
    def _calculate_average_fps(self):
        if not self.fps_counter:
            return 0
        return sum(self.fps_counter) / len(self.fps_counter)
