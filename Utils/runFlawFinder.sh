#!/bin/sh

echo "Flawfinder, please run me in WSL"

if [ $1 ]
then
  folder=$1
  bname=$(basename "$folder")
  REPORT_FILE="$(pwd)/reports/flawfinder_report_${bname}_$(date +'%d_%m_%Y_%H_%M').sarif"
  
  cd "$folder"
  pwd
  echo "Folder : ${folder} Bname : ${bname}"
  echo "Report file is: $REPORT_FILE"

  python3 -m flawfinder --sarif . > "$REPORT_FILE"

  cd -
else
  me=$(basename "$0")
  echo "Usage: $me <path to files for scan>"
fi


