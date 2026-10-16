@echo off
setlocal enabledelayedexpansion
title Horizon: Under Place - Radio Mod Uninstaller
color 0E

echo ======================================================================
echo           UNDER PLACE RADIO STATION - RESTAURADOR VANILLA
echo ======================================================================
echo.

set "GAME_DIR="

if exist "ForzaHorizon4.exe" (
    set "GAME_DIR=%CD%"
) else if exist "..\ForzaHorizon4.exe" (
    set "GAME_DIR=%~dp0.."
) else if exist "F:\SteamLibrary\steamapps\common\ForzaHorizon4\ForzaHorizon4.exe" (
    set "GAME_DIR=F:\SteamLibrary\steamapps\common\ForzaHorizon4"
)

if "%GAME_DIR%"=="" (
    set /p "GAME_DIR=Introduce la ruta de Forza Horizon 4: "
)

set "BAK_DIR=%~dp0vanilla_backup"

if not exist "%BAK_DIR%\R4_Tracks.bank" (
    color 0C
    echo [ERROR] No se encontraron archivos de respaldo en %BAK_DIR%.
    pause
    exit /b 1
)

echo Restaurando banco de audio original Horizon XS...
copy /Y "%BAK_DIR%\R4_Tracks.bank" "%GAME_DIR%\media\audio\fmodopus\x64\R4_Tracks.bank" >nul

echo Restaurando RadioInfo MX y EN...
copy /Y "%BAK_DIR%\RadioInfo_MX.xml" "%GAME_DIR%\media\audio\RadioInfo_MX.xml" >nul
copy /Y "%BAK_DIR%\RadioInfo_EN.xml" "%GAME_DIR%\media\audio\RadioInfo_EN.xml" >nul

echo Restaurando AlbumArt original...
copy /Y "%BAK_DIR%\AlbumArt_hires.zip" "%GAME_DIR%\media\ui\textures\hires\data_bound\AlbumArt.zip" >nul
copy /Y "%BAK_DIR%\AlbumArt_normal.zip" "%GAME_DIR%\media\ui\textures\data_bound\AlbumArt.zip" >nul

echo Restaurando RadioStations original...
copy /Y "%BAK_DIR%\RadioStations_hires.zip" "%GAME_DIR%\media\ui\textures\hires\data_bound\RadioStations.zip" >nul
copy /Y "%BAK_DIR%\RadioStations_normal.zip" "%GAME_DIR%\media\ui\textures\data_bound\RadioStations.zip" >nul

color 0A
echo.
echo ======================================================================
echo   RESTAURACION COMPLETADA!
echo   Horizon XS original ha sido restablecido a su estado de fabrica.
echo ======================================================================
echo.
pause
