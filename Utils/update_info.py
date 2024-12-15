import os
import json

# Load the JSON file
def load_json(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

# Append issue to the specific info.txt file
def append_issue_to_info(issue, folder_path):
    info_file_path = os.path.join(folder_path, 'info.txt')
    try:
        with open(info_file_path, 'a') as file:
            file.write("\n\nDetect info from scanners: \n")
            # Convert issue back to JSON string and append to file
            json.dump(issue, file, indent=4)
            file.write("\n")
        print(f"Issue appended to {info_file_path}")
    except Exception as e:
        print(f"Error writing to {info_file_path}: {e}")

# Main function to iterate over folders and append issues
def main(json_file, base_folder_path):
    # Load all issues from the JSON
    data = load_json(json_file)
    if not data:
        return
    issues = data.get('issues', [])
    
    # Iterate over folders Issue_01 to Issue_64
    for i in range(1, 65):
        folder_name = f"Issue_{i:02d}"  # Format folder name as Issue_01, Issue_02, etc.
        folder_path = os.path.join(base_folder_path, folder_name)
        
        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(f"Folder {folder_path} does not exist, skipping...")
            continue
        
        # Check if there's a corresponding issue in the JSON data
        if i-1 < len(issues):
            issue_list = issues[i-1]  # Assuming issues are ordered from Issue_01 to Issue_64
            for issue in issue_list:
                # Append each issue to the folder's info.txt
                append_issue_to_info(issue, folder_path)
        else:
            print(f"No issue found for {folder_name}, skipping...")

if __name__ == "__main__":
    # Replace with your JSON file path and base folder path
    json_file = "Output_report.json"
    base_folder_path = "."
    
    main(json_file, base_folder_path)
