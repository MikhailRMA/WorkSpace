import pandas as pd
import os
import json
import logging
from datetime import datetime
import sys

class DataFilter:
    def __init__(self):
        # Основные пути
        self.PROJECT_ROOT = r"C:\Users\majkl\github_repo\WorkSpace\preprocessing_excel_data"
        self.DATA_DIR = os.path.join(self.PROJECT_ROOT, "data")
        self.RESULTS_DIR = os.path.join(self.PROJECT_ROOT, "results")
        self.SCRIPTS_DIR = os.path.join(self.PROJECT_ROOT, "scripts")
        
        # Устанавливаем корректную кодировку
        self._set_encoding()
        
        # Проверка существования папок
        self._validate_dirs()
        
        # Пути к файлам
        self.CONFIG_FILE = os.path.join(self.RESULTS_DIR, "processing_config.json")
        self.INPUT_FILE = os.path.join(self.DATA_DIR, "Общая_выгрузка_тикеты.xlsx")
        
        # Загрузка конфигурации
        self.CONFIG = self._load_config()
        self.GROUPED_FOLDER = self._get_grouped_folder_path()
        
        # Настройка логирования
        self._setup_logging()
        
        # Загрузка данных
        self.df = self._load_input_data()
        self.grouped_data = self._load_grouped_data()
    
    def _set_encoding(self):
        """Устанавливаем корректную кодировку для работы с русскими путями"""
        if sys.platform == 'win32':
            import locale
            if os.name == 'nt':
                import win32api
                try:
                    win32api.GetShortPathName(self.RESULTS_DIR)
                except:
                    pass
    
    def _get_grouped_folder_path(self):
        """Получаем правильный путь к папке с группированными данными"""
        all_items = os.listdir(self.RESULTS_DIR)
        for item in all_items:
            if "внешние_заявители_группировка".lower() in item.lower():
                return os.path.join(self.RESULTS_DIR, item)
        
        raise FileNotFoundError(
            f"Не найдена папка с группированными данными в {self.RESULTS_DIR}\n"
            f"Доступные элементы: {all_items}"
        )
    
    def _validate_dirs(self):
        """Проверка существования всех необходимых папок"""
        required_dirs = {
            "project": self.PROJECT_ROOT,
            "data": self.DATA_DIR,
            "results": self.RESULTS_DIR,
            "scripts": self.SCRIPTS_DIR
        }
        
        for name, path in required_dirs.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Не найдена папка {name}: {path}")

    def _load_config(self):
        """Загрузка конфигурации из файла"""
        if not os.path.exists(self.CONFIG_FILE):
            available_files = "\n".join(os.listdir(self.RESULTS_DIR))
            raise FileNotFoundError(
                f"Файл конфигурации не найден: {self.CONFIG_FILE}\n"
                f"Файлы в папке results:\n{available_files}"
            )
        
        with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверка обязательных полей
        required_keys = ["output_folder", "processed_at", "source_file"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"В конфиге отсутствует ключ: {key}")
                
        return config

    def _setup_logging(self):
        """Настройка системы логирования"""
        log_file = os.path.join(self.RESULTS_DIR, "filtering.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file, encoding='utf-8')
            ]
        )
        logging.info("="*60)
        logging.info("Инициализация скрипта фильтрации")
        logging.info(f"Корень проекта: {self.PROJECT_ROOT}")
        logging.info(f"Файл конфигурации: {self.CONFIG_FILE}")
        logging.info(f"Группированные данные: {self.GROUPED_FOLDER}")
        logging.info(f"Входной файл: {self.INPUT_FILE}")

    def _load_input_data(self):
        """Загрузка входных данных"""
        if not os.path.exists(self.INPUT_FILE):
            available_files = "\n".join(os.listdir(self.DATA_DIR))
            raise FileNotFoundError(
                f"Файл с тикетами не найден: {self.INPUT_FILE}\n"
                f"Доступные файлы:\n{available_files}"
            )
        
        df = pd.read_excel(self.INPUT_FILE)
        
        # Проверка обязательных колонок
        required_columns = {"ID тикета", "Тип страны", "Дата"}
        missing = required_columns - set(df.columns)
        if missing:
            available_columns = "\n".join(df.columns)
            raise ValueError(f"Не хватает колонок: {missing}\nДоступные колонки:\n{available_columns}")
            
        return df

    def _load_grouped_data(self):
        """Загрузка сгруппированных данных"""
        report_path = os.path.join(self.GROUPED_FOLDER, "report.xlsx")
        if not os.path.exists(report_path):
            available_files = "\n".join(os.listdir(self.GROUPED_FOLDER))
            raise FileNotFoundError(
                f"Отчет не найден: {report_path}\n"
                f"Файлы в папке:\n{available_files}"
            )
            
        return pd.read_excel(report_path)

    def _save_results(self):
        """Сохранение отфильтрованных результатов с разбивкой по датам"""
        # Сохранение общих файлов (без разбивки по датам)
        self._save_filtered(None, "пустые_типы.csv", lambda x: x["Тип страны"].isna())
        self._save_filtered(None, "рф_тикеты.csv", lambda x: x["Тип страны"] == "РФ")
        self._save_filtered(None, "глобал_снг_тикеты.csv", 
                          lambda x: x["Тип страны"].isin(["Глобал", "СНГ"]))
        
        # Сохранение по группам дат
        for _, group in self.grouped_data.iterrows():
            group_folder = os.path.join(self.GROUPED_FOLDER, group['Группа дат'])
            if not os.path.exists(group_folder):
                os.makedirs(group_folder)
            
            # Получаем список дат для текущей группы
            if 'to' in group['Группа дат']:
                start_date, end_date = group['Группа дат'].split('_to_')
                date_filter = (self.df["Дата"] >= pd.to_datetime(start_date)) & \
                             (self.df["Дата"] <= pd.to_datetime(end_date))
            else:
                date_filter = self.df["Дата"] == pd.to_datetime(group['Группа дат'])
            
            # Сохраняем данные с фильтрацией по дате и стране
            self._save_filtered(group_folder, "рф_тикеты.csv", 
                              lambda x: (x["Тип страны"] == "РФ") & date_filter)
            self._save_filtered(group_folder, "глобал_снг_тикеты.csv",
                              lambda x: x["Тип страны"].isin(["Глобал", "СНГ"]) & date_filter)

    def _save_filtered(self, folder, filename, filter_func):
        """Сохранение отфильтрованных данных с удалением дубликатов"""
        path = os.path.join(folder or self.GROUPED_FOLDER, filename)
        
        # Получаем отфильтрованные данные и удаляем дубликаты
        filtered = self.df[filter_func(self.df)]["ID тикета"].dropna().unique()
        
        # Удаляем дубликаты и сохраняем
        unique_data = pd.Series(filtered).drop_duplicates().values
        pd.DataFrame(unique_data).to_csv(path, index=False, header=False, encoding='utf-8')
        
        logging.info(f"Сохранено {len(unique_data)} уникальных тикетов в {path}")

    def run(self):
        """Основной метод обработки"""
        try:
            logging.info("Начало обработки...")
            
            # Обработка и сохранение
            self._save_results()
            
            logging.info("Обработка успешно завершена!")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка обработки: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    print("="*60)
    print("Запуск скрипта фильтрации тикетов")
    print("="*60)
    
    try:
        processor = DataFilter()
        if processor.run():
            print("\nСкрипт успешно завершен!")
            print(f"Результаты сохранены в папки группировки: {processor.GROUPED_FOLDER}")
        else:
            print("\nСкрипт завершился с ошибками")
            print(f"Подробности в лог-файле: {os.path.join(processor.RESULTS_DIR, 'filtering.log')}")
            exit(1)
    except Exception as e:
        print(f"\nКритическая ошибка при запуске: {str(e)}")
        print("Проверьте следующее:")
        print(f"1. Существует ли файл: {os.path.join(processor.DATA_DIR, 'Общая_выгрузка_тикеты.xlsx')}")
        print(f"2. Убедитесь, что первый скрипт создал файл: {processor.CONFIG_FILE}")
        print(f"3. Проверьте, что в папке {processor.RESULTS_DIR} есть папка с группированными данными")
        exit(1)