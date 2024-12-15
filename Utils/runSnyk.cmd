@echo off
:: Check if the first argument is empty
if "%~1"=="" (
    echo Usage: runSnyk.bat ^<path to src folder^>
    exit /b -1
)

:: Set the reports folder to the current directory's reports folder
set "REPORTS=%cd%\reports"

:: Navigate to the specified folder
cd /d "%~1"

:: Generate the report filename with the current date and time
for /f "tokens=2 delims==" %%A in ('wmic os get localdatetime /value') do set datetime=%%A
set "datetime=%datetime:~0,4%_%datetime:~4,2%_%datetime:~6,2%_%datetime:~8,2%_%datetime:~10,2%"

set "report_filename=%REPORTS%\snyk_report_%datetime%.sarif"

echo %report_filename%

:: Run the Snyk command and measure the time
echo Running Snyk...
snyk code test --org=c0d94333-4cd8-4428-8599-9080ca7cef78 --sarif-file-output="%report_filename%"

:: Go back to the original directory
cd -

