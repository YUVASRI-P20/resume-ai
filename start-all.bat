@echo off
title InterviewIQ AI — Fullstack Runner
echo ========================================================
echo   Starting InterviewIQ AI (Backend + Frontend)
echo ========================================================

echo.
echo [1/2] Launching FastAPI Backend on http://localhost:8000 ...
start "InterviewIQ Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo.
echo [2/2] Launching Next.js Frontend on http://localhost:3000 ...
start "InterviewIQ Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   InterviewIQ is starting!
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - Swagger Docs: http://localhost:8000/api/v1/docs
echo ========================================================
