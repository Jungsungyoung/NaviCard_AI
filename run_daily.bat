@echo off
cd /d "d:\01_DevProjects\Python_Projects\NaviCard_AI"
call venv\Scripts\activate.bat

echo [Starting NaviCard AI] %date% %time% >> run_log.txt
python src/main.py >> run_log.txt 2>&1
echo [Finished] %date% %time% >> run_log.txt

echo Done. Log saved to run_log.txt
