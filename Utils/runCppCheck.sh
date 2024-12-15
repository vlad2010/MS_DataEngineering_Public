#!/bin/sh 

echo "Run me from WSL"

SUPPRESS="--suppress=missingIncludeSystem --suppress=missingInclude --suppress=syntaxError --suppress=unusedStructMember --suppress=unreadVariable --suppress=passedByValue --suppress=constParameter --suppress=unusedFunction --suppress=unusedVariable --suppress=constVariable --suppress=functionConst  --suppress=constParameterPointer  --suppress=noExplicitConstructor  --suppress=cstyleCast --suppress=variableScope --suppress=normalCheckLevelMaxBranches --suppress=unusedPrivateFunction --suppress=functionStatic --suppress=functionConst --suppress=initializerList --suppress=constParameterReference
--suppress=useStlAlgorithm --suppress=unknownMacro --suppress=constVariablePointer  --suppress=constParameterCallback  --suppress=ctuOneDefinitionRuleViolation"

if [ $1 ]
then
  folder=$1
  bname=$(basename "$folder")
  
  REPORT_FILE="$(pwd)/reports/cppcheck_report_${bname}_$(date +'%d_%m_%Y_%H_%M').txt"
  pwd
 
  echo "Folder : ${folder} Bname : ${bname}"
  echo "REPORT_FILE: ${REPORT_FILE}\n"
  
  time cppcheck --quiet --enable=warning,style,performance,portability,information,unusedFunction --error-exitcode=1 --force --inconclusive $SUPPRESS --template=gcc  "$folder" 2> "${REPORT_FILE}"
    
  echo "Err code: $?"
else
  me=$(basename "$0")
  echo "Usage: $me <path to files for scan>"
fi



