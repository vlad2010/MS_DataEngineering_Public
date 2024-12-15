import json
from datetime import datetime
import argparse
import os

def get_lines_from_file(filename, start_line, end_line):
    """
    Returns lines from a file starting from 'start_line' to 'end_line'.

    Parameters:
    - filename (str): Path to the file.
    - start_line (int): The starting line number (1-based).
    - end_line (int): The ending line number (1-based).

    Returns:
    - list: A list of lines from start_line to end_line.
    """
    lines = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for current_line_num, line in enumerate(file, start=1):
                if start_line <= current_line_num <= end_line:
                    lines.append(line.rstrip('\n'))
                elif current_line_num > end_line:
                    break
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return lines[0].strip()

def convert_sarif_to_json(input_sarif_file, output_json_file, path_to_source_folder, extensions):
    # Open and load the SARIF file
    with open(input_sarif_file, 'r', encoding='utf-8') as file:
        sarif_data = json.load(file)
    
    issues = []
    
    # Extracting the relevant SARIF results and converting them into the desired schema format
    for run in sarif_data.get("runs", []):
        for result in run.get("results", []):
            for location in result.get("locations", []):
                # Extract necessary data
                physical_location = location.get("physicalLocation", {})
                artifact_location = physical_location.get("artifactLocation", {})
                region = physical_location.get("region", {})
                
                file_path = artifact_location.get("uri", "nofile")
                line_number = region.get("startLine", 0)
                message = result.get("message", {}).get("text", "")
                severity = result.get("level", "warning")  # Assume default to "warning" if not found
                rule = result.get("ruleId", "unknown")
                
                # Ignore "nofile" entries
                if "nofile" not in file_path:
                    # Extract sharing from the path (starting from "Sharing_" and ending at the first delimiter)
                    sharing_match = file_path.split("/")  # Split based on slashes for paths
                    sharing = next((segment for segment in sharing_match if segment.startswith("Sharing_")), "unknown")
                    
                    # Extract the source code from snippet.text (if available)
                    location_region = physical_location.get("region", {})
                    if "snippet" in location_region:
                        source_code = location_region.get("snippet", {}).get("text", rule)
                        print(f"location region present: {location_region}")
                    else:
                        # only line number is available
                        startLine = int(location_region.get("startLine"))
                        endLine = int(location_region.get("endLine"))
                        full_path = os.path.join(path_to_source_folder, file_path)
                        source_code = get_lines_from_file(full_path, startLine, endLine)
                    
                    issues.append({
                        "line": line_number,
                        "file": file_path,
                        "severity": severity,
                        "text": message,
                        "type": rule,
                        "sharing": sharing,
                        "source_code": source_code
                    })
    
    # Create the final output in the desired format
    output_data = {
        "pathToSourceFolder": path_to_source_folder,
        "dateAndTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": extensions,
        "issues": issues
    }
    
    # Write the output JSON file
    with open(output_json_file, 'w', encoding='utf-8') as out_file:
        json.dump(output_data, out_file, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Convert SARIF file to JSON format.")

    # Positional arguments
    parser.add_argument('input_sarif_file', help="Input SARIF file")
    parser.add_argument('output_json_file', help="Output JSON file")
    parser.add_argument('source_folder', help="Path to the source folder")

    # Optional argument to handle file extensions
    parser.add_argument('--extensions', nargs='+', required=True, help="List of file extensions to filter by")

    args = parser.parse_args()

    convert_sarif_to_json(args.input_sarif_file, args.output_json_file, args.source_folder, args.extensions)

    print(f"Report converted and written to : {args.output_json_file}")

if __name__ == "__main__":
    main()
