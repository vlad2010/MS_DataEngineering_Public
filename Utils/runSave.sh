#!/bin/bash 

PYTHON_EXE=python

# Try to run the script with python or python3
if command -v python &>/dev/null; then
    PYTHON_EXE=python
elif command -v python3 &>/dev/null; then
    PYTHON_EXE=python3
else
    echo "Neither Python nor Python3 is installed. Please install Python."
    exit
fi

echo "Python exe is: ${PYTHON_EXE}"

"$PYTHON_EXE" save_code_snippets.py "../../../DevGPT/snapshot_20231012" "$1" --lang=cpp --lang=csharp 

