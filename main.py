import sys
import os
from pathlib import Path

def get_resource_path(relative_path):
    """
    Возвращает абсолютный путь к ресурсу, работая как в режиме разработки,
    так и в упакованном PyInstaller исполняемом файле.
    """
    # Определяем базовый путь
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, 'src', relative_path)


def ensure_resource_directories():
    """Проверяет и создает необходимые папки ресурсов."""
    icons_dir = get_resource_path('resources/icons')

    # Создаем папки, если они не существуют
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
        print(f"Создана папка: {icons_dir}")


# Вызываем функцию для создания папок ресурсов
ensure_resource_directories()

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

try:
    from src.ui.file_selection import FileSelection
except ImportError as e:
    print(f"Ошибка: Не удалось импортировать FileSelection из src.ui.file_selection.")
    print(f"Убедитесь, что файл 'file_selection.py' находится в каталоге '{project_root / 'src' / 'ui'}'")
    print(f"Подробности ошибки: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    """
    Основная функция для инициализации и запуска приложения FastQClite.
    """
    print("Запуск приложения FastQClite...")
    try:
        app = FileSelection(get_resource_path)
        app.mainloop()
    except Exception as e:
        print(f"Произошла непредвиденная ошибка во время выполнения приложения: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()