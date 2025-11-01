"""
Перетаскиваемое окно-оверлей для выбора области захвата
"""

import tkinter as tk
import config


class DraggableOverlay:
    """Перемещаемый overlay с рамкой для захвата области экрана"""
    
    def __init__(self, width, height, border_width=6, outline=False):
        """
        Args:
            width: ширина области захвата (без рамки)
            height: высота области захвата (без рамки)
            border_width: толщина рамки
            outline: не используется (для совместимости)
        """
        self.width = width
        self.height = height
        self.border_width = border_width
        
        # Используем параметры из config
        self.color_square_size = config.OVERLAY_COLOR_SQUARE_SIZE
        self.right_panel_width = config.OVERLAY_RIGHT_PANEL_WIDTH
        
        # Создаём главное окно
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Убираем стандартную рамку окна
        self.root.attributes('-topmost', True)  # Поверх всех окон
        self.root.attributes('-transparentcolor', 'black')  # Чёрный цвет = прозрачный
        
        # Общие размеры окна
        # Высота = высота рамки (может быть меньше минимума для правой панели)
        canvas_height = self.height + 2 * self.border_width
        min_right_height = 300  # Минимальная высота для элементов управления
        self.total_height = max(canvas_height, min_right_height)
        self.total_width = self.width + 2 * self.border_width + self.right_panel_width
        
        x, y = self._get_center_position()
        self.root.geometry(f'{self.total_width}x{self.total_height}+{x}+{y}')
        self.root.configure(bg='black')
        
        # Создаём layout: canvas слева для рамки, canvas справа для информации
        self._create_layout()
        
        # ID элементов для обновления
        self.border_id = None
        self.square_id = None
        self.fps_text_id = None
        
        # Для перемещения окна
        self.drag_x = 0
        self.drag_y = 0
        
        # Ссылка на ScreenCapture (устанавливается позже)
        self.capture_ref = None
        
        # Рисуем рамку СРАЗУ после создания layout
        self._draw_border()
        
        # Привязка событий для перемещения (только на левом canvas)
        self.canvas_left.bind('<Button-1>', self._on_mouse_press)
        self.canvas_left.bind('<B1-Motion>', self._on_mouse_drag)
        
        # Рисуем начальную рамку
        self.update_border_color('#ffffff')
    
    def _get_center_position(self):
        """Вычисляет координаты центра экрана"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.total_width) // 2
        y = (screen_height - self.total_height) // 2
        return x, y
    
    def _create_layout(self):
        """Создаём layout: левый canvas (рамка), правый canvas (информация)"""
        # Левый canvas для рамки (ПРОЗРАЧНЫЙ ФОН)
        canvas_left_width = self.width + 2 * self.border_width
        canvas_left_height = self.height + 2 * self.border_width
        self.canvas_left = tk.Canvas(
            self.root,
            width=canvas_left_width,
            height=canvas_left_height,
            bg='black',  # Чёрный = прозрачный (благодаря transparentcolor)
            highlightthickness=0
        )
        self.canvas_left.pack(side=tk.LEFT, anchor='nw')
        
        # Правый canvas для информации (НЕ прозрачный)
        self.canvas_right = tk.Canvas(
            self.root,
            width=self.right_panel_width,
            height=self.total_height,
            bg='#1a1a1a',  # Тёмно-серый (НЕ чёрный, чтобы не стал прозрачным)
            highlightthickness=0
        )
        self.canvas_right.pack(side=tk.LEFT, anchor='nw', fill=tk.Y)
        
        # Привязка событий для перемещения к ОБОИМ canvas
        self.canvas_left.bind('<Button-1>', self._on_mouse_press)
        self.canvas_left.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas_right.bind('<Button-1>', self._on_mouse_press)
        self.canvas_right.bind('<B1-Motion>', self._on_mouse_drag)
        
        # Создаём элементы управления на правом canvas
        self._create_controls()
    
    def _draw_border(self):
        """Рисуем белую рамку на левом canvas"""
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
        """Создаём элементы управления на правом canvas"""
        y_pos = 15
        
        # Кнопка закрыть
        btn_close = tk.Button(
            self.canvas_right,
            text="✕ Закрыть",
            command=self._on_close,
            font=("Arial", 10, "bold"),
            bg="#d00",
            fg="white",
            width=14
        )
        self.canvas_right.create_window(self.right_panel_width // 2, y_pos, window=btn_close)
        y_pos += 40
        
        # Квадрат с цветом
        self.color_square_id = self.canvas_right.create_rectangle(
            (self.right_panel_width - self.color_square_size) // 2,
            y_pos,
            (self.right_panel_width + self.color_square_size) // 2,
            y_pos + self.color_square_size,
            fill='red',
            outline='white',
            width=2
        )
        y_pos += self.color_square_size + 20
        
        # Текст FPS
        self.fps_text_id = self.canvas_right.create_text(
            self.right_panel_width // 2,
            y_pos,
            text="FPS: 0",
            fill='yellow',
            font=("Arial", 16, "bold"),
            anchor='n'
        )
        y_pos += 40
        
        # Индикатор нажатия клавиши (галочка)
        self.key_pressed_id = self.canvas_right.create_text(
            self.right_panel_width // 2,
            y_pos,
            text="",
            fill='lime',
            font=("Arial", 24, "bold"),
            anchor='n'
        )
        y_pos += 40
        
        # Чекбокс "Активен"
        self.active_var = tk.BooleanVar(value=True)
        chk_active = tk.Checkbutton(
            self.canvas_right,
            text="Активен",
            variable=self.active_var,
            command=self._on_toggle_active,
            font=("Arial", 11, "bold"),
            bg='#1a1a1a',
            fg='white',
            selectcolor='#333',
            activebackground='#1a1a1a',
            activeforeground='white'
        )
        self.canvas_right.create_window(self.right_panel_width // 2, y_pos, window=chk_active)
        y_pos += 40
        
        # Метка "Клавиша:"
        lbl_key = tk.Label(
            self.canvas_right,
            text="Клавиша:",
            font=("Arial", 10, "bold"),
            bg='#1a1a1a',
            fg='white'
        )
        self.canvas_right.create_window(self.right_panel_width // 2, y_pos, window=lbl_key)
        y_pos += 25
        
        # Поле ввода для клавиши (автоматическое применение)
        self.key_entry = tk.Entry(
            self.canvas_right,
            font=("Arial", 12, "bold"),
            width=8,
            justify='center',
            bg='#333',
            fg='white',
            insertbackground='white'
        )
        self.key_entry.insert(0, 'a')  # По умолчанию 'a'
        self.key_entry.bind('<Return>', self._on_key_change)
        self.key_entry.bind('<FocusOut>', self._on_key_change)
        self.canvas_right.create_window(self.right_panel_width // 2, y_pos, window=self.key_entry)
        y_pos += 40
        
        # Кнопка "Нажать клавишу"
        btn_press = tk.Button(
            self.canvas_right,
            text="Нажать",
            command=self._on_manual_press,
            font=("Arial", 11, "bold"),
            bg="#444",
            fg="white",
            width=14
        )
        self.canvas_right.create_window(self.right_panel_width // 2, y_pos, window=btn_press)
    
    def _on_close(self):
        """Закрыть приложение"""
        self.root.quit()
    
    def _on_toggle_active(self):
        """Переключение активности через чекбокс"""
        if self.capture_ref:
            self.capture_ref.active = self.active_var.get()
            status = "включено" if self.capture_ref.active else "выключено"
            print(f"[GUI] Детектор {status}")
    
    def _on_manual_press(self):
        """Ручное нажатие клавиши"""
        if self.capture_ref:
            import keyboard
            key = self.capture_ref.trigger_key
            keyboard.press(key)
            print(f"[GUI] Нажата клавиша: {key}")
            self.root.after(100, lambda: keyboard.release(key))
    
    def _on_mouse_press(self, event):
        """Обработчик нажатия мыши для перемещения"""
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _on_mouse_drag(self, event):
        """Обработчик перемещения мыши"""
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f'+{x}+{y}')
    
    def get_position(self):
        """Возвращает координаты области захвата (внутри рамки)"""
        # Координаты окна
        win_x = self.root.winfo_x()
        win_y = self.root.winfo_y()
        
        # Координаты области захвата (внутри рамки на canvas_left)
        x1 = win_x + self.border_width
        y1 = win_y + self.border_width
        x2 = x1 + self.width
        y2 = y1 + self.height
        
        return (x1, y1, x2, y2)
    
    def update_border_color(self, hex_color, pixel_rgb=None):
        """
        Обновить цвет рамки
        
        Args:
            hex_color: цвет рамки в HEX формате (#RRGGBB)
            pixel_rgb: (r, g, b) - цвет для квадрата (опционально)
        """
        # Рамка уже нарисована в __init__, просто обновляем цвет квадрата
        if pixel_rgb:
            self.update_color_square(pixel_rgb)
    
    def update_color_square(self, rgb):
        """Обновить цвет квадрата"""
        r, g, b = rgb
        color = f'#{r:02x}{g:02x}{b:02x}'
        
        # Обновляем цвет квадрата в правой панели
        self.canvas_right.itemconfig(self.color_square_id, fill=color)
    
    def update_fps(self, fps):
        """Обновить отображение FPS"""
        # ОТЛАДКА
        print(f"[DEBUG UI] Обновление FPS на UI: {fps:.1f}")
        self.canvas_right.itemconfig(self.fps_text_id, text=f"FPS: {int(fps)}")
    
    def set_capture_ref(self, capture):
        """
        Устанавливает ссылку на ScreenCapture для управления
        
        Args:
            capture: объект ScreenCapture
        """
        self.capture_ref = capture
    
    def run(self):
        """Запустить главный цикл окна"""
        self.root.mainloop()
    
    def destroy(self):
        """Закрыть окно"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def _on_key_change(self, event=None):
        """Изменить клавишу для нажатия (автоматически при Enter или потере фокуса)"""
        if self.capture_ref:
            new_key = self.key_entry.get().strip().lower()
            if new_key:
                self.capture_ref.trigger_key = new_key
                print(f"[GUI] Клавиша изменена на: {new_key}")
            else:
                print("[GUI] Ошибка: введите клавишу")
    
    def update_key_pressed_indicator(self, is_pressed):
        """Обновить индикатор нажатия клавиши"""
        if is_pressed:
            self.canvas_right.itemconfig(self.key_pressed_id, text="✔")
        else:
            self.canvas_right.itemconfig(self.key_pressed_id, text="")
