#!/bin/bash 


DT="2024_11_12_20_12_51"

../Utils/get_unique_files.py  ./reports/unique_files.json ./reports/uniqie_info.txt reports/report_cppcheck_${DT}.json  reports/report_flawfinder_${DT}.json  reports/report_semgrep_${DT}.json  reports/report_snyk_${DT}.json

