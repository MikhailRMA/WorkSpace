@echo off
echo Creating project structure...

mkdir "C:\Users\majkl\WorkSpace\series_tracker_project"
mkdir "C:\Users\majkl\WorkSpace\series_tracker_project\dags"
mkdir "C:\Users\majkl\WorkSpace\series_tracker_project\dags\helpers"
mkdir "C:\Users\majkl\WorkSpace\series_tracker_project\data"
mkdir "C:\Users\majkl\WorkSpace\series_tracker_project\docs"
mkdir "C:\Users\majkl\WorkSpace\series_tracker_project\docker"

cd "C:\Users\majkl\WorkSpace\series_tracker_project"

echo. > dags\series_etl_dag.py
echo. > dags\helpers\parser.py
echo. > dags\helpers\database.py
echo. > dags\helpers\email_sender.py
echo. > requirements.txt
echo. > README.md

echo Project structure created successfully!
dir /s