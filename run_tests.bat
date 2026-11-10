@echo off
cd c:\Users\taras\OneDrive\Plocha\Projects\App\Causa
call .venv\Scripts\activate
python -m pytest tests/ -x -v --tb=short 2>&1 | findstr "PASSED|FAILED|ERROR|test_"