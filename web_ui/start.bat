@echo off
echo Starting Web UI server...
echo Web UI will be available at http://localhost:8080
echo.
echo Make sure the API server is running on http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python serve.py

pause
