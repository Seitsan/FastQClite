import tkinter as tk
from tkinter import filedialog, font, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from .stats_window import StatsWindow
from PIL import Image, ImageTk

APP_ICON_FILENAME = "icon.png"

def create_placeholder_image(size=(16, 16), color="#FFFFFF"):
    """Создает небольшое белое изображение-заглушку."""
    img = Image.new('RGB', size, color=color)
    return ImageTk.PhotoImage(img)

def load_app_icon(get_path_func):
    """Загружает иконку приложения или использует заглушку."""
    try:
        icon_path = get_path_func(f"resources/icons/{APP_ICON_FILENAME}")
        img = Image.open(icon_path)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Ошибка загрузки иконки приложения '{APP_ICON_FILENAME}': {e}. Используется заглушка.")
        return create_placeholder_image(size=(32, 32), color="#44944A")

class FileSelection(TkinterDnD.Tk):
    """
    Основное приложение, реализующее окно выбора файла с Drag and Drop.
    """

    def __init__(self, get_path_func):
        super().__init__()

        self.bg_color = "#F5F5F5"
        self.accent_color = "#3E5F8A"
        self.header_size = 18
        self.text_size = 14
        self.main_font = "Montserrat"
        self.get_path = get_path_func

        self.app_icon_photo = load_app_icon(self.get_path)
        self.iconphoto(True, self.app_icon_photo)

        self.title("FastQClite - Выбор файла")
        self.geometry("600x400")
        self.config(bg=self.bg_color)

        # Установка шрифтов
        try:
            self.header_font = font.Font(family=self.main_font, size=self.header_size, weight="bold")
            self.text_font = font.Font(family=self.main_font, size=self.text_size)
        except tk.TclError:
            self.main_font = "Helvetica"
            self.header_font = font.Font(family=self.main_font, size=self.header_size, weight="bold")
            self.text_font = font.Font(family=self.main_font, size=self.text_size)

        self._center_window()
        self._create_widgets()

    def _center_window(self):
        """Центрирует окно приложения на экране."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """Создает и размещает все виджеты в окне."""

        main_frame = tk.Frame(self, bg=self.bg_color)
        main_frame.pack(expand=True, padx=20, pady=50)

        label = tk.Label(main_frame,
                         text="Выберите файл FastQ",
                         font=self.header_font,
                         bg=self.bg_color,
                         fg="#333333")
        label.pack(pady=(0, 30))

        select_button = tk.Button(main_frame,
                                  text="Выбрать файл",
                                  font=self.text_font,
                                  command=self._open_file_dialog,
                                  bg=self.accent_color,
                                  fg="white",
                                  activebackground=self.accent_color,
                                  activeforeground="white",
                                  bd=0,
                                  padx=20,
                                  pady=10)
        select_button.pack(pady=10)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._handle_drop)

        dnd_label = tk.Label(main_frame,
                             text="(Поддерживается .fastq, .fq, .gz)",
                             font=("Montserrat", 10),
                             bg=self.bg_color,
                             fg="#666666")
        dnd_label.pack(pady=(5, 0))

    def _open_file_dialog(self):
        """Открывает стандартное диалоговое окно выбора файла."""
        filepath = filedialog.askopenfilename(
            title="Выберите файл FastQ",
            filetypes=[
                ("FASTQ files", "*.fastq"),
                ("Compressed FASTQ files", "*.fastq.gz"),
                ("Other FASTQ extensions", "*.fq *.fq.gz"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self._process_file_selection(filepath)

    def _handle_drop(self, event):
        """Обрабатывает событие перетаскивания (Drop)."""
        filepath = event.data.strip('{}')

        # Обработка случая, когда путь содержит пробелы, но не заключен в скобки
        if ' ' in filepath and '{' not in filepath:
            filepath = filepath.split(' ')[0]

        if filepath:
            self._process_file_selection(filepath)

    def _process_file_selection(self, filepath):
        """Вызывает класс StatsWindow с выбранным путем к файлу."""
        if filepath:
            # Скрываем главное окно перед открытием StatsWindow
            self.withdraw()

            # Вызываем класс StatsWindow из модуля stats_window
            StatsWindow(self, filepath, self.app_icon_photo)

            print(f"Файл выбран/перетащен: {filepath}")