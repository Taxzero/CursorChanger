# === mabinogiCursor.py (윈도우 11 포커스 문제 수정) ===

import os
import sys
import time
import threading
import ctypes
import psutil
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import win32gui
import win32con
from pystray import Icon, Menu, MenuItem
from PIL import Image
import keyboard

# === 경로 설정 ===
def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

BASE_PATH      = get_base_path()
CURSOR_FOLDER  = "custom_cursors"
CURSOR_DIR     = os.path.join(BASE_PATH, CURSOR_FOLDER)

# ★ 설정 파일을 사용자 AppData 아래에 저장
APPDATA_DIR    = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
SETTINGS_DIR   = os.path.join(APPDATA_DIR, "MabinogiCursor")
os.makedirs(SETTINGS_DIR, exist_ok=True)
SETTINGS_PATH  = os.path.join(SETTINGS_DIR, "settings.json")

ICON_PATH      = os.path.join(CURSOR_DIR, "icon.ico")
TARGET_PROCESS = "mabinogimobile.exe"

cursor_enabled = True
cursor_changed = False

# === TK 팝업을 항상 위로 띄우는 헬퍼 ===
def show_info(title, message):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()
    messagebox.showinfo(title, message, parent=root)
    root.destroy()

def show_error(title, message):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()
    messagebox.showerror(title, message, parent=root)
    root.destroy()

# === 설정 저장/불러오기 ===
def save_cursor_selection(filename):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump({"cursor": filename}, f)
        show_info("설정 저장됨", f"{filename}이(가) 기본 커서로 설정되었습니다.")
    except Exception as e:
        show_error("저장 실패", f"settings.json 저장 중 오류 발생:\n{e}")

def load_cursor_selection():
    if not os.path.exists(SETTINGS_PATH):
        return None
    try:
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f).get("cursor")
    except Exception as e:
        print(f"[오류] settings 로드 실패: {e}")
        return None

# === 첫 실행: 폴더/설정 초기화 ===
os.makedirs(CURSOR_DIR, exist_ok=True)
if not os.path.exists(SETTINGS_PATH):
    default_cursor = next((f for f in os.listdir(CURSOR_DIR)
                           if f.lower().endswith((".ani", ".cur"))), None)
    if default_cursor:
        save_cursor_selection(default_cursor)

# === 현재 커서 경로 불러오기 ===
def get_cursor_path():
    saved = load_cursor_selection()
    if saved:
        path = os.path.join(CURSOR_DIR, saved)
        if os.path.exists(path):
            return path
    for f in os.listdir(CURSOR_DIR):
        if f.lower().endswith((".ani", ".cur")):
            return os.path.join(CURSOR_DIR, f)
    return None

# === 커서 적용/복원 ===
def set_custom_cursor(path):
    if not path or not os.path.exists(path):
        return
    h = win32gui.LoadImage(None, path, win32con.IMAGE_CURSOR, 0, 0,
                            win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
    if h:
        ctypes.windll.user32.SetSystemCursor(h, win32con.OCR_NORMAL)

def restore_default_cursor():
    ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, 0, 0)

def is_game_running():
    return TARGET_PROCESS in [p.name().lower() for p in psutil.process_iter()]

# === 트레이 메뉴 핸들러 ===
def change_cursor_file(icon, item=None):
    dlg = tk.Tk()
    dlg.withdraw()
    dlg.attributes('-topmost', True)
    dlg.update()
    file_path = filedialog.askopenfilename(
        parent=dlg,
        title="새 커서(.ani/.cur) 선택",
        filetypes=[("Cursor Files", "*.ani *.cur")]
    )
    dlg.destroy()
    if not file_path:
        return

    filename = os.path.basename(file_path)
    os.makedirs(CURSOR_DIR, exist_ok=True)
    dest = os.path.join(CURSOR_DIR, filename)
    try:
        if os.path.abspath(file_path) != os.path.abspath(dest):
            shutil.copy(file_path, dest)
    except shutil.SameFileError:
        pass

    save_cursor_selection(filename)
    # 게임이 실행 중일 때만 즉시 적용
    if is_game_running():
        set_custom_cursor(get_cursor_path())

def delete_cursor_folder(icon, item=None):
    # similar topmost handling for messagebox
    try:
        if os.path.exists(CURSOR_DIR):
            shutil.rmtree(CURSOR_DIR)
            show_info("삭제됨", "🗑 커서 폴더가 삭제되었습니다.")
        else:
            show_info("정보", "📂 커서 폴더가 없습니다.")
    except Exception as e:
        show_error("오류", f"❌ 삭제 실패: {e}")

def toggle_cursor(icon=None, item=None):
    global cursor_enabled, cursor_changed
    cursor_enabled = not cursor_enabled
    if not cursor_enabled:
        restore_default_cursor()
    elif is_game_running():
        set_custom_cursor(get_cursor_path())
    cursor_changed = False

# === 게임 감시 쓰레드 ===
def watch_game():
    global cursor_changed
    while True:
        running = is_game_running()
        if running and cursor_enabled and not cursor_changed:
            set_custom_cursor(get_cursor_path())
            cursor_changed = True
        elif (not running or not cursor_enabled) and cursor_changed:
            restore_default_cursor()
            cursor_changed = False
        time.sleep(2)

def on_quit(icon, item):
    restore_default_cursor()
    icon.stop()

# === 트레이 아이콘 초기화 ===
def setup_tray_icon():
    image = Image.open(ICON_PATH)
    menu = Menu(
        MenuItem('커서 ON/OFF 토글', toggle_cursor),
        MenuItem('새 커서 파일 선택', change_cursor_file),
        MenuItem('커서 폴더 삭제', delete_cursor_folder),
        MenuItem('종료', on_quit)
    )
    icon = Icon("MabinogiCursor", image, "커서 감지기", menu)
    # 시작 시 게임 실행 중일 때만 적용
    if is_game_running():
        set_custom_cursor(get_cursor_path())
    threading.Thread(target=watch_game, daemon=True).start()
    keyboard.add_hotkey("ctrl+f12", toggle_cursor)
    icon.run()

if __name__ == "__main__":
    setup_tray_icon()
