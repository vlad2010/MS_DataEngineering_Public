@echo off 

REM cppcheck --enable=warning,style,performance,portability,information,unusedFunction --error-exitcode=1 --force --inconclusive --template=gcc --suppress=missingIncludeSystem --suppress=missingInclude --suppress=syntaxError      src\code > cppcheck_report.txt 2>&1


if "%1"=="" (
    echo Please provide a folder name.
    exit /b 1
)

set FOLDER=%1
for %%F in ("%FOLDER%") do set BASENAME=%%~nF

REM cppcheck --enable=warning,style,performance,portability,information,unusedFunction --error-exitcode=1 --force --inconclusive --template=gcc --suppress=missingIncludeSystem --suppress=missingInclude --suppress=syntaxError %FOLDER% > cppcheck_report_%BASENAME%.txt 2>&1

cppcheck --enable=warning,style,performance,portability,information,unusedFunction --error-exitcode=1 --force --inconclusive --template=gcc --suppress=missingIncludeSystem --suppress=missingInclude --output-format=sarif --suppress=syntaxError --output-file=cppcheck_report_%BASENAME%.sarif --template="{file}:{line}:{severity}:{message}"  %FOLDER%





