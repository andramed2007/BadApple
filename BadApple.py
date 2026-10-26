import cv2
import numpy as np
import os
import time

os.system('')

VIDEO_FILE = "BadAppleS.mp4"

if not os.path.exists(VIDEO_FILE):
    print(f"Ошибка: Видеофайл '{VIDEO_FILE}' не найден рядом со скриптом!")
    exit()

cap = cv2.VideoCapture(VIDEO_FILE)

print(f"Видеофайл обнаружен. Запуск звука и кадров напрямую из {VIDEO_FILE}...")
print("Разверните консоль на весь экран! Запуск через 2 секунды...")
time.sleep(2)

print("\033[2J\033[H", end="")

VIDEO_ASPECT = 4.0 / 3.0
FONT_COMPENSATION = 0.42

FPS = 30
FRAME_TIME = 1.0 / FPS 

def play_audio(file_path):
    abs_path = os.path.abspath(file_path).replace("\\", "\\\\")
    vbs_content = (
        'Set p = CreateObject("WMPlayer.OCX")\n'
        f'p.URL = "{abs_path}"\n'
        'p.controls.play\n'
        'Do While p.playState <> 1\n'
        '  Wscript.Sleep 100\n'
        'Loop\n'
    )
    with open("sound.vbs", "w", encoding="cp1251") as f:
        f.write(vbs_content)
    os.system("start /min wscript.exe sound.vbs")

def stop_audio():
    os.system("taskkill /IM wscript.exe /F >nul 2>&1")
    if os.path.exists("sound.vbs"):
        try:
            os.remove("sound.vbs")
        except:
            pass

while True:
    stop_audio()
    play_audio(VIDEO_FILE)
        
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while cap.isOpened():
        start_time = time.perf_counter()
        
        ret, frame = cap.read()
        if not ret:
            break  
            
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        try:
            terminal_columns, terminal_lines = os.get_terminal_size()
        except OSError:
            terminal_columns, terminal_lines = 80, 24

        target_width = terminal_columns
        target_height = int((target_width / VIDEO_ASPECT) * FONT_COMPENSATION)
        
        target_width = max(1, target_width)
        target_height = max(1, target_height)

        resized_image = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)

        print("\033[H", end="")

        frame_lines = []
        for row in resized_image:
            line_symbols = np.where(row > 127, "-", " ")
            text_line = "".join(line_symbols)
            
            padding = " " * (terminal_columns - len(text_line))
            frame_lines.append(text_line + padding)
            
        print("\n".join(frame_lines), end="")
        
        elapsed_time = time.perf_counter() - start_time
        if elapsed_time < FRAME_TIME:
            time.sleep(FRAME_TIME - elapsed_time)
            
    stop_audio()

cap.release()
