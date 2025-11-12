@echo off
chcp 65001 >nul
title Airflow and PostgreSQL Manager
echo ===============================
echo    Multi-Service Manager
echo ===============================
echo.

:: Проверяем наличие Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Docker не установлен или не запущен!
    echo Убедитесь, что Docker Desktop запущен.
    pause
    exit /b 1
)

:menu
cls
echo ===============================
echo    Выберите действие:
echo ===============================
echo 1 - Запустить все сервисы
echo 2 - Запустить только Airflow
echo 3 - Запустить только PostgreSQL + pgAdmin
echo 4 - Остановить все сервисы
echo 5 - Перезапустить Airflow
echo 6 - Полная переустановка Airflow
echo 7 - Показать логи Airflow
echo 8 - Показать статус
echo 9 - Выход
echo.

set /p choice="Введите номер [1-9]: "

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_airflow
if "%choice%"=="3" goto start_postgres
if "%choice%"=="4" goto stop_all
if "%choice%"=="5" goto restart_airflow
if "%choice%"=="6" goto reinstall_airflow
if "%choice%"=="7" goto show_logs
if "%choice%"=="8" goto status
if "%choice%"=="9" goto exit
echo Неверный выбор! Нажмите любую клавишу...
pause
goto menu

:start_all
echo Запуск всех сервисов...
echo Запускаю PostgreSQL и pgAdmin...
docker-compose -f docker-compose-postgres.yml up -d
timeout /t 5
echo Запускаю Airflow...
docker-compose -f docker-compose-airflow.yml up -d
echo.
echo ===============================
echo Все сервисы запущены!
echo Ждите 2-3 минуты пока Airflow инициализируется...
echo.
echo Airflow: http://localhost:8080
echo Логин: airflow / Пароль: airflow
echo.
echo pgAdmin: http://localhost:5050
echo Логин: admin@admin.com / Пароль: admin
echo ===============================
pause
goto menu

:start_airflow
echo Запуск Airflow...
docker-compose -f docker-compose-airflow.yml up -d
echo Airflow запущен: http://localhost:8080
echo Логин: airflow / Пароль: airflow
echo Ждите 2-3 минуты для инициализации...
pause
goto menu

:start_postgres
echo Запуск PostgreSQL и pgAdmin...
docker-compose -f docker-compose-postgres.yml up -d
echo.
echo PostgreSQL запущен: localhost:5432
echo pgAdmin: http://localhost:5050
echo Данные для входа: admin@admin.com / admin
pause
goto menu

:stop_all
echo Остановка всех сервисов...
docker-compose -f docker-compose-airflow.yml down
docker-compose -f docker-compose-postgres.yml down
echo Все сервисы остановлены!
pause
goto menu

:restart_airflow
echo Перезапуск Airflow...
docker-compose -f docker-compose-airflow.yml down
timeout /t 5
docker-compose -f docker-compose-airflow.yml up -d
echo Airflow перезапущен. Ждите 2-3 минуты...
pause
goto menu

:reinstall_airflow
echo Полная переустановка Airflow...
docker-compose -f docker-compose-airflow.yml down --volumes --remove-orphans
echo Удаляем volumes...
docker volume prune -f
echo Инициализируем Airflow...
docker-compose -f docker-compose-airflow.yml up airflow-init
echo Запускаем сервисы...
docker-compose -f docker-compose-airflow.yml up -d
echo Airflow переустановлен! Ждите 3-5 минут...
pause
goto menu

:show_logs
echo Логи Airflow (Ctrl+C для выхода):
docker-compose -f docker-compose-airflow.yml logs -f
pause
goto menu

:status
echo Статус сервисов:
echo.
echo === Airflow ===
docker-compose -f docker-compose-airflow.yml ps
echo.
echo === PostgreSQL ===
docker-compose -f docker-compose-postgres.yml ps
echo.
pause
goto menu

:exit
echo Выход...
pause