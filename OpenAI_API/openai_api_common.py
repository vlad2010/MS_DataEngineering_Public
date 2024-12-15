
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content