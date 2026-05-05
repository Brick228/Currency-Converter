import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import datetime

# --- Настройки ---
HISTORY_FILE = "history.json"
API_URL = "https://api.exchangerate.host/latest?base={from_currency}&symbols={to_currency}"

# --- Функции логики ---

def get_rates(from_currency, to_currency):
    """Получает курс конвертации из API."""
    try:
        url = API_URL.format(from_currency=from_currency, to_currency=to_currency)
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Проверка на ошибки HTTP
        data = response.json()
        return data['rates'][to_currency]
    except (requests.RequestException, KeyError) as e:
        messagebox.showerror("Ошибка сети", "Не удалось получить данные о курсе валют.\nПроверьте подключение к интернету.")
        return None

def save_history(entry):
    """Сохраняет запись о конвертации в файл JSON."""
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(entry)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def load_history():
    """Загружает историю из файла JSON."""
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- Функции интерфейса ---

def on_convert():
    """Обработчик нажатия кнопки 'Конвертировать'."""
    from_currency = combo_from.get()
    to_currency = combo_to.get()
    amount_str = entry_amount.get()

    # Валидация ввода
    if not amount_str.replace('.', '', 1).isdigit():
        messagebox.showerror("Ошибка ввода", "Пожалуйста, введите корректное число.")
        return

    amount = float(amount_str)
    if amount <= 0:
        messagebox.showerror("Ошибка ввода", "Сумма должна быть больше нуля.")
        return

    # Получение курса и расчет
    rate = get_rates(from_currency, to_currency)
    if rate is None:
        return # Ошибка уже показана в функции get_rates

    result = round(amount * rate, 2)
    
    # Отображение результата
    label_result.config(text=f"Результат: {result} {to_currency}")

    # Сохранение в историю и обновление таблицы
    entry = {
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "result": result,
        "rate": rate,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_history(entry)
    update_history_table()

def update_history_table():
    """Обновляет виджет таблицы с историей."""
    for i in tree.get_children():
        tree.delete(i)
        
    history = load_history()
    for item in history:
        tree.insert("", "end", values=(
            item["from"],
            item["to"],
            item["amount"],
            item["result"],
            item["rate"],
            item["date"]
        ))

# --- Создание главного окна ---
root = tk.Tk()
root.title("Currency Converter")
root.geometry("800x500")
root.resizable(False, False)

# Основной фрейм для виджетов
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

# --- Блок конвертации (верхняя часть) ---
conversion_frame = ttk.LabelFrame(main_frame, text="Конвертация", padding="10")
conversion_frame.pack(fill="x", pady=5)

# Валюта "Из"
ttk.Label(conversion_frame, text="Из:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
combo_from = ttk.Combobox(conversion_frame, values=["USD", "EUR", "RUB", "GBP"], state="readonly")
combo_from.current(0)
combo_from.grid(row=0, column=1, sticky="w", padx=5, pady=5)

# Валюта "В"
ttk.Label(conversion_frame, text="В:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
combo_to = ttk.Combobox(conversion_frame, values=["USD", "EUR", "RUB", "GBP"], state="readonly")
combo_to.current(1)
combo_to.grid(row=1, column=1, sticky="w", padx=5, pady=5)

# Сумма
ttk.Label(conversion_frame, text="Сумма:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_amount = ttk.Entry(conversion_frame)
entry_amount.grid(row=2, column=1, sticky="w", padx=5, pady=5)
entry_amount.focus() # Фокус на поле ввода при запуске

# Кнопка
ttk.Button(conversion_frame, text="Конвертировать", command=on_convert).grid(row=3, column=0, columnspan=2, pady=15)

# Результат
label_result = ttk.Label(conversion_frame, text="Результат: ")
label_result.grid(row=4, column=0, columnspan=2)


# --- Блок истории (нижняя часть) ---
history_frame = ttk.LabelFrame(main_frame, text="История операций", padding="10")
history_frame.pack(fill="both", expand=True)

# Таблица (Treeview)
tree_columns = ("Из", "В", "Сумма", "Результат", "Курс", "Дата")
tree = ttk.Treeview(history_frame, columns=tree_columns, show="headings")

# Настройка ширины колонок и заголовков
for col in tree_columns:
    tree.heading(col, text=col)
    tree.column(col, width=90 if col in ("Из", "В") else 100 if col == "Дата" else 80)

tree.pack(fill="both", expand=True)

# Полоса прокрутки для таблицы
scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")


# --- Запуск приложения ---
if __name__ == "__main__":
    update_history_table() # Загрузить историю при старте окна
    root.mainloop()
