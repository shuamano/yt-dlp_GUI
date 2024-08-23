@echo off
setlocal

:: Set variables
set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
set "YTDLP_URL=https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
set "DOWNLOAD_DIR=%TEMP%\tools"
set "INSTALL_DIR=C:\Program Files\tools"

:: Create directories
if not exist "%DOWNLOAD_DIR%" mkdir "%DOWNLOAD_DIR%"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Download and extract FFmpeg
echo Downloading FFmpeg...
powershell -Command "Invoke-WebRequest -Uri %FFMPEG_URL% -OutFile %DOWNLOAD_DIR%\ffmpeg.zip"
echo Extracting FFmpeg...
powershell -Command "Expand-Archive -Path %DOWNLOAD_DIR%\ffmpeg.zip -DestinationPath %DOWNLOAD_DIR%\ffmpeg"
xcopy /E /I /Y "%DOWNLOAD_DIR%\ffmpeg\ffmpeg-*-essentials_build\bin" "%INSTALL_DIR%\ffmpeg"

:: Download yt-dlp
echo Downloading yt-dlp...
powershell -Command "Invoke-WebRequest -Uri %YTDLP_URL% -OutFile %INSTALL_DIR%\yt-dlp.exe"

:: Add to PATH
setx PATH "%INSTALL_DIR%\ffmpeg;%INSTALL_DIR%;%%PATH%%"

echo Installation completed. Please restart your command prompt or system for changes to take effect.

:: Cleanup
rd /s /q "%DOWNLOAD_DIR%"

endlocal
exit /b
