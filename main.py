import pyautogui
import time
import tkinter as tk
from tkinter import ttk
import threading

def get_screen_resolution():
  """Возвращает разрешение экрана."""
  screen_width, screen_height = pyautogui.size()
  return screen_width, screen_height

def capture_click_position():
  """Создает окно для захвата клика мышью."""
  global x, y, click_captured
  click_captured = False

  def on_click(event):
    """Обработчик события клика в окне захвата."""
    global x, y, click_captured
    x, y = event.x_root, event.y_root
    click_captured = True
    capture_window.destroy()

  capture_window = tk.Tk()
  capture_window.title("Кликните в нужное место")
  capture_window.attributes('-fullscreen', True)
  capture_window.attributes('-alpha', 0.2)
  capture_window.bind("<Button-1>", on_click)

  while not click_captured:
    capture_window.update()

def schedule_click(x, y, scheduled_time):
  """Имитирует клик мышью в заданное время и в заданной точке."""
  while True:
    current_time = time.localtime()
    if current_time.tm_hour == scheduled_time.tm_hour and \
       current_time.tm_min == scheduled_time.tm_min:
      pyautogui.click(x, y)
      print(f"Клик выполнен в {time.strftime('%H:%M:%S')} в точке ({x}, {y})")
      break
    time.sleep(1)

# --- Создание главного окна ---
root = tk.Tk()
root.title("Планировщик кликов")

# --- Список для хранения запланированных кликов ---
scheduled_clicks = []

# --- Функция для запуска захвата координат ---
def start_capture():
  global click_captured
  capture_click_position()
  if click_captured:
    coords_label.config(text=f"Координаты: ({x}, {y})")

# --- Функция для добавления нового запланированного клика ---
def add_click():
  global x, y, scheduled_clicks
  if not click_captured:
    error_label.config(text="Сначала выберите точку клика!")
    return

  try:
    hour = int(hour_spinbox.get())
    minute = int(minute_spinbox.get())
    scheduled_time_tuple = time.localtime()[:3] + (hour, minute, 0) + time.localtime()[6:]
    scheduled_time = time.struct_time(scheduled_time_tuple)
    scheduled_clicks.append((x, y, scheduled_time))
    update_click_list()
    error_label.config(text="")
  except ValueError:
    error_label.config(text="Неверный формат времени!")

# --- Функция для запуска всех запланированных кликов в отдельных потоках ---
def start_schedule():
  for click in scheduled_clicks:
    x, y, scheduled_time = click
    threading.Thread(target=schedule_click, args=(x, y, scheduled_time)).start()
  scheduled_clicks.clear()  # Очищаем список после запуска
  update_click_list()

# --- Функция для обновления списка запланированных кликов ---
def update_click_list():
  click_listbox.delete(0, tk.END)
  for i, click in enumerate(scheduled_clicks):
    x, y, scheduled_time = click
    click_listbox.insert(tk.END, f"Клик {i+1}: {time.strftime('%H:%M', scheduled_time)} в ({x}, {y})")

# --- Элементы интерфейса ---
capture_button = ttk.Button(root, text="1. Выбрать точку клика", command=start_capture)
capture_button.pack(pady=10)

coords_label = ttk.Label(root, text="Координаты: не выбраны")
coords_label.pack()

time_frame = ttk.Frame(root)
time_frame.pack()

hour_label = ttk.Label(time_frame, text="Час:")
hour_label.pack(side="left")
hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, width=3, wrap=True)
hour_spinbox.pack(side="left")

minute_label = ttk.Label(time_frame, text="Минуты:")
minute_label.pack(side="left")
minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, width=3, wrap=True)
minute_spinbox.pack(side="left")

add_button = ttk.Button(root, text="Добавить клик", command=add_click)
add_button.pack(pady=5)

click_listbox = tk.Listbox(root)
click_listbox.pack()

schedule_button = ttk.Button(root, text="2. Запустить все клики", command=start_schedule)
schedule_button.pack(pady=10)

error_label = ttk.Label(root, text="", foreground="red")
error_label.pack()

root.mainloop()