import pandas as pd
import os
import math
import json
from datetime import datetime
import logging
class DataGrouper:
    def __init__(self):
        # Инициализация путей
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")
        self.RESULTS_DIR = os.path.join(self.BASE_DIR, "results")
        
        # Создаем все необходимые папки
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.RESULTS_DIR, exist_ok=True)
        
        # Конфигурация файлов
        self.INPUT_FILE = os.path.join(self.DATA_DIR, "Выгурзка_25.09.25_без_дубликатов.xlsx")
        self.OUTPUT_FOLDER = os.path.join(self.RESULTS_DIR, "Внешние_заявители_группировка")
        self.CONFIG_FILE = os.path.join(self.RESULTS_DIR, "processing_config.json")
        
        # Настраиваем логирование после создания папки results
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка системы логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(self.RESULTS_DIR, "grouping.log"))
            ]
        )
        logging.info("Logger initialized")
    
    def _validate_input(self):
        """Проверка входных данных"""
        if not os.path.exists(self.INPUT_FILE):
            raise FileNotFoundError(f"Input file not found: {self.INPUT_FILE}")
        
        logging.info("Input validation passed")
    
    def _prepare_folders(self):
        """Создание необходимых папок"""
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)
        logging.info(f"Output folder ready: {self.OUTPUT_FOLDER}")
    
    def _load_data(self):
        """Загрузка данных из Excel"""
        logging.info("Loading input data...")
        df = pd.read_excel(self.INPUT_FILE)
        
        # Проверка необходимых колонок
        required_columns = {"Дата", "ID продавца, на которого подали жалобу", "SKU"}
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
            
        logging.info("Data loaded successfully")
        return df
    
    def _group_dates(self, df):
        """Группировка дат по количеству уникальных ID продавцов"""
        logging.info("Grouping dates by seller IDs...")
        
        grouped = df.groupby("Дата")["ID продавца, на которого подали жалобу"].nunique().reset_index()
        grouped.columns = ["Дата", "Unique_IDs"]
        
        # Разделение дат
        big_dates = grouped[grouped["Unique_IDs"] >= 600]["Дата"].tolist()
        small_dates = grouped[grouped["Unique_IDs"] < 600].copy()
        
        # Группировка малых дат
        merged_groups = []
        current_group = []
        current_count = 0
        
        for _, row in small_dates.iterrows():
            date = row["Дата"]
            unique_ids = row["Unique_IDs"]
            
            if current_count + unique_ids <= 600:
                current_group.append(date)
                current_count += unique_ids
            else:
                if current_group:
                    merged_groups.append((current_group, current_count))
                current_group = [date]
                current_count = unique_ids
        
        if current_group:
            merged_groups.append((current_group, current_count))
            
        logging.info(f"Found {len(big_dates)} big dates and {len(merged_groups)} small date groups")
        return big_dates, merged_groups
    
    def _save_group_results(self, df, big_dates, merged_groups):
        """Сохранение результатов группировки"""
        logging.info("Saving grouped data...")
        report_data = []
        
        # Обработка больших дат
        for date in big_dates:
            group_name = date.strftime("%Y-%m-%d")
            group_folder = os.path.join(self.OUTPUT_FOLDER, group_name)
            os.makedirs(group_folder, exist_ok=True)
            
            mask = df["Дата"] == date
            group_df = df[mask]
            
            # Сохранение данных
            group_df.to_excel(os.path.join(group_folder, f"data_{group_name}.xlsx"), index=False)
            self._save_sku_parts(group_df, group_folder)
            
            report_data.append({
                "Дата": date,
                "Уникальные ID продавцов": len(group_df["ID продавца, на которого подали жалобу"].unique()),
                "Группа дат": group_name,
                "Уникальные ID в группе": len(group_df["ID продавца, на которого подали жалобу"].unique())
            })
        
        # Обработка малых дат
        for i, (group_dates, group_total) in enumerate(merged_groups, 1):
            date_min = min(group_dates).strftime("%Y-%m-%d")
            date_max = max(group_dates).strftime("%Y-%m-%d")
            group_name = f"{date_min}_to_{date_max}"
            group_folder = os.path.join(self.OUTPUT_FOLDER, group_name)
            os.makedirs(group_folder, exist_ok=True)
            
            mask = df["Дата"].isin(group_dates)
            group_df = df[mask]
            
            group_df.to_excel(os.path.join(group_folder, f"data_{group_name}.xlsx"), index=False)
            self._save_sku_parts(group_df, group_folder)
            
            for date in group_dates:
                report_data.append({
                    "Дата": date,
                    "Уникальные ID продавцов": len(df[df["Дата"] == date]["ID продавца, на которого подали жалобу"].unique()),
                    "Группа дат": group_name,
                    "Уникальные ID в группе": group_total
                })
        
        # Сохранение отчета
        report_path = os.path.join(self.OUTPUT_FOLDER, "report.xlsx")
        pd.DataFrame(report_data).to_excel(report_path, index=False)
        logging.info(f"Report saved to: {report_path}")
    
    def _save_sku_parts(self, data, folder_path):
        """Сохранение SKU по частям"""
        unique_sellers = data["ID продавца, на которого подали жалобу"].unique()
        num_parts = math.ceil(len(unique_sellers) / 600)
        
        for i in range(num_parts):
            start_idx = i * 600
            end_idx = start_idx + 600
            sellers_part = unique_sellers[start_idx:end_idx]
            part_data = data[data["ID продавца, на которого подали жалобу"].isin(sellers_part)]
            unique_skus = part_data["SKU"].dropna().unique()
            
            output_path = os.path.join(folder_path, f"sku_part_{i+1}.csv")
            pd.DataFrame(unique_skus, columns=["SKU"]).to_csv(output_path, index=False)
        
        logging.info(f"Saved {num_parts} SKU parts to {folder_path}")
    
    def _save_config(self):
        """Сохранение конфигурации обработки"""
        config = {
            "output_folder": self.OUTPUT_FOLDER,
            "processed_at": datetime.now().isoformat(),
            "source_file": os.path.basename(self.INPUT_FILE)
        }
        
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logging.info(f"Config saved to: {self.CONFIG_FILE}")
    
    def run(self):
        """Основной метод обработки"""
        try:
            logging.info("Starting data processing...")
            self._validate_input()
            self._prepare_folders()
            
            df = self._load_data()
            big_dates, merged_groups = self._group_dates(df)
            
            self._save_group_results(df, big_dates, merged_groups)
            self._save_config()
            
            logging.info("Processing completed successfully!")
            print(f"\nГотово! Результаты сохранены в: {self.OUTPUT_FOLDER}")
            return True
            
        except Exception as e:
            logging.error(f"Processing failed: {str(e)}", exc_info=True)
            print(f"\nОшибка: {str(e)}")
            print(f"Подробности в лог-файле: {os.path.join(self.RESULTS_DIR, 'grouping.log')}")
            return False
if __name__ == "__main__":
    print("Запуск скрипта группировки данных...")
    processor = DataGrouper()
    if processor.run():
        print("Скрипт успешно завершен!")
    else:
        print("Скрипт завершился с ошибками")
        exit(1) 