"""
Общий управляющий оверлей для 4 детекторов
"""

import tkinter as tk
from tkinter import ttk
import json
import os


class MultiControlOverlay:
    """Управляющая панель для 4 детекторов"""
    
    def __init__(self, detectors_data):
        self.detectors_data = detectors_data
        self.detector_refs = []  # Ссылки на экземпляры детекторов
        
        # Увеличенные размеры панели
        self.panel_width = 140
        self.panel_height = 520
        
        self.drag_x = 0
        self.drag_y = 0
        
        # Создаём главное окно
        self.root = tk.Tk()
        self.root.title("Multi Detector Control")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Загружаем позицию
        x, y = self._load_position()
        self.root.geometry(f'{self.panel_width}x{self.panel_height}+{x}+{y}')
        self.root.configure(bg='#0a0a0a')
        
        # Создаём canvas с прокруткой
        self.canvas = tk.Canvas(
            self.root,
            width=self.panel_width,
            height=self.panel_height,
            bg='#0a0a0a',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Создаём фрейм внутри canvas
        self.main_frame = tk.Frame(self.canvas, bg='#0a0a0a')
        self.canvas_window = self.canvas.create_window(0, 0, window=self.main_frame, anchor='nw')
        
        self._create_ui()
        
        # Привязка перемещения к canvas
        self.canvas.bind('<Button-1>', self._on_mouse_press)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
    
    def _load_position(self):
        """Загрузить позицию панели управления"""
        try:
            if os.path.exists("multi_control_position.json"):
                with open("multi_control_position.json", "r") as f:
                    pos = json.load(f)
                return pos.get("x", 50), pos.get("y", 50)
        except:
            pass
        return 50, 50
    
    def _save_position(self):
        """Сохранить позицию панели"""
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            with open("multi_control_position.json", "w") as f:
                json.dump({"x": x, "y": y}, f)
        except:
            pass
    
    def _create_ui(self):
        """Создать интерфейс управления"""
        # Заголовок
        title_label = tk.Label(
            self.main_frame,
            text="CONTROL PANEL",
            font=("Arial", 11, "bold"),
            bg='#0a0a0a',
            fg='white'
        )
        title_label.pack(pady=8)
        
        # Кнопка закрыть
        btn_close = tk.Button(
            self.main_frame,
            text="× CLOSE",
            command=self._on_close,
            font=("Arial", 10, "bold"),
            bg="#ff3b3b",
            fg="white",
            activebackground="#ff0000",
            bd=0,
            width=12,
            height=1
        )
        btn_close.pack(pady=5)
        
        # Разделитель
        separator = tk.Frame(self.main_frame, height=2, bg='#333')
        separator.pack(fill=tk.X, padx=10, pady=8)
        
        # Создаём элементы для каждого детектора
        self.detector_widgets = []
        for i, detector in enumerate(self.detectors_data, 1):
            self._create_detector_control(i, detector)
    
    def _create_detector_control(self, num, detector):
        """Создать элементы управления для одного детектора"""
        frame = tk.Frame(self.main_frame, bg='#1a1a1a', relief='solid', bd=1)
        frame.pack(padx=8, pady=6, fill=tk.X)
        
        # Название
        name_label = tk.Label(
            frame,
            text=f"DETECTOR {num}",
            font=("Arial", 9, "bold"),
            bg='#1a1a1a',
            fg='white'
        )
        name_label.pack(pady=(4, 2))
        
        # Квадрат цвета
        color_canvas = tk.Canvas(frame, width=40, height=40, bg='#1a1a1a', highlightthickness=0)
        r, g, b = detector['target_color']
        color = f'#{r:02x}{g:02x}{b:02x}'
        color_square = color_canvas.create_rectangle(8, 8, 32, 32, fill=color, outline='#666', width=2)
        color_canvas.pack(pady=4)
        
        # Контейнер для checkbox и индикатора
        controls_frame = tk.Frame(frame, bg='#1a1a1a')
        controls_frame.pack(pady=2)
        
        # Checkbox активности
        active_var = tk.BooleanVar(value=detector['active'])
        chk = tk.Checkbutton(
            controls_frame,
            text="Active",
            variable=active_var,
            command=lambda idx=num-1, var=active_var: self._toggle_detector(idx, var),
            bg='#1a1a1a',
            fg='#aaa',
            activebackground='#1a1a1a',
            selectcolor='#0a0a0a',
            font=("Arial", 8)
        )
        chk.pack(side=tk.LEFT, padx=4)
        
        # Индикатор нажатия
        indicator_label = tk.Label(
            controls_frame,
            text="",
            font=("Arial", 14, "bold"),
            bg='#1a1a1a',
            fg='lime',
            width=2
        )
        indicator_label.pack(side=tk.LEFT, padx=4)
        
        # Label для клавиши
        key_label = tk.Label(
            frame,
            text="Key:",
            font=("Arial", 8),
            bg='#1a1a1a',
            fg='#aaa'
        )
        key_label.pack()
        
        # Поле клавиши
        key_entry = tk.Entry(
            frame,
            font=("Consolas", 11, "bold"),
            width=5,
            justify='center',
            bg='#0a0a0a',
            fg='#00ff00',
            insertbackground='#00ff00',
            bd=1,
            relief='solid'
        )
        key_entry.insert(0, detector['trigger_key'])
        key_entry.bind('<Return>', lambda e, idx=num-1, entry=key_entry: self._update_key(idx, entry))
        key_entry.pack(pady=(2, 6))
        
        self.detector_widgets.append({
            'frame': frame,
            'active_var': active_var,
            'key_entry': key_entry,
            'indicator': indicator_label,
            'color_canvas': color_canvas,
            'color_square': color_square
        })
    
    def _toggle_detector(self, idx, var):
        """Переключить активность детектора"""
        if idx < len(self.detector_refs):
            self.detector_refs[idx].active = var.get()
    
    def _update_key(self, idx, entry):
        """Обновить клавишу детектора"""
        if idx < len(self.detector_refs):
            new_key = entry.get().strip().lower()
            if new_key:
                self.detector_refs[idx].trigger_key = new_key
    
    def _on_mouse_press(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _on_mouse_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f'+{x}+{y}')
        
        if hasattr(self, '_save_timer'):
            self.root.after_cancel(self._save_timer)
        self._save_timer = self.root.after(500, self._save_position)
    
    def _on_close(self):
        self._save_position()
        self.root.quit()
    
    def set_detector_refs(self, refs):
        """Установить ссылки на детекторы"""
        self.detector_refs = refs
    
    def update_detector_color(self, idx, rgb):
        """Обновить цвет детектора"""
        if idx < len(self.detector_widgets):
            r, g, b = rgb
            color = f'#{r:02x}{g:02x}{b:02x}'
            widget = self.detector_widgets[idx]
            widget['color_canvas'].itemconfig(widget['color_square'], fill=color)
    
    def update_key_indicator(self, idx, is_pressed):
        """Обновить индикатор нажатия клавиши"""
        if idx < len(self.detector_widgets):
            widget = self.detector_widgets[idx]
            widget['indicator'].config(text="✔" if is_pressed else "")
    
    def run(self):
        self.root.mainloop()
    
    def destroy(self):
        self._save_position()
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
