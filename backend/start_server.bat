@echo off
cd %~dp0
python -m uvicorn carbon_calculator:app --host 0.0.0.0 --port 8002 