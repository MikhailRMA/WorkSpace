@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    Data Quality Assistant Project Creator
echo ========================================
echo.

set PROJECT_NAME=data_quality_assistant

echo Creating project structure for: %PROJECT_NAME%
echo.

:: Создание основной папки проекта
if not exist "%PROJECT_NAME%" (
    mkdir "%PROJECT_NAME%"
    echo ✓ Created folder: %PROJECT_NAME%
) else (
    echo ⚠ Folder %PROJECT_NAME% already exists
)

:: Создание подпапок
set FOLDERS=modules utils assets

for %%f in (%FOLDERS%) do (
    if not exist "%PROJECT_NAME%\%%f" (
        mkdir "%PROJECT_NAME%\%%f"
        echo ✓ Created folder: %PROJECT_NAME%\%%f
    )
)

:: Создание основных файлов
set FILES=app.py requirements.txt README.md

for %%i in (%FILES%) do (
    if not exist "%PROJECT_NAME%\%%i" (
        type nul > "%PROJECT_NAME%\%%i"
        echo ✓ Created file: %PROJECT_NAME%\%%i
    )
)

:: Создание файлов в modules
set MODULE_FILES=data_loader.py data_overview.py quality_analysis.py data_cleaning.py reporting.py code_generator.py

for %%m in (%MODULE_FILES%) do (
    if not exist "%PROJECT_NAME%\modules\%%m" (
        type nul > "%PROJECT_NAME%\modules\%%m"
        echo ✓ Created file: %PROJECT_NAME%\modules\%%m
    )
)

:: Создание файлов в utils
set UTILS_FILES=helpers.py presets.py

for %%u in (%UTILS_FILES%) do (
    if not exist "%PROJECT_NAME%\utils\%%u" (
        type nul > "%PROJECT_NAME%\utils\%%u"
        echo ✓ Created file: %PROJECT_NAME%\utils\%%u
    )
)

:: Создание файлов в assets
set ASSETS_FILES=educational_content.py

for %%a in (%ASSETS_FILES%) do (
    if not exist "%PROJECT_NAME%\assets\%%a" (
        type nul > "%PROJECT_NAME%\assets\%%a"
        echo ✓ Created file: %PROJECT_NAME%\assets\%%a
    )
)

:: Заполнение requirements.txt
(
echo streamlit
echo pandas
echo numpy
echo matplotlib
echo seaborn
echo plotly
echo scipy
echo openpyxl
)> "%PROJECT_NAME%\requirements.txt"

echo.
echo ========================================
echo    Project structure created successfully!
echo ========================================
echo.
echo Next steps:
echo 1. cd %PROJECT_NAME%
echo 2. pip install -r requirements.txt
echo 3. streamlit run app.py
echo.

:: Открытие папки проекта в проводнике
explorer "%PROJECT_NAME%"

endlocal
pause