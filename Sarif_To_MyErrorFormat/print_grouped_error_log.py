import re
import json
import sys
from collections import defaultdict
import os
from pathlib import Path
import argparse

import common_utils

# error types map
g_error_types = {}

# number of groups
g_number_of_groups = 0

g_number_of_errors = 0

# file extensions, effectively programming languahe
g_extensions = {}

# severity of issue
g_severity = {}

# files fictionary, save all files and
g_files_dict = {}

def load_json(json_file):
    """Load JSON data from the file."""
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def group_issues_by_field(issues, group_field):
    """Group issues by a specified field."""
    grouped_issues = defaultdict(list)
    
    # Group issues by the specified field
    for issue in issues:
        key = issue.get(group_field, "unknown")
        grouped_issues[key].append(issue)
    
    return grouped_issues

def update_frequency_table(value, dict):
    if value in dict:
        dict[value] = dict[value] + 1
    else:
        dict[value] = 1

def print_frequency_table(message, dict, output_file=sys.stdout):
    for typename, typenumber in dict.items():
        print(f"{message}: {typename} - {typenumber}", file=output_file)

def print_grouped_issues(grouped_issues, group_field, path_to_source_folder, output_file=sys.stdout):
    global g_number_of_groups
    """Print grouped issues and add a delimiter line between groups."""
    for key, group in grouped_issues.items():

        g_number_of_groups += 1
        print(f"Group: {g_number_of_groups} === Grouped by {group_field}: {key} ===", file=output_file)
        for issue in group:
            print_issue(issue, path_to_source_folder, output_file)
        print("\n" + "="*50 + "\n", file=output_file)


def print_issue(issue, path_to_source_folder, output_file=sys.stdout):
    global g_error_types, g_extensions, g_number_of_errors, g_severity
    """Print a single issue in a readable format with the full file path."""

    file_name = issue['file']
    full_file_path = common_utils.fix_path(file_name, path_to_source_folder)

    # register file name
    update_frequency_table(full_file_path, g_files_dict)

    g_number_of_errors += 1

    file_extension = os.path.splitext(full_file_path)[1]
    update_frequency_table(file_extension, g_extensions)

    sharing_path = common_utils.get_sharing_path(full_file_path)
    title = common_utils.extract_from_file("Title:", os.path.join(sharing_path, common_utils.SHARING_INFO_FILE))
    url = common_utils.extract_from_file("Url:", os.path.join(sharing_path, common_utils.SHARING_INFO_FILE))

    severity = issue['severity']
    update_frequency_table(severity, g_severity)

    print(f"Title: {title}", file=output_file)
    print(f"Url: {url}", file=output_file)
    print(f"Line: {issue['line']}", file=output_file)
    print(f"File: {full_file_path}", file=output_file)
    print(f"Severity: {severity}", file=output_file)
    print(f"Text: {issue['text']}", file=output_file)
    print(f"Type: {issue['type']}", file=output_file)
    print(f"Sharing: {issue['sharing']}", file=output_file)
    print(f"Sharing path: {sharing_path}", file=output_file)

    # Print source code, handling Unicode characters correctly
    source_code = issue.get('source_code', '')
    print(f"Source Code: {source_code}", file=output_file)

    update_frequency_table(issue['type'], g_error_types)
    
    print("\n" + "-"*50 + "\n", file=output_file)


def print_unique_files(files, output_file=sys.stdout):
    for file_name in files:
        print(f"\n{file_name}", file=output_file)

def print_report(files, total_files, args, output_file=sys.stdout):
    # print report
    print_frequency_table("Issues types", g_error_types, output_file)
    print("", file=output_file)
    print_frequency_table("Issue severity", g_severity, output_file)
    print("", file=output_file)
    print_frequency_table("Programming languages", g_extensions, output_file)
    print("", file=output_file)

    print(f"Number of groups: {g_number_of_groups}", file=output_file)
    print(f"Number of issues: {g_number_of_errors}", file=output_file)

    print(f"Number of files where issues found: {len(g_files_dict)}", file=output_file)
    print(f"Total number of files : {total_files}", file=output_file)
    print(f"Percent of files affected: {(len(g_files_dict)*100/total_files):.2f}", file=output_file)

    if args.filter is not None:
        print(f"Group field filter: {args.filter}")

    print(f"\nUnique files: ", file=output_file)

    print_unique_files(files, output_file)

def main():

    parser = argparse.ArgumentParser(description="Print issues report grouped by field.")

    # Positional arguments
    parser.add_argument('input_json_file', help="Input json simplified report file")
    parser.add_argument('group_field', help="Grouping field")

    # Optional argument to handle file extensions
    parser.add_argument('--filter', required=False, help="Filter for grouping field")

    args = parser.parse_args()

    # Load JSON data
    data = load_json(args.input_json_file)

    # Get pathToSourceFolder and issues from the JSON data
    path_to_source_folder = data.get("pathToSourceFolder", "")

    extensions = data.get("files", "")
    file_paths = common_utils.scan_for_files(path_to_source_folder, extensions)

    issues = data.get("issues", [])

    if args.filter is not None:
        filtered_issues = []
        for issue in issues:
            if args.filter in issue['file']:
                filtered_issues.append(issue)

        issues = filtered_issues

    # Group issues by the specified field
    grouped_issues = group_issues_by_field(issues, args.group_field)

    # Check if output is being redirected to a file
    if sys.stdout.isatty():
        # Output to console (standard behavior)
        print_grouped_issues(grouped_issues, args.group_field, path_to_source_folder)
    else:
        # Output is redirected (e.g., to a file), force UTF-8 encoding
        with open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False) as output_file:
            print_grouped_issues(grouped_issues, args.group_field, path_to_source_folder, output_file)

    # now check how many files were actually with errors.
    total_files = 0
    for k, v in file_paths.items():
        total_files += len(v)

    # Check if output is being redirected to a file
    if sys.stdout.isatty():
        # Output to console (standard behavior)
        print_report(g_files_dict, total_files, args)
    else:
        # Output is redirected (e.g., to a file), force UTF-8 encoding
        with open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False) as output_file:
            print_report(g_files_dict, total_files, args, output_file)

if __name__ == "__main__":
    main()
