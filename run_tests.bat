@echo off
cd /d E:\Dev\GnosisCore
set PYTHONPATH=E:\Dev\GnosisCore;%PYTHONPATH%
python -m pytest tests -v --tb=short
pause
