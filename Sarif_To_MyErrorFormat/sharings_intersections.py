import os
import json
import sys
from collections import defaultdict
import common_utils

def load_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data = {}
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data[file_path] = json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file_path}", file=sys.stderr)
    return data

def extract_sharing_info(issue_file_path):
    # Split the file path into folders
    path_parts = issue_file_path.replace("\\", "/").split("/")

    # Find the index of the "Sharing_" segment
    sharing_index = next((i for i, part in enumerate(path_parts) if part.startswith("Sharing_")), None)

    if sharing_index is None or sharing_index < 2:
        return None, None

    # Extract the sharing name and the two previous folder names
    sharing_name = path_parts[sharing_index]
    preceding_folders = "/".join(path_parts[sharing_index - 2:sharing_index])

    return sharing_name, preceding_folders

def extract_extended_sharing(issue_file_path):
    # Split the file path into folders
    path_parts = issue_file_path.replace("\\", "/").split("/")

    # Find the index of the "Sharing_" segment
    sharing_index = next((i for i, part in enumerate(path_parts) if part.startswith("Sharing_")), None)

    if sharing_index is None:
        return None

    # Extract the path starting from "Sharing_" onward
    extended_sharing_path = "/".join(path_parts[sharing_index-2:])
    return extended_sharing_path

def find_sharing_intersections(json_data, full_path_mode=False, line_numbers_mode=False):
    sharing_map = defaultdict(set)  # Use a set to track unique files for each extended sharing

    # Iterate over all loaded JSON data
    for file_path, content in json_data.items():
        issues = content.get('issues', [])
        for issue in issues:
            if full_path_mode:
                # Compare the entire path starting from "extended sharing"
                extended_sharing = extract_extended_sharing(issue['file'])
                if extended_sharing:
                    key = (extended_sharing, issue['line']) if line_numbers_mode else extended_sharing
                    sharing_map[key].add(file_path)
            else:
                # Compare only the sharing name and preceding folders
                sharing_name, preceding_folders = extract_sharing_info(issue['file'])
                if sharing_name and preceding_folders:
                    key = ((sharing_name, preceding_folders), issue['line']) if line_numbers_mode else (sharing_name, preceding_folders)
                    sharing_map[key].add(file_path)

    # Find sharings that appear in more than one different file
    intersections = {sharing: list(file_paths) for sharing, file_paths in sharing_map.items() if len(file_paths) > 1}
    
    return intersections

def get_issue_details(sharing, file_path, json_data, full_path_mode=False, line_numbers_mode=False):
    details = []
    issues = json_data[file_path]['issues']

    path_to_source_folder = json_data[file_path]['pathToSourceFolder']

    for issue in issues:

        # get issue sharing
        file_name = issue['file']
        full_file_path = common_utils.fix_path(file_name, path_to_source_folder)

        sharing_path = common_utils.get_sharing_path(full_file_path)
        title = common_utils.extract_from_file("Title:", os.path.join(sharing_path, common_utils.SHARING_INFO_FILE))
        url = common_utils.extract_from_file("Url:", os.path.join(sharing_path, common_utils.SHARING_INFO_FILE))


        if full_path_mode:
            extended_sharing = extract_extended_sharing(issue['file'])
            if line_numbers_mode:
                key = (extended_sharing, issue['line'])
            else:
                key = extended_sharing
            if sharing == key:
                detail = (
                    f"Title: {title}\n"
                    f"Url: {url}\n"
                    f"Line: {issue['line']}, Severity: {issue['severity']}, Type: {issue['type']}\n"
                    f"Text: {issue['text']}\n"
                    f"File Path: {issue['file']}\n"
                    f"Full Path: {full_file_path}\n"
                    f"Source code: {issue['source_code']}\n"
                    f"{'-' * 40}"
                )
                details.append(detail)
        else:
            sharing_name, preceding_folders = extract_sharing_info(issue['file'])
            if line_numbers_mode:
                key = ((sharing_name, preceding_folders), issue['line'])
            else:
                key = (sharing_name, preceding_folders)
            if sharing == key:
                detail = (
                    f"Title: {title}\n"
                    f"Url: {url}\n"
                    f"Line: {issue['line']}, Severity: {issue['severity']}, Type: {issue['type']}\n"
                    f"Text: {issue['text']}\n"
                    f"File Path: {issue['file']}\n"
                    f"Full Path: {full_file_path}\n"
                    f"Source code: {issue['source_code']}\n"
                    f"{'-' * 40}"
                )
                details.append(detail)
    return "\n".join(details)

def write_intersections_to_file(intersections, json_data, output_file, full_path_mode=False, line_numbers_mode=False):
    with open(output_file, 'w', encoding='utf-8') as f:
        if not intersections:
            f.write("No sharing intersections found.\n")
            return

        intersection_count = 0
        for sharing, file_paths in intersections.items():
            intersection_count += 1
            f.write(f"\n{'=' * 20} INTERSECTION {intersection_count} {'=' * 20}\n")
            if full_path_mode:
                sharing_info = sharing[0] if line_numbers_mode else sharing
                f.write(f"Extended sharing path intersection found: {sharing_info}\n")
            else:
                sharing_info = sharing[0] if line_numbers_mode else sharing
                sharing_name, preceding_folders = sharing_info
                f.write(f"Sharing intersection found: {sharing_name}\n")
                f.write(f"Preceding folders: {preceding_folders}\n")
            
            if line_numbers_mode:
                f.write(f"Line number: {sharing[1]}\n")
            f.write(f"{'-' * 50}\n")
            
            for file_path in file_paths:
                f.write(f"\nFile: {file_path}\n")
                f.write(f"{'-' * 40}\n")
                issue_details = get_issue_details(sharing, file_path, json_data, full_path_mode, line_numbers_mode)
                f.write(f"{issue_details}\n")
            f.write(f"\n{'=' * 50}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sharing_intersections.py <folder_path> <output_file> [--full-path] [--line-numbers]")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_file = sys.argv[2]
    full_path_mode = '--full-path' in sys.argv
    line_numbers_mode = '--line-numbers' in sys.argv

    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    json_data = load_json_files(folder_path)
    intersections = find_sharing_intersections(json_data, full_path_mode, line_numbers_mode)
    write_intersections_to_file(intersections, json_data, output_file, full_path_mode, line_numbers_mode)
    print(f"Intersections have been written to '{output_file}'.")
