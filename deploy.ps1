# 1-Click Deploy Script for GitHub & Render
Write-Host "Committing and Pushing latest updates to GitHub..." -ForegroundColor Cyan

Set-Location -Path $PSScriptRoot

git add .
git commit -m "Deploy latest updates to GitHub"
git push -u origin main

Write-Host "Done! GitHub repository updated. Render will auto-deploy the changes!" -ForegroundColor Green
