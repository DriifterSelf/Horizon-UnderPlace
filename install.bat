@echo off
setlocal enabledelayedexpansion
title Horizon: Under Place - Radio Mod Installer
color 0B

echo ======================================================================
echo           UNDER PLACE RADIO STATION - FORZA HORIZON 4
echo           Reemplazo Underground / Club / Plugg para Horizon XS
echo ======================================================================
echo.

:: Detect game directory
set "GAME_DIR="

if exist "ForzaHorizon4.exe" (
    set "GAME_DIR=%CD%"
) else if exist "..\ForzaHorizon4.exe" (
    set "GAME_DIR=%~dp0.."
) else if exist "F:\SteamLibrary\steamapps\common\ForzaHorizon4\ForzaHorizon4.exe" (
    set "GAME_DIR=F:\SteamLibrary\steamapps\common\ForzaHorizon4"
)

if "%GAME_DIR%"=="" (
    echo [ERROR] No se detecto automaticamente la carpeta de Forza Horizon 4.
    set /p "GAME_DIR=Por favor introduce la ruta completa del juego: "
)

if not exist "%GAME_DIR%\ForzaHorizon4.exe" (
    color 0C
    echo [ERROR] No se encontro ForzaHorizon4.exe en la ruta especificada:
    echo "%GAME_DIR%"
    echo Instalacion cancelada.
    pause
    exit /b 1
)

echo [OK] Carpeta del juego detectada: "%GAME_DIR%"
echo.

:: 1. Create backups if not exist
set "MOD_SRC=%~dp0mod_files"
set "BAK_DIR=%~dp0vanilla_backup"

if not exist "%BAK_DIR%" mkdir "%BAK_DIR%"

echo === Paso 1: Verificando respaldos vanilla ===
if not exist "%BAK_DIR%\R4_Tracks.bank" (
    echo Creando respaldo de R4_Tracks.bank...
    copy /Y "%GAME_DIR%\media\audio\fmodopus\x64\R4_Tracks.bank" "%BAK_DIR%\R4_Tracks.bank" >nul
)
if not exist "%BAK_DIR%\RadioInfo_MX.xml" (
    echo Creando respaldo de RadioInfo_MX.xml...
    copy /Y "%GAME_DIR%\media\audio\RadioInfo_MX.xml" "%BAK_DIR%\RadioInfo_MX.xml" >nul
)
if not exist "%BAK_DIR%\RadioInfo_EN.xml" (
    echo Creando respaldo de RadioInfo_EN.xml...
    copy /Y "%GAME_DIR%\media\audio\RadioInfo_EN.xml" "%BAK_DIR%\RadioInfo_EN.xml" >nul
)
if not exist "%BAK_DIR%\AlbumArt_hires.zip" (
    echo Creando respaldo de AlbumArt hires...
    copy /Y "%GAME_DIR%\media\ui\textures\hires\data_bound\AlbumArt.zip" "%BAK_DIR%\AlbumArt_hires.zip" >nul
)
if not exist "%BAK_DIR%\AlbumArt_normal.zip" (
    echo Creando respaldo de AlbumArt normal...
    copy /Y "%GAME_DIR%\media\ui\textures\data_bound\AlbumArt.zip" "%BAK_DIR%\AlbumArt_normal.zip" >nul
)
if not exist "%BAK_DIR%\RadioStations_hires.zip" (
    echo Creando respaldo de RadioStations hires...
    copy /Y "%GAME_DIR%\media\ui\textures\hires\data_bound\RadioStations.zip" "%BAK_DIR%\RadioStations_hires.zip" >nul
)
if not exist "%BAK_DIR%\RadioStations_normal.zip" (
    echo Creando respaldo de RadioStations normal...
    copy /Y "%GAME_DIR%\media\ui\textures\data_bound\RadioStations.zip" "%BAK_DIR%\RadioStations_normal.zip" >nul
)
echo [OK] Respaldos asegurados en %BAK_DIR%.
echo.

:: 2. Deploy mod files
echo === Paso 2: Instalando archivos de Under Place ===

echo Copiando banco de audio FMOD R4_Tracks.bank (114 MB)...
copy /Y "%MOD_SRC%\media\audio\fmodopus\x64\R4_Tracks.bank" "%GAME_DIR%\media\audio\fmodopus\x64\R4_Tracks.bank" >nul

echo Copiando metadatos y cues (RadioInfo MX / EN)...
copy /Y "%MOD_SRC%\media\audio\RadioInfo_MX.xml" "%GAME_DIR%\media\audio\RadioInfo_MX.xml" >nul
copy /Y "%MOD_SRC%\media\audio\RadioInfo_EN.xml" "%GAME_DIR%\media\audio\RadioInfo_EN.xml" >nul

echo Copiando AlbumArt.zip con portadas BC7 bit-perfect...
copy /Y "%MOD_SRC%\media\ui\textures\hires\data_bound\AlbumArt.zip" "%GAME_DIR%\media\ui\textures\hires\data_bound\AlbumArt.zip" >nul
copy /Y "%MOD_SRC%\media\ui\textures\data_bound\AlbumArt.zip" "%GAME_DIR%\media\ui\textures\data_bound\AlbumArt.zip" >nul

echo Copiando logotipos de estacion Under Place...
copy /Y "%MOD_SRC%\media\ui\textures\hires\data_bound\RadioStations.zip" "%GAME_DIR%\media\ui\textures\hires\data_bound\RadioStations.zip" >nul
copy /Y "%MOD_SRC%\media\ui\textures\data_bound\RadioStations.zip" "%GAME_DIR%\media\ui\textures\data_bound\RadioStations.zip" >nul

color 0A
echo.
echo ======================================================================
echo   INSTALACION COMPLETADA EXITOSAMENTE!
echo   La estacion Horizon XS ha sido reemplazada por "Under Place".
echo   - 20 Canciones Underground / Club / Plugg / Breakcore
echo   - Portadas personalizadas en alta definicion
echo   - Cues musicales sincronizados con las carreras y podio
echo ======================================================================
echo.
pause
