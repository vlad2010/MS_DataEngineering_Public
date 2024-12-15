import os
import sys

def delete_files(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    
    # Iterate through files in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check file extension and if the name doesn't start with "New_generated"
            if file.endswith(('.c', '.cs', '.cpp')) and not file.startswith("New_generated"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python delete_files.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    delete_files(folder_path)



