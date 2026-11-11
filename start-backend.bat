@echo off
cd /d %~dp0backend
py -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
