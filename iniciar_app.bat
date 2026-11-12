@echo off
cd /d "%~dp0"
set FLASK_APP=wsgi.py
set FLASK_ENV=development
start "" http://127.0.0.1:5000/inicio
python -m flask run --host=127.0.0.1 --port=5000
