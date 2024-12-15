#!/usr/bin/env python3

import json
import sys
import os

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_path(path):
    """Remove '/./' subpaths from a given path."""
    while '/./' in path:
        path = path.replace('/./', '/')
    return path

def extract_unique_file_paths(json_files):
    """Extract unique file paths by combining pathToSourceFolder and issue file paths."""
    unique_files = set()
    
    for file_path in json_files:
        try:
            data = load_json(file_path)
            source_folder = data.get("pathToSourceFolder", "")
            
            for issue in data.get("issues", []):
                file_name = issue.get("file", "")
                full_path = os.path.join(source_folder, file_name)
                clean_full_path = clean_path(full_path)
                unique_files.add(clean_full_path)
        except:
            print(f"Can't open file: {file_path}")
    
    # Sort the unique files alphabetically
    return sorted(unique_files)

def get_stats(unique_files):
    # s = { 'c':0, 'cpp':0, 'cs':0 }
    s = {}

    for file in unique_files:
        _, ext = os.path.splitext(file)

        # print(f"Ext is : {ext}")
        if ext in s:
            s[ext] = s[ext] + 1
        else:
            s[ext] = 1

    return s

def save_unique_files_to_json(unique_files, output_file, info_file):
    """Save unique file paths to a JSON file, creating the file if it does not exist."""
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    output_data = {"unique_files": unique_files}
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

    st = get_stats(unique_files)
    info_data = f"Number of unique files: {len(unique_files)}\n"

    for lang, lnum in st.items():
        print(f"[{lang}] - [{lnum}]")
        info_data = info_data + f"[{lang}] - [{lnum}]\n"

    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_data)

def main():
    if len(sys.argv) < 4:
        print("Usage: python script.py <output_file> <info_file> <json_file1> <json_file2> ...")
        sys.exit(1)
    
    output_file = sys.argv[1]
    info_file = sys.argv[2]
    json_files = sys.argv[3:]
    unique_files = extract_unique_file_paths(json_files)
    
    # Print the number of unique files and save the list to the specified output JSON file
    print(f"Number of unique files: {len(unique_files)}")
    save_unique_files_to_json(unique_files, output_file, info_file)

if __name__ == "__main__":
    main()
