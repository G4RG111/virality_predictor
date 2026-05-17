$root = "d:\ML Projects\ViralityPredictor\vibe-predictor"

Write-Host "Stopping existing Node processes..." -ForegroundColor Yellow
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Cleaning Next.js cache..." -ForegroundColor Yellow
Remove-Item -Recurse -Force "$root\frontend\.next" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$root\frontend\.next-build" -ErrorAction SilentlyContinue

Write-Host "Starting backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; uvicorn app.main:app --reload --port 8000"

Start-Sleep -Seconds 3

Write-Host "Starting frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

Write-Host ""
Write-Host "Both servers starting." -ForegroundColor Green
Write-Host "Wait ~60 seconds, then open: http://localhost:3000" -ForegroundColor Green
