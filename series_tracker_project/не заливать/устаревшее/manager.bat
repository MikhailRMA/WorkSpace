@echo off
chcp 65001
cls

echo.
echo ===============================
echo   SERIES TRACKER MANAGER
echo ===============================
echo.

:check_docker
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not running!
    echo.
    echo Please open Docker Desktop and wait for it to start.
    echo Then run this script again.
    echo.
    pause
    exit
)

echo SUCCESS: Docker is running!
timeout 1
goto menu

:menu
cls
echo.
echo ===============================
echo   SERIES TRACKER MANAGER
echo ===============================
echo.
echo  1 - START ALL SERVICES (First time)
echo  2 - START SERVICES ONLY (if already initialized)
echo  3 - STOP ALL SERVICES
echo  4 - CHECK STATUS
echo  5 - VIEW LOGS
echo  6 - RESET EVERYTHING
echo  0 - EXIT
echo.
set /p choice="Choose option: "

if "%choice%"=="1" goto start_first_time
if "%choice%"=="2" goto start_services
if "%choice%"=="3" goto stop_all
if "%choice%"=="4" goto check_status
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto reset_all
if "%choice%"=="0" goto exit
goto menu

:start_first_time
echo.
echo 🚀 FIRST TIME SETUP...
echo.
echo This will initialize Airflow database and create user.
echo.
docker-compose down
echo.
echo Step 1: Starting databases...
docker-compose up -d postgres airflow-postgres airflow-redis
timeout 15
echo.
echo Step 2: Initializing Airflow...
docker-compose up airflow-webserver
echo.
echo If you see Airflow running, press Ctrl+C to stop it.
echo Then run option 2 to start services normally.
echo.
pause
goto menu

:start_services
echo.
echo 🚀 STARTING SERVICES...
echo.
docker-compose down
echo.
echo Starting all services...
docker-compose up -d
echo.
echo ⏳ Waiting for services to start (30 seconds)...
timeout 30
echo.
echo ✅ SERVICES STARTED!
echo 🌐 Airflow: http://localhost:8080
echo 👤 Username: airflow
echo 🔐 Password: airflow
echo.
echo 🗄️ PostgreSQL: localhost:5432
echo.
pause
goto menu

:stop_all
echo.
echo 🛑 STOPPING ALL SERVICES...
docker-compose down
echo.
echo ✅ All services stopped!
echo.
pause
goto menu

:check_status
echo.
echo 📊 SERVICE STATUS:
echo.
docker-compose ps
echo.
echo 🔍 Checking Airflow...
curl -s http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Airflow Web: RUNNING
) else (
    echo ❌ Airflow Web: NOT RESPONDING
)
echo.
echo 🔗 URLs:
echo 🌐 Airflow: http://localhost:8080
echo 🗄️ PostgreSQL: localhost:5432
echo.
pause
goto menu

:view_logs
echo.
echo 📜 AIRFLOW LOGS:
echo.
docker-compose logs airflow-webserver --tail=30
echo.
echo Press any key to continue...
pause >nul
goto menu

:reset_all
echo.
echo 💥 RESETTING EVERYTHING...
echo.
echo This will delete all data and start fresh!
set /p confirm="Are you sure? (YES/no): "
if /i not "%confirm%"=="YES" goto menu

docker-compose down -v
docker system prune -f
echo.
echo ✅ Everything reset!
echo Run option 1 for first time setup.
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye!
timeout 2