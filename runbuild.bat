@echo off

setlocal

call :runme call app\omni.code.bat --/rtx/ecoMode/enabled=false --ext-folder exts --enable robotica.example.video.scrubbing %* <NUL
@REM _build\windows-x86_64\release\robotica-ext-property-animation.bat %* <NUL

goto :eof

:runme
%*
goto :eof
