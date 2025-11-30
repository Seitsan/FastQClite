import tkinter as tk
from tkinter import font, messagebox
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ..models.fastq_plots import run_analysis, create_figure_length, create_figure_quality, create_figure_content


class StatsWindow(tk.Toplevel):
    """
    Окно для отображения статистического анализа FASTQ-файла с графиками Matplotlib.
    """

    def __init__(self, master, filepath: str, app_icon_photo: tk.PhotoImage):
        super().__init__(master)

        self.iconphoto(True, app_icon_photo)

        self.bg_color = "#F5F5F5"
        self.accent_color = "#3E5F8A"
        self.header_size = 18
        self.text_size = 14
        self.main_font = "Montserrat"
        self.filepath = filepath
        self.analysis_data: Any = None

        self.title("FastQClite - Статистика")
        self.geometry("1200x800")
        self.config(bg=self.bg_color)

        # Установка шрифтов
        try:
            self.header_font = font.Font(family=self.main_font, size=self.header_size, weight="bold")
            self.text_font = font.Font(family=self.main_font, size=self.text_size)
        except tk.TclError:
            self.main_font = "Helvetica"
            self.header_font = font.Font(family=self.main_font, size=self.header_size, weight="bold")
            self.text_font = font.Font(family=self.main_font, size=self.text_size)

        # Перехватываем закрытие окна, чтобы восстановить главное окно
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        if not self._load_data():
            return

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._create_left_frame()
        self._create_right_frame()

        self.show_length_distribution()

        self._center_window()

    def _load_data(self) -> bool:
        """Запускает анализ и обрабатывает возможные ошибки."""
        try:
            self.analysis_data = run_analysis(self.filepath)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка анализа",
                                 f"Не удалось проанализировать файл '{Path(self.filepath).name}': {e}")
            self.master.deiconify()
            self.destroy()
            return False

    def _center_window(self):
        """Центрирует окно статистики."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _on_closing(self):
        """Обрабатывает закрытие окна статистики."""
        self.master.deiconify()
        self.destroy()

    def _create_left_frame(self):
        """Создает левый фрейм с навигационными кнопками."""
        self.left_frame = tk.Frame(self,
                                   width=300,
                                   bg="white",
                                   relief=tk.RIDGE,
                                   borderwidth=1)
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.left_frame.grid_propagate(False)

        # Заголовок FastQClite
        title_label = tk.Label(self.left_frame,
                               text="FastQClite",
                               font=("Montserrat", 24, "bold"),
                               bg="white",
                               fg=self.accent_color,
                               pady=20)
        title_label.pack(fill='x')

        # Разделитель
        tk.Frame(self.left_frame, height=2, bg=self.accent_color).pack(fill='x', padx=10, pady=5)

        # Кнопки для графиков
        self.buttons_config = [
            ("Распределение длин последовательностей", self.show_length_distribution),
            ("Среднее качество по каждой позиции в риде", self.show_quality_distribution),
            ("Процентное содержание каждого нуклеотида по позициям", self.show_base_content)
        ]

        self.button_widgets = {}
        for text, command in self.buttons_config:
            btn = tk.Button(self.left_frame,
                            text=text,
                            command=command,
                            font=self.text_font,
                            bg="white",
                            fg="#333333",
                            activebackground=self.accent_color,
                            activeforeground="white",
                            bd=0,
                            anchor="w",
                            padx=15,
                            pady=10)
            btn.pack(fill='x', padx=10, pady=5)
            self.button_widgets[text] = btn

        filename = Path(self.filepath).name
        file_label = tk.Label(self.left_frame,
                              text=f"Файл: {filename}",
                              font=("Montserrat", 10),
                              bg="white",
                              fg="#666666",
                              wraplength=280,
                              justify=tk.LEFT)
        file_label.pack(side=tk.BOTTOM, fill='x', padx=15, pady=10)

    def _create_right_frame(self):
        """Создает правый фрейм для встраивания графиков."""
        self.right_frame = tk.Frame(self, bg=self.bg_color)
        self.right_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.plot_container = tk.Frame(self.right_frame, bg=self.bg_color)
        self.plot_container.grid(row=0, column=0, sticky="nswe")
        self.plot_container.grid_rowconfigure(0, weight=1)
        self.plot_container.grid_columnconfigure(0, weight=1)

        self.canvas_widget = None
        self.toolbar = None

    def _update_plot_frame(self, new_figure: plt.Figure, active_button_text: str):
        """Обновляет правый фрейм новым графиком Matplotlib."""

        if self.canvas_widget:
            self.canvas_widget.destroy()
        if self.toolbar:
            self.toolbar.destroy()

        canvas = FigureCanvasTkAgg(new_figure, master=self.plot_container)
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Добавление панели инструментов Matplotlib (навигация)
        self.toolbar = NavigationToolbar2Tk(canvas, self.plot_container, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.draw()

        self._update_button_state(active_button_text)

    def _update_button_state(self, active_button_text: str):
        """Подсвечивает активную кнопку."""
        for text, btn in self.button_widgets.items():
            if text == active_button_text:
                btn.config(bg=self.accent_color, fg="white", relief=tk.SUNKEN)
            else:
                btn.config(bg="white", fg="#333333", relief=tk.FLAT)

    def show_length_distribution(self):
        """Отображает Распределение длин последовательностей."""
        data = self.analysis_data.get('sequence_lengths', [])
        fig = create_figure_length(data, self.accent_color)
        self._update_plot_frame(fig, "Распределение длин последовательностей")

    def show_quality_distribution(self):
        """Отображает Среднее качество по каждой позиции в риде."""
        data = self.analysis_data.get('mean_qualities_data')
        fig = create_figure_quality(data, self.accent_color)
        self._update_plot_frame(fig, "Среднее качество по каждой позиции в риде")

    def show_base_content(self):
        """Отображает Процентное содержание каждого нуклеотида по позициям."""
        data = self.analysis_data.get('base_content_data')
        fig = create_figure_content(data, self.accent_color)
        self._update_plot_frame(fig, "Процентное содержание каждого нуклеотида по позициям")
