@echo off

set start_time=%time%
echo Start Time: %start_time%

set OUT=GroupedRepresentation
set JSON=FinalReports

rmdir /S /Q "%OUT%"

mkdir "%OUT%"

set CPP_CHECK_FILE=cppcheck_report_cpp_csharp_15_10_2024.json


python print_grouped_error_log.py "%JSON%\%CPP_CHECK_FILE%" sharing > "%OUT%/cppcheck_report.txt"
python print_grouped_error_log.py "%JSON%\flawfinder_simple_report_ext_28_09_2024.json" sharing > "%OUT%/flawfinder_report.txt"
python print_grouped_error_log.py "%JSON%\semgrep_simple_ext_28_09_2024.json" sharing > "%OUT%/semgrep_report.txt"
python print_grouped_error_log.py "%JSON%\snyk_simple_report_ext_29_09_2024.json" sharing > "%OUT%/snyk_report.txt"


python print_grouped_error_log.py "%JSON%\%CPP_CHECK_FILE%" sharing --filter Conversation_001 > "%OUT%/cppcheck_report_cnv001.txt"
python print_grouped_error_log.py "%JSON%\flawfinder_simple_report_ext_28_09_2024.json" sharing --filter Conversation_001 > "%OUT%/flawfinder_report_cnv001.txt"
python print_grouped_error_log.py "%JSON%\semgrep_simple_ext_28_09_2024.json" sharing --filter Conversation_001 > "%OUT%/semgrep_report_cnv001.txt"
python print_grouped_error_log.py "%JSON%\snyk_simple_report_ext_29_09_2024.json" sharing --filter Conversation_001 > "%OUT%/snyk_report_cnv001.txt"


python sharings_intersections.py "%JSON%" "%OUT%/intersections_full.txt" --full-path --line-numbers 
python sharings_intersections.py "%JSON%" "%OUT%/intersections_on_full_path.txt" --full-path
python sharings_intersections.py "%JSON%" "%OUT%/intersections_on_sharing.txt"


set end_time=%time%
echo End Time: %end_time%


REM Calculating the difference
REM Note: This works well if the script executes within the same hour.
set /A elapsed_time=((%end_time:~0,2%*3600 + %end_time:~3,2%*60 + %end_time:~6,2%) - (%start_time:~0,2%*3600 + %start_time:~3,2%*60 + %start_time:~6,2%))
echo Elapsed Time (in seconds): %elapsed_time%
pause