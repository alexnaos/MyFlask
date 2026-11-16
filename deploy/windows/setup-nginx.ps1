<#
.SYNOPSIS
  Развёртывание Nginx как службы Windows + установка отказоустойчивого конфигура
  балансировщика (основной Orange Pi 192.168.1.23:8080, резерв 127.0.0.1:8080).

.DESCRIPTION
  - Если nginx не установлен — скачивает ZIP с nginx.org и распаковывает в C:\nginx.
  - Копирует deploy/windows/nginx.conf.
  - Регистрирует Nginx как Windows-службу через NSSM (nssm.exe лежит в корне репозитория).
  Запускать ОТ ИМЕНИ АДМИНИСТРАТОРА.
#>
$ErrorActionPreference = 'Stop'

# Проверка прав администратора
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Запустите PowerShell от имени Администратора.'
}

$RepoRoot   = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # ...\MyFlask
$NginxDir   = 'C:\nginx'
$ConfDir    = Join-Path $NginxDir 'conf'
$NginxExe   = Join-Path $NginxDir 'nginx.exe'
$NssmExe    = Join-Path $RepoRoot 'nssm.exe'
$SourceConf = Join-Path $PSScriptRoot 'nginx.conf'

# --- 1. Установка Nginx -----------------------------------------------------
if (-not (Test-Path $NginxExe)) {
    Write-Host 'Nginx не найден. Скачиваю...' -ForegroundColor Cyan
    $version = '1.27.3'
    $zip = Join-Path $env:TEMP "nginx-$version.zip"
    Invoke-WebRequest "https://nginx.org/download/nginx-$version.zip" -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $env:TEMP -Force
    $extracted = Get-ChildItem $env:TEMP -Directory | Where-Object { $_.Name -like "nginx-$version*" } | Select-Object -First 1
    Move-Item $extracted.FullName $NginxDir -Force
    Remove-Item $zip -Force
}

# --- 2. Конфиг --------------------------------------------------------------
Copy-Item $SourceConf (Join-Path $ConfDir 'nginx.conf') -Force

Write-Host 'Проверка конфигурации...' -ForegroundColor Cyan
& $NginxExe -t -p "$NginxDir\"
if ($LASTEXITCODE -ne 0) { throw 'nginx -t завершился с ошибкой. Проверьте конфиг.' }

# --- 3. Служба через NSSM ---------------------------------------------------
if (-not (Test-Path $NssmExe)) { throw "Не найден $NssmExe — положите nssm.exe в корень репозитория MyFlask" }

& $NssmExe install MyFlaskNginx $NginxExe "-p $NginxDir"
& $NssmExe set MyFlaskNginx AppDirectory $NginxDir
& $NssmExe set MyFlaskNginx AppExit Default Restart
& $NssmExe set MyFlaskNginx Start SERVICE_AUTO_START
& $NssmExe start MyFlaskNginx

Write-Host ''
Write-Host 'Готово. Nginx слушает :80 и проксирует на Flask с failover ~2 сек.' -ForegroundColor Green
Write-Host 'ВАЖНО: остановите/удалите старую службу MyFlaskApp (NSSM), т.к. она занимает порт 8080.' -ForegroundColor Yellow
Write-Host '  nssm.exe stop MyFlaskApp; nssm.exe remove MyFlaskApp confirm'