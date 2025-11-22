@echo off
chcp 65001 >nul

echo Creating project structure...

:: Создание корневой папки проекта
mkdir "Extractor-SKU-Data-Analysis"
cd "Extractor-SKU-Data-Analysis"

:: Создание подпапок
mkdir data
mkdir notebooks
mkdir sql
mkdir dashboard
mkdir presentation

:: Создание файлов
type nul > README.md
type nul > notebooks\data_analysis.ipynb
type nul > sql\queries.sql
type nul > dashboard\screenshot.png
type nul > dashboard\link_to_dashboard.txt
type nul > presentation\Extractor_SKU_Analysis.pdf

echo Structure created successfully!
echo.
echo Project tree:
tree /F

pause