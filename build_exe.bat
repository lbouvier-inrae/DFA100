@echo off
pip install -r requirements.txt
pyinstaller --noconsole --add-data "src/settings.json;src" src/main.py
pause
