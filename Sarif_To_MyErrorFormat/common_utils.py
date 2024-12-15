import re
import os
from pathlib import Path, PureWindowsPath, PurePosixPath

SHARING_INFO_FILE = "sharing_info.txt"

def extract_from_file(string_start, file_path):
    try:
        # Open the file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith(string_start):
                    # Extract the title by removing the "Title:" part and stripping any extra whitespace
                    return line.split(string_start, 1)[1].strip()
        return "Title not found"
    except UnicodeDecodeError:
        return "Unicode decoding error: Unable to read file with UTF-8 encoding"
    except FileNotFoundError:
        return f"File {file_path} not found"


def fix_path(file_name, path_to_source_folder):

    return os.path.join(path_to_source_folder, file_name)

    # match = re.match(r"^/mnt/([a-zA-Z])/", file_name)
    # if match:
    #     full_file_path = fix_unix_full_path(file_name, match)
    # else:
    #     # Combine pathToSourceFolder and the file field using Windows-style delimiters
    #     full_file_path = os.path.join(path_to_source_folder, file_name).replace('/', '\\')
    #
    # return full_file_path

def fix_unix_full_path(path, match):

    # drive_letter = match.group(1).lower() + ":\\"
    drive_letter = match.group(1).lower() + ":\\\\"
    new_path = re.sub(r"^/mnt/[a-zA-Z]/", drive_letter, path)
    # Replace all remaining forward slashes with backslashes
    new_path = new_path.replace("/", "\\")
    return new_path

def get_sharing_path(full_path):
    # Detect and convert the path based on Windows or WSL style
    if '\\' in full_path:
        # Likely a Windows path
        path_obj = PureWindowsPath(full_path)
    else:
        # Likely a WSL or POSIX path
        path_obj = PurePosixPath(full_path)

    # Loop through the parts of the path to find the one that starts with "Sharing_"
    for i, part in enumerate(path_obj.parts):
        if part.startswith("Sharing_"):
            # Construct the subpath up to and including the "Sharing_" folder
            subpath = Path(*path_obj.parts[:i+1])
            return subpath

    # Return None if no "Sharing_" folder is found
    print("No 'Sharing_' folder found in the path.")
    return None

        
def scan_for_files(folder_path, extensions):
    # Create a dictionary to store file lists for each extension
    files_by_extension = {ext: [] for ext in extensions}
    
    # Walk through the folder tree
    for root, _, files in os.walk(folder_path):
        for file in files:
            # Get the file extension
            file_ext = os.path.splitext(file)[1].lstrip('.').lower()
            full_path = os.path.join(root, file)
            
            # Check if the extension is in the required list and append accordingly
            if file_ext in extensions:
                files_by_extension[file_ext].append(full_path)
    
    # Return the dictionary containing the lists of files for each extension
    return files_by_extension