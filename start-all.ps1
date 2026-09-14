# InterviewIQ AI — Fullstack PowerShell Runner
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting InterviewIQ AI (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Launching FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --reload --port 8000"

Write-Host "`n[2/2] Launching Next.js Frontend on http://localhost:3000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  InterviewIQ services initiated:" -ForegroundColor White
Write-Host "  - Frontend:     http://localhost:3000" -ForegroundColor Green
Write-Host "  - Backend API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  - Swagger Docs: http://localhost:8000/api/v1/docs" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
