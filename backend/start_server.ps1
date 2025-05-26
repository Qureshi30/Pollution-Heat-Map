# PowerShell script to start the carbon calculator backend server
Set-Location -Path $PSScriptRoot
python -m uvicorn carbon_calculator:app --host 0.0.0.0 --port 8002 