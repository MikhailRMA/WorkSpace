import os
from pathlib import Path

def print_directory_structure(start_path):
    """
    Рекурсивно выводит структуру папок и файлов
    :param start_path: начальный путь к папке
    """
    for root, dirs, files in os.walk(start_path):
        # Получаем относительный путь
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            print(f"{sub_indent}{file}")

def main():
    # Укажите путь к папке, которую нужно просканировать
    folder_path = input("Введите путь к папке: ")
    
    # Проверяем, существует ли папка
    if not os.path.isdir(folder_path):
        print(f"Ошибка: папка '{folder_path}' не существует!")
        return
    
    print(f"\nСтруктура папки '{folder_path}':\n")
    print_directory_structure(folder_path)

if __name__ == "__main__":
    main()