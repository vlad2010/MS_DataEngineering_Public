#!/bin/bash 

PYTHON_EXE=python

DEVGPT="../../../DevGPT/snapshot_20231012"

if [ -z "$1" ]
then
    echo "Usage: $0 <path to src folder>"
    exit -1
fi


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

"$PYTHON_EXE" save_code_snippets.py "$DEVGPT" "$1/cpp" --lang=cpp
"$PYTHON_EXE" save_code_snippets.py "$DEVGPT" "$1/csharp" --lang=csharp
# "$PYTHON_EXE" save_code_snippets.py "$DEVGPT" "$1/python" --lang=python
# "$PYTHON_EXE" save_code_snippets.py "$DEVGPT" "$1/java" --lang=java



