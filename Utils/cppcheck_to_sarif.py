import json
import sys
import re
import os
import uuid

def parse_cppcheck_output(file_path):
    """Parse Cppcheck text output and extract errors and warnings."""
    issues = []
    issue_pattern = re.compile(r"(.+):(\d+):\s+(.+):\s+(.+)")
    
    with open(file_path, 'r') as f:
        for line in f:
            match = issue_pattern.match(line)
            if match:
                file_name = match.group(1)
                line_number = int(match.group(2))
                severity = match.group(3)
                message = match.group(4)
                
                issues.append({
                    "file": file_name,
                    "line": line_number,
                    "severity": severity,
                    "message": message
                })
    
    return issues

def generate_sarif(issues):
    """Generate SARIF JSON structure from parsed issues."""
    sarif_template = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Cppcheck",
                        "version": "2.x",
                        "informationUri": "http://cppcheck.sourceforge.net",
                        "rules": []
                    }
                },
                "results": []
            }
        ]
    }

    for issue in issues:
        sarif_template["runs"][0]["results"].append({
            "ruleId": str(uuid.uuid4()),  # Unique ID for each rule
            "level": "error" if issue["severity"] == "error" else "warning",
            "message": {
                "text": issue["message"]
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": os.path.abspath(issue["file"])
                        },
                        "region": {
                            "startLine": issue["line"]
                        }
                    }
                }
            ]
        })
    
    return sarif_template

def save_sarif(output_path, sarif_data):
    """Save SARIF data to a file."""
    with open(output_path, 'w') as f:
        json.dump(sarif_data, f, indent=4)

def main(input_file, output_file):
    issues = parse_cppcheck_output(input_file)
    sarif_data = generate_sarif(issues)
    save_sarif(output_file, sarif_data)
    print(f"SARIF report generated: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: cppcheck_to_sarif.py <cppcheck_output.txt> <output.sarif>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_file, output_file)



