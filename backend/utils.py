import os

def read_file_content(file_path):
    """
    Reads content from .txt, .md, or .yaml files.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    _, ext = os.path.splitext(file_path)
    if ext.lower() not in ['.txt', '.md', '.yaml', '.yml']:
        raise ValueError("Unsupported file format. Please provide .txt, .md, or .yaml files.")

    try:
        with open(file_path, 'r', encoding='utf-8') as fr:
            return fr.read()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")
