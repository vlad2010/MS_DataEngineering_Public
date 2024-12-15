#!/bin/sh 

if [ -z "$1" ]
then
    echo "Usage: runSnyk.sh <path to src folder>"
    exit -1
fi

REPORTS="$(pwd)/reports"

cd "$1"
report_filename="${REPORTS}/snyk_report_$(date +'%d_%m_%Y_%H_%M').sarif"

echo "$report_filename"
time snyk code test --org=c0d94333-4cd8-4428-8599-9080ca7cef78 --sarif-file-output="./${report_filename}"  

cd - 


