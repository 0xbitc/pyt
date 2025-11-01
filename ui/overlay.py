"""
Перетаскиваемое окно-оверлей для выбора области захвата
"""

import tkinter as tk
import json
import os


class DraggableOverlay:
    """Перемещаемый overlay с рамкой для захвата области экрана"""
    
    def __init__(self, width, height, border_width=6, outline=False):
        self.width = width
        self.height = height
        self.border_width = border_width
        
        # Загружаем параметры из detector_config.json
        try:
            with open("detector_config.json", "r", encoding="utf-8") as f:
                detector_config = json.load(f)
            self.right_panel_width = 90
            self.color_square_size = 35
        except:
            self.right_panel_width = 90
            self.color_square_size = 35
        
        # Создаём главное окно
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')
        
        # Общие размеры окна
        canvas_height = self.height + 2 * self.border_width
        self.total_height = max(canvas_height, 250)
        self.total_width = self.width + 2 * self.border_width + self.right_panel_width
        
        # Загружаем сохранённую позицию или центрируем
        x, y = self._load_position()
        self.root.geometry(f'{self.total_width}x{self.total_height}+{x}+{y}')
        self.root.configure(bg='black')
        
        self._create_layout()
        
        self.border_id = None
        self.drag_x = 0
        self.drag_y = 0
        self.capture_ref = None
        
        self._draw_border()
    
    def _get_center_position(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.total_width) // 2
        y = (screen_height - self.total_height) // 2
        return x, y
    
    def _load_position(self):
        """Загрузить сохранённую позицию окна"""
        try:
            if os.path.exists("window_position.json"):
                with open("window_position.json", "r") as f:
                    pos = json.load(f)
                return pos.get("x", self._get_center_position()[0]), pos.get("y", self._get_center_position()[1])
        except:
            pass
        return self._get_center_position()
    
    def _save_position(self):
        """Сохранить текущую позицию окна"""
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            with open("window_position.json", "w") as f:
                json.dump({"x": x, "y": y}, f)
        except:
            pass
    
    def _create_layout(self):
        """Создаём layout: левый canvas (рамка), правый canvas (информация)"""
        # Левый canvas для рамки
        canvas_left_width = self.width + 2 * self.border_width
        canvas_left_height = self.height + 2 * self.border_width
        self.canvas_left = tk.Canvas(
            self.root,
            width=canvas_left_width,
            height=canvas_left_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas_left.pack(side=tk.LEFT, anchor='nw')
        
        # Правый canvas для информации
        self.canvas_right = tk.Canvas(
            self.root,
            width=self.right_panel_width,
            height=self.total_height,
            bg='#0a0a0a',
            highlightthickness=0
        )
        self.canvas_right.pack(side=tk.LEFT, anchor='nw', fill=tk.Y)
        
        # Привязка событий ТОЛЬКО к левому canvas (рамке)
        self.canvas_left.bind('<Button-1>', self._on_mouse_press)
        self.canvas_left.bind('<B1-Motion>', self._on_mouse_drag)
        # УБРАЛИ привязку к правому canvas — теперь кнопки работают нормально
        
        self._create_controls()
    
    def _draw_border(self):
        """Рисуем белую рамку"""
        canvas_width = self.width + 2 * self.border_width
        canvas_height = self.height + 2 * self.border_width
        
        self.border_id = self.canvas_left.create_rectangle(
            self.border_width // 2,
            self.border_width // 2,
            canvas_width - self.border_width // 2,
            canvas_height - self.border_width // 2,
            outline='white',
            width=self.border_width
        )
    
    def _create_controls(self):
        """Создаём элементы управления с правильными отступами"""
        center_x = self.right_panel_width // 2
        y = 10
        
        # 1. КНОПКА ЗАКРЫТЬ
        btn_close = tk.Button(
            self.canvas_right,
            text="×",
            command=self._on_close,
            font=("Arial", 14, "bold"),
            bg="#ff3b3b",
            fg="white",
            activebackground="#ff0000",
            bd=0,
            width=4,
            height=1
        )
        btn_close_window = self.canvas_right.create_window(center_x, y, window=btn_close, anchor='n')
        y += 35
        
        # 2. КВАДРАТ ЦВЕТА
        square_half = self.color_square_size // 2
        self.color_square_id = self.canvas_right.create_rectangle(
            center_x - square_half,
            y,
            center_x + square_half,
            y + self.color_square_size,
            fill='#000000',
            outline='#444',
            width=1
        )
        y += self.color_square_size + 15
        
        # 3. CHECKBOX
        self.active_var = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(
            self.canvas_right,
            variable=self.active_var,
            command=self._on_toggle_active,
            bg='#0a0a0a',
            selectcolor='#1a1a1a',
            bd=0
        )
        chk_window = self.canvas_right.create_window(center_x, y, window=chk, anchor='n')
        y += 30
        
        # 4. ИНДИКАТОР НАЖАТИЯ КЛАВИШИ (галочка)
        self.key_pressed_y = y
        self.key_pressed_id = None
        y += 35
        
        # 5. FPS (создаётся динамически в update_fps)
        self.fps_y = y
        self.fps_id = None
        y += 40
        
        # 6. ПОЛЕ ВВОДА КЛАВИШИ
        self.key_entry = tk.Entry(
            self.canvas_right,
            font=("Consolas", 14, "bold"),
            width=3,
            justify='center',
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='#00ff00',
            bd=1,
            relief='solid'
        )
        # Загружаем значение из capture_ref (будет установлено через set_capture_ref)
        # Пока оставляем пустым, заполним позже
        self.key_entry.bind('<Return>', self._on_key_change)
        self.key_entry.bind('<FocusOut>', self._on_key_change)
        entry_window = self.canvas_right.create_window(center_x, y, window=self.key_entry, anchor='n')
    
    def _on_close(self):
        self.root.quit()
    
    def _on_toggle_active(self):
        if self.capture_ref:
            self.capture_ref.active = self.active_var.get()
    
    def _on_key_change(self, event=None):
        if self.capture_ref:
            new_key = self.key_entry.get().strip().lower()
            if new_key:
                self.capture_ref.trigger_key = new_key
    
    def _on_mouse_press(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _on_mouse_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f'+{x}+{y}')
        # Сохраняем позицию при перемещении (с задержкой через after)
        if hasattr(self, '_save_timer'):
            self.root.after_cancel(self._save_timer)
        self._save_timer = self.root.after(500, self._save_position)
    
    def get_position(self):
        win_x = self.root.winfo_x()
        win_y = self.root.winfo_y()
        x1 = win_x + self.border_width
        y1 = win_y + self.border_width
        x2 = x1 + self.width
        y2 = y1 + self.height
        return (x1, y1, x2, y2)
    
    def update_border_color(self, hex_color, pixel_rgb=None):
        if pixel_rgb and hasattr(self, 'color_square_id'):
            r, g, b = pixel_rgb
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas_right.itemconfig(self.color_square_id, fill=color)
    
    def update_fps(self, fps):
        if self.fps_id:
            self.canvas_right.delete(self.fps_id)
        
        self.fps_id = self.canvas_right.create_text(
            self.right_panel_width // 2,
            self.fps_y,
            text=f"{int(fps)}",
            fill='#00ff00',
            font=("Consolas", 20, "bold"),
            anchor='n'
        )
    
    def set_capture_ref(self, capture):
        """Устанавливает ссылку на ScreenCapture и обновляет поле клавиши"""
        self.capture_ref = capture
        # Обновляем поле ввода значением из детектора
        if hasattr(capture, 'trigger_key'):
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, capture.trigger_key)
    
    def run(self):
        self.root.mainloop()
    
    def destroy(self):
        # Сохраняем позицию перед закрытием
        self._save_position()
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def update_key_pressed_indicator(self, is_pressed):
        """Обновить индикатор нажатия клавиши"""
        if self.key_pressed_id:
            self.canvas_right.delete(self.key_pressed_id)
        
        if is_pressed:
            self.key_pressed_id = self.canvas_right.create_text(
                self.right_panel_width // 2,
                self.key_pressed_y,
                text="✔",
                fill='lime',
                font=("Arial", 24, "bold"),
                anchor='n'
            )
        else:
            self.key_pressed_id = None
