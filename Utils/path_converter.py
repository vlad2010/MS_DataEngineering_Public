import os

def convert_to_windows_path(path):
    # Convert forward slashes to backslashes
    windows_path = path.replace('/', '\\')
    # Optional: resolve to an absolute path
   
    absolute_path = os.path.join("d:\\GitHub\\MS_DataEngineering\\Dissertation\\Utils\\cpp_csharp\\Code", windows_path)
   
    return absolute_path

# Example usage
if __name__ == "__main__":
    input_path = input("Enter the file path to convert: ")
    windows_formatted_path = convert_to_windows_path(input_path)
    print(f"Windows formatted path: {windows_formatted_path}")


