#!/bin/sh

if [ $1 ]
then
  folder=$1
  bname=$(basename "$folder")
  cd "$folder"
  pwd
  echo "Folder : ${folder} Bname : ${bname}"
  # time semgrep scan -v --no-force-color --text --exclude '**/*.html'  --include '**/*.c' --include '**/*.cpp' --include '**/*.cs' .

  time semgrep scan -v --no-force-color --sarif --sarif-output="semgrep_test_${bname}.sarif" --text --text-output="semgrep_test_${bname}.txt" --exclude '**/*.html'  --include '**/*.c' --include '**/*.cpp' --include '**/*.cs' .


  cd -
else
  me=$(basename "$0")
  echo "Usage: $me <path to files for scan>"
fi


