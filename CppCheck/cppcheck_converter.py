import json
import re
from datetime import datetime
import argparse

def parse_cppcheck_report(input_file):
    # Regex to capture cppcheck report lines
    issue_pattern = re.compile(r"^(.*):(\d+):(\d+): (warning|error): (.*)\[(.*)\]$")
    
    issues = []
    current_source_code = ""

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            match = issue_pattern.match(line.strip())
            if match:
                file_path, line_num, column, severity, message, type_code = match.groups()
                # Ignore "nofile" entries
                if "nofile" not in file_path:
                    # Extract the sharing part from the path starting with "Sharing_" and ending with the first delimiter
                    sharing_match = re.search(r"(Sharing_[^/\\]+)", file_path)
                    sharing = sharing_match.group(1) if sharing_match else "unknown"
                    
                    # If there is any leftover source code, we save it before resetting
                    if current_source_code:
                        current_source_code = current_source_code.strip()

                    issues.append({
                        "line": int(line_num),
                        "file": file_path,
                        "severity": severity,
                        "text": message,
                        "type": type_code,
                        "sharing": sharing,
                        "source_code": current_source_code if current_source_code else type_code
                    })
                    
                    # Reset source code for the next file
                    current_source_code = ""
            else:
                # Collect any additional source code in the subsequent lines
                current_source_code += line.strip() + " "

    return issues

def write_json(output_file, path_to_source_folder, issues, extensions):
    output_data = {
        "pathToSourceFolder": path_to_source_folder,
        "dateAndTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": extensions,
        "issues": issues
    }
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(output_data, out_file, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Convert SARIF file to JSON format.")

    # Positional arguments
    parser.add_argument('input_file', help="Input CppCheck file")
    parser.add_argument('output_json_file', help="Output JSON file")
    parser.add_argument('source_folder', help="Path to the source folder")

    # Optional argument to handle file extensions , we need it on later stages for example   --extensions c cpp
    parser.add_argument('--extensions', nargs='+', required=True, help="List of file extensions to filter by")

    args = parser.parse_args()
    issues = parse_cppcheck_report(args.input_file)
    write_json(args.output_json_file, args.source_folder, issues, args.extensions)

if __name__ == "__main__":
    main()
