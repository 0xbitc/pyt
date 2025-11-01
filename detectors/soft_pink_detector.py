import numpy as np

class SoftPinkDetector:
    def __init__(self, config):
        # config: dict с ключами min_rgb, max_rgb, min_percent
        self.min_rgb = np.array(config.get("min_rgb", [200, 120, 180]))
        self.max_rgb = np.array(config.get("max_rgb", [255, 200, 255]))
        self.min_percent = config.get("min_percent", 0.01)
        self.trigger_key = config.get("trigger_key", "a")
        self._last_detected = False

    def get_name(self):
        return "Мягкий розовый"

    def detect(self, r, g, b, frame=None):
        # frame: numpy array (BGR)
        if frame is None:
            return False
        rgb = frame[..., ::-1]  # BGR -> RGB
        mask = np.all((rgb >= self.min_rgb) & (rgb <= self.max_rgb), axis=-1)
        percent = np.mean(mask)
        detected = percent >= self.min_percent
        self._last_detected = detected
        return detected

    def get_detection_message(self, r, g, b):
        return "Обнаружен мягкий розовый цвет!"

    def last_detected(self):
        return self._last_detected
