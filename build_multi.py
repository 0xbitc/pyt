"""
Скрипт сборки multi_detector_runner.py в исполняемый файл
"""

import PyInstaller.__main__
import os
import shutil

# Имя выходного файла
OUTPUT_NAME = 'MultiDetector'

# Очистка предыдущих сборок
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# Параметры сборки
PyInstaller.__main__.run([
    'multi_detector_runner.py',
    '--onefile',
    '--windowed',
    '--name=' + OUTPUT_NAME,
    '--icon=NONE',
    '--add-data=ui;ui',
    '--hidden-import=keyboard',
    '--hidden-import=mss',
    '--hidden-import=PIL',
    '--hidden-import=numpy',
    '--hidden-import=win32api',
    '--hidden-import=win32con',
    '--clean',
    '--noconfirm',
])

print("\n" + "="*50)
print(f"Сборка завершена!")
print(f"Исполняемый файл: dist\\{OUTPUT_NAME}.exe")
print("="*50)

# Копируем конфиг в папку dist (если он существует)
if os.path.exists('multi_detector_config.json'):
    shutil.copy('multi_detector_config.json', 'dist/multi_detector_config.json')
    print("Конфигурация скопирована в dist/")
